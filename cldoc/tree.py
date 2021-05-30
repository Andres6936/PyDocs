# This file is part of cldoc.  cldoc is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -*- coding: utf-8 -*-

import os
import platform
import sys
from ctypes.util import find_library
from tempfile import NamedTemporaryFile
from typing import List, Callable, Optional, Tuple

import documentmerger
import example
from files import includepaths
import nodes

from clang.config import Config
from clang.exceptions.lib_clang import LibclangError
from clang.kinds.cursor_kind import CursorKind
from clang.objects.index import Index
from clang.objects.translation_unit import TranslationUnit
from clang.utility.diagnostic import Diagnostic
from clang.utility.token_kind import TokenKind
from util.defdict import Defdict
from comment import Comment
from comments.comments_database import CommentsDatabase
from files.provider_source import ProviderSource
from nodes import Root

if platform.system() == 'Darwin':
    libclangs = [
        '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib',
        '/Library/Developer/CommandLineTools/usr/lib/libclang.dylib'
    ]

    found = False

    for libclang in libclangs:
        if os.path.exists(libclang):
            Config.set_library_path(os.path.dirname(libclang))
            found = True
            break

    if not found:
        lname = find_library("clang")

        if not lname is None:
            Config.set_library_file(lname)
else:
    versions = [None, '7.0', '6.0', '5.0', '4.0', '3.9', '3.8', '3.7', '3.6', '3.5', '3.4', '3.3', '3.2']

    for v in versions:
        name = 'clang'

        if not v is None:
            name += '-' + v

        lname = find_library(name)

        if not lname is None:
            Config.set_library_file(lname)
            break

testconf = Config()

try:
    testconf.get_cindex_library()
except LibclangError as e:
    sys.stderr.write(
        "\nFatal: Failed to locate libclang library. cldoc depends on libclang for parsing sources, please make sure you have libclang installed.\n" + str(
            e) + "\n\n")
    sys.exit(1)


class Tree(documentmerger.DocumentMerger):
    def __init__(self, provider_source: ProviderSource, flags: str):
        super().__init__()
        self.headers = {}
        self.processed = {}
        self.index = Index.create()
        self.flags = includepaths.flags(flags)
        self.provider_source: ProviderSource = provider_source
        self.processing = {}
        self.kindmap = {}

        # Things to skip
        self.kindmap[CursorKind.USING_DIRECTIVE] = None

        # Create a map from CursorKind to classes representing those cursor
        # kinds.
        for cls in nodes.Node.subclasses():
            if hasattr(cls, 'kind'):
                self.kindmap[cls.kind] = cls

        self.root: Root = Root()

        self.all_nodes = []
        self.cursor_to_node = Defdict()
        self.usr_to_node = Defdict()
        self.qid_to_node = Defdict()

        # Map from category name to the nodes.Category for that category
        self.category_to_node = Defdict()

        # Map from filename to comment.CommentsDatabase
        self.commentsdbs = Defdict()

        self.qid_to_node[None] = self.root
        self.usr_to_node[None] = self.root

    def _lookup_node_from_cursor_despecialized(self, cursor):
        template = cursor.specialized_cursor_template

        if template is None:
            parent = self.lookup_node_from_cursor(cursor.semantic_parent)
        else:
            return self.lookup_node_from_cursor(template)

        if parent is None:
            return None

        for child in parent.children:
            if child.name == cursor.spelling:
                return child

        return None

    def lookup_node_from_cursor(self, cursor):
        if cursor is None:
            return None

        # Try lookup by direct cursor reference
        node = self.cursor_to_node[cursor]

        if not node is None:
            return node

        node = self.usr_to_node[cursor.get_usr()]

        if not node is None:
            return node

        return self._lookup_node_from_cursor_despecialized(cursor)

    @staticmethod
    def filter_source(path: str) -> bool:
        """
        :param path: The path to source file.
        :return: True if the file is of type C++ (source or header).
         For determine it, the extension of file is revised and if it
         is .c or .cpp or .cc for the source and .h or .hh or .hpp for
         the header return True, this method return False otherwise.
        """
        return path.endswith('.c') or path.endswith('.cpp') or path.endswith('.h') or \
               path.endswith('.cc') or path.endswith('.hh') or path.endswith('.hpp')

    def expand_sources(self, sources: List[str], filter: Optional[Callable[[str], bool]] = None) \
            -> Tuple[List[str], bool]:
        """
        :param sources: List with the paths to sources files, if the path
         is a directory, the content of this directory will be returned.
        :param filter: The callback that will be used for filter final
         files of list of sources, if the callback return True, the path
         to file that is passed to callback will be included in the final list.
        :return: Tuple, the first value content the list of path to sources
         files and the second value determine if the operation is successful.
        """
        ret: List[str] = []
        successful: bool = True

        for source in sources:
            if filter is not None and not filter(source):
                continue

            if os.path.isdir(source):
                retdir, okdir = self.expand_sources([os.path.join(source, x) for x in os.listdir(source)],
                                                    self.filter_source)

                if not okdir:
                    successful = False

                ret += retdir
            elif not os.path.exists(source):
                sys.stderr.write("The specified source `" + source + "` could not be found\n")
                successful = False
            else:
                ret.append(source)

        return ret, successful

    def is_header(self, filename):
        return filename.endswith('.hh') or filename.endswith('.hpp') or filename.endswith('.h')

    def find_node_comment(self, node):
        for location in node.comment_locations:
            db = self.commentsdbs[location.file.name]

            if db:
                cm = db.lookup(location)

                if cm:
                    return cm

        return None

    def process(self):
        """
        process processes all the files with clang and extracts all relevant
        nodes from the generated AST
        """
        self.logger.informational("Starting processing with CLang")

        for f in self.provider_source:
            self.logger.informational("Processing the file: {}".format(os.path.basename(f)))
            if f in self.processed:
                self.logger.informational("The file '{}' has already been processed".format(os.path.basename(f)))

            translation_unit: TranslationUnit = self.index.parse(f, self.flags)

            if len(translation_unit.diagnostics) != 0:
                self.logger.warning("Found {} diagnostics for the file: {}".format(
                    len(translation_unit.diagnostics), os.path.basename(f)))
                fatal = False

                for d in translation_unit.diagnostics:
                    if d.severity == Diagnostic.Fatal or d.severity == Diagnostic.Error:
                        fatal = True
                        self.logger.critical(d.format())
                    else:
                        self.logger.warning(d.format())

                if fatal:
                    self.logger.critical("Could not generate documentation due to parser errors")
                    sys.exit(1)

            if not translation_unit:
                self.logger.critical("Could not parse file {}...".format(os.path.basename(f)))
                sys.exit(1)

            # Extract comments from files and included files that we are
            # supposed to inspect
            extractfiles: List[str] = [f]

            for inc in translation_unit.get_includes():
                filename = str(inc.include)
                self.headers[filename] = True

                if filename in self.processed or (not filename in self.provider_source) or filename in extractfiles:
                    continue

                extractfiles.append(filename)

            for extracted in extractfiles:
                db = CommentsDatabase(extracted, translation_unit)

                self.add_categories(db.category_names)
                self.commentsdbs[extracted] = db

            self.visit(translation_unit.cursor.get_children())

            for f in self.processing:
                self.processed[f] = True

            self.processing = {}

        # Construct hierarchy of nodes.
        for node in self.all_nodes:
            q = node.qid

            if node.parent is None:
                par = self.find_parent(node)

                # Lookup categories for things in the root
                if (par is None or par == self.root) and (not node.cursor is None):
                    location = node.cursor.extent.start
                    db = self.commentsdbs[location.file.name]

                    if db:
                        par = self.category_to_node[db.lookup_category(location)]

                if par is None:
                    par = self.root

                par.append(node)

            # Resolve comment
            cm = self.find_node_comment(node)

            if cm:
                node.merge_comment(cm)

        # Keep track of classes to resolve bases and subclasses
        classes = {}

        # Map final qid to node
        for node in self.all_nodes:
            q = node.qid
            self.qid_to_node[q] = node

            if isinstance(node, nodes.Class):
                classes[q] = node

        # Resolve bases and subclasses
        for qid in classes:
            classes[qid].resolve_bases(classes)

    def markup_code(self, index):
        for node in self.all_nodes:
            if node.comment is None:
                continue

            if not node.comment.doc:
                continue

            comps = node.comment.doc.components

            for i in range(len(comps)):
                component = comps[i]

                if not isinstance(component, Comment.Example):
                    continue

                text = str(component)

                tmpfile = NamedTemporaryFile(delete=False)
                tmpfile.write(text)
                filename = tmpfile.name
                tmpfile.close()

                tu = index.parse(filename, self.flags, options=1)
                tokens = tu.get_tokens(extent=tu.get_extent(filename, (0, os.stat(filename).st_size)))
                os.unlink(filename)

                hl = []
                incstart = None

                for token in tokens:
                    start = token.extent.start.offset
                    end = token.extent.end.offset

                    if token.kind == TokenKind.KEYWORD:
                        hl.append((start, end, 'keyword'))
                        continue
                    elif token.kind == TokenKind.COMMENT:
                        hl.append((start, end, 'comment'))

                    cursor = token.cursor

                    if cursor.kind == CursorKind.PREPROCESSING_DIRECTIVE:
                        hl.append((start, end, 'preprocessor'))
                    elif cursor.kind == CursorKind.INCLUSION_DIRECTIVE and incstart is None:
                        incstart = cursor
                    elif (not incstart is None) and \
                            token.kind == TokenKind.PUNCTUATION and \
                            token.spelling == '>':
                        hl.append((incstart.extent.start.offset, end, 'preprocessor'))
                        incstart = None

                ex = example.Example()
                lastpos = 0

                for ih in range(len(hl)):
                    h = hl[ih]

                    ex.append(text[lastpos:h[0]])
                    ex.append(text[h[0]:h[1]], h[2])

                    lastpos = h[1]

                ex.append(text[lastpos:])
                comps[i] = ex

    def match_ref(self, child, name):
        if isinstance(name, str):
            return name == child.name
        else:
            return name.match(child.name)

    def find_ref(self, node, name, goup):
        if node is None:
            return []

        ret = []

        for child in node.resolve_nodes:
            if self.match_ref(child, name):
                ret.append(child)

        if goup and len(ret) == 0:
            return self.find_ref(node.parent, name, True)
        else:
            return ret

    def cross_ref_node(self, node):
        if not node.comment is None:
            node.comment.resolve_refs(self.find_ref, node)

        for child in node.children:
            self.cross_ref_node(child)

    def cross_ref(self):
        self.cross_ref_node(self.root)
        self.markup_code(self.index)

    def decl_on_c_struct(self, node, tp):
        n = self.cursor_to_node[tp.decl]

        if isinstance(n, nodes.Struct) or \
                isinstance(n, nodes.Typedef) or \
                isinstance(n, nodes.Enum):
            return n

        return None

    def c_function_is_constructor(self, node):
        hints = ['new', 'init', 'alloc', 'create']

        for hint in hints:
            if node.name.startswith(hint + "_") or \
                    node.name.endswith("_" + hint):
                return True

        return False

    def node_on_c_struct(self, node):
        if isinstance(node, nodes.Method) or \
                not isinstance(node, nodes.Function):
            return None

        decl = None

        if self.c_function_is_constructor(node):
            decl = self.decl_on_c_struct(node, node.return_type)

        if not decl:
            args = node.arguments

            if len(args) > 0:
                decl = self.decl_on_c_struct(node, args[0].type)

        return decl

    def find_parent(self, node):
        cursor = node.cursor

        # If node is a C function, then see if we should group it to a struct
        parent = self.node_on_c_struct(node)

        if parent:
            return parent

        while cursor:
            cursor = cursor.semantic_parent
            parent = self.cursor_to_node[cursor]

            if parent:
                return parent

        return self.root

    def register_node(self, node, parent=None):
        self.all_nodes.append(node)

        self.usr_to_node[node.cursor.get_usr()] = node
        self.cursor_to_node[node.cursor] = node

        # Typedefs in clang are not parents of typedefs, but we like it better
        # that way, explicitly set the parent directly here
        if parent and isinstance(parent, nodes.Typedef):
            parent.append(node)

        if parent and hasattr(parent, 'current_access'):
            node.access = parent.current_access

    def register_anon_typedef(self, node, parent):
        node.typedef = parent
        node.add_comment_location(parent.cursor.extent.start)

        self.all_nodes.remove(parent)

        # Map references to the typedef directly to the node
        self.usr_to_node[parent.cursor.get_usr()] = node
        self.cursor_to_node[parent.cursor] = node

    def cursor_is_exposed(self, cursor):
        # Only cursors which are in headers are exposed.
        filename = str(cursor.location.file)
        return filename in self.headers or self.is_header(filename)

    def is_unique_anon_struct(self, node, parent):
        if not node:
            return False

        if not isinstance(node, nodes.Struct):
            return False

        if not (node.is_anonymous or not node.name):
            return False

        return not isinstance(parent, nodes.Typedef)

    def visit(self, citer, parent=None):
        """
        visit iterates over the provided cursor iterator and creates nodes
        from the AST cursors.
        """
        if not citer:
            return

        while True:
            try:
                item = next(citer)
            except StopIteration:
                return

            # Check the source of item
            if not item.location.file:
                self.visit(item.get_children())
                continue

            # Ignore files we already processed
            if str(item.location.file) in self.processed:
                continue

            # Ignore files other than the ones we are scanning for
            if not str(item.location.file) in self.provider_source:
                continue

            # Ignore unexposed things
            if item.kind == CursorKind.UNEXPOSED_DECL:
                self.visit(item.get_children(), parent)
                continue

            self.processing[str(item.location.file)] = True

            if item.kind in self.kindmap:
                cls = self.kindmap[item.kind]

                if not cls:
                    # Skip
                    continue

                # see if we already have a node for this thing
                node = self.usr_to_node[item.get_usr()]

                if not node or self.is_unique_anon_struct(node, parent):
                    # Only register new nodes if they are exposed.
                    if self.cursor_is_exposed(item):
                        node = cls(item, None)
                        self.register_node(node, parent)

                elif isinstance(parent, nodes.Typedef) and isinstance(node, nodes.Struct):
                    # Typedefs are handled a bit specially because what happens
                    # is that clang first exposes an unnamed struct/enum, and
                    # then exposes the typedef, with as a child again the
                    # cursor to the already defined struct/enum. This is a
                    # bit reversed as to how we normally process things.
                    self.register_anon_typedef(node, parent)
                else:
                    self.cursor_to_node[item] = node
                    node.add_ref(item)

                if node and node.process_children:
                    self.visit(item.get_children(), node)
            else:
                par = self.cursor_to_node[item.semantic_parent]

                if not par:
                    par = parent

                if par:
                    ret = par.visit(item, citer)

                    if not ret is None:
                        for node in ret:
                            self.register_node(node, par)

                ignoretop = [CursorKind.TYPE_REF, CursorKind.PARM_DECL]

                if (not par or ret is None) and not item.kind in ignoretop:
                    self.logger.warning("Unhandled cursor: {}".format(item.kind))

# vi:ts=4:et
