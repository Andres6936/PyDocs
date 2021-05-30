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
# ===- cindex.py - Python Indexing Library Bindings -----------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# ===------------------------------------------------------------------------===#

r"""
Clang Indexing Library Bindings
===============================

This module provides an interface to the Clang indexing library. It is a
low-level interface to the indexing library which attempts to match the Clang
API directly while also being "pythonic". Notable differences from the C API
are:

 * string results are returned as Python strings, not CXString objects.

 * null cursors are translated to None.

 * access to child cursors is done via iteration, not visitation.

The major indexing objects are:

  Index

    The top-level object which manages some global library state.

  TranslationUnit

    High-level object encapsulating the AST for a single translation unit. These
    can be loaded from cldoc.ast files or parsed on the fly.

  Cursor

    Generic object for representing a node in the AST.

  SourceRange, SourceLocation, and File

    Objects representing information about the input source.

Most object information is exposed using properties, when the underlying API
call is efficient.
"""

# TODO
# ====
#
# o API support for invalid translation units. Currently we can't even get the
#   diagnostics on failure because they refer to locations in an object that
#   will have been invalidated.
#
# o fix memory management issues (currently client must hold on to index and
#   translation unit, or risk crashes).
#
# o expose code completion APIs.
#
# o cleanup ctypes wrapping, would be nice to separate the ctypes details more
#   clearly, and hide from the external interface (i.e., help(cindex)).
#
# o implement additional SourceLocation, SourceRange, and File methods.
import os.path
from ctypes import *

from clang.config import conf
from clang.cursor import Cursor
from clang.decorators.cached_property import CachedProperty
from clang.exceptions.compilation_database import CompilationDatabaseError
from clang.exceptions.lib_clang import LibclangError
from clang.exceptions.translation_unit import TranslationUnitLoadError
from clang.kinds.availability_kind import AvailabilityKind
from clang.kinds.cursor_kind import CursorKind
from clang.kinds.linkage_kind import LinkageKind
from clang.kinds.tls_kind import TLSKind
from clang.kinds.type_kind import TypeKind
from clang.objects.code_completion_results import CodeCompletionResults
from clang.objects.completion_string import CompletionString
from clang.objects.translation_unit import TranslationUnit
from clang.prototypes.functions import c_object_p, callbacks, functionList
from clang.spelling_cache import SpellingCache
from clang.token import Token
from clang.token_kinds import TokenKinds
from clang.type import Type
from clang.utility.diagnostic import Diagnostic
from clang.utility.fix_it import FixIt
from clang.utility.source_location import SourceLocation
from clang.utility.token_kind import TokenKind


### Structures and Utility Classes ###


class SourceRange(Structure):
    """
    A SourceRange describes a range of source locations within the source
    code.
    """
    _fields_ = [
        ("ptr_data", c_void_p * 2),
        ("begin_int_data", c_uint),
        ("end_int_data", c_uint)]

    # FIXME: Eliminate this and make normal constructor? Requires hiding ctypes
    # object.
    @staticmethod
    def from_locations(start: SourceLocation, end: SourceLocation):
        return conf.lib.clang_getRange(start, end)

    @property
    def start(self):
        """
        Return a SourceLocation representing the first character within a
        source range.
        """
        return conf.lib.clang_getRangeStart(self)

    @property
    def end(self):
        """
        Return a SourceLocation representing the last character within a
        source range.
        """
        return conf.lib.clang_getRangeEnd(self)

    def __eq__(self, other):
        return conf.lib.clang_equalRanges(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, other):
        """Useful to detect the Token/Lexer bug"""
        if not isinstance(other, SourceLocation):
            return False
        if other.file is None and self.start.file is None:
            pass
        elif (self.start.file.name != other.file.name or
              other.file.name != self.end.file.name):
            # same file name
            return False
        # same file, in between lines
        if self.start.line < other.line < self.end.line:
            return True
        elif self.start.line == other.line:
            # same file first line
            if self.start.column <= other.column:
                return True
        elif other.line == self.end.line:
            # same file last line
            if other.column <= self.end.column:
                return True
        return False

    def __repr__(self):
        return "<SourceRange start %r, end %r>" % (self.start, self.end)

## CIndex Objects ##

# CIndex objects (derived from ClangObject) are essentially lightweight
# wrappers attached to some underlying object, which is exposed via CIndex as
# a void*.

class ClangObject(object):
    """
    A helper for Clang objects. This class helps act as an intermediary for
    the ctypes library and the Clang CIndex library.
    """

    def __init__(self, obj):
        assert isinstance(obj, c_object_p) and obj
        self.obj = self._as_parameter_ = obj

    def from_param(self):
        return self._as_parameter_


class _CXUnsavedFile(Structure):
    """Helper for passing unsaved file arguments."""
    _fields_ = [("name", c_char_p), ("contents", c_char_p), ('length', c_ulong)]


class CompletionChunk:
    class Kind:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

        def __repr__(self):
            return "<ChunkKind: %s>" % self

    def __init__(self, completionString, key):
        self.cs = completionString
        self.key = key
        self.__kindNumberCache = -1

    def __repr__(self):
        return "{'" + self.spelling + "', " + str(self.kind) + "}"

    @CachedProperty
    def spelling(self):
        if self.__kindNumber in SpellingCache:
            return SpellingCache[self.__kindNumber]
        return conf.lib.clang_getCompletionChunkText(self.cs, self.key)

    # We do not use @CachedProperty here, as the manual implementation is
    # apparently still significantly faster. Please profile carefully if you
    # would like to add CachedProperty back.
    @property
    def __kindNumber(self):
        if self.__kindNumberCache == -1:
            self.__kindNumberCache = \
                conf.lib.clang_getCompletionChunkKind(self.cs, self.key)
        return self.__kindNumberCache

    @CachedProperty
    def kind(self):
        return completionChunkKindMap[self.__kindNumber]

    @CachedProperty
    def string(self):
        res = conf.lib.clang_getCompletionChunkCompletionString(self.cs,
                                                                self.key)

        if (res):
            return CompletionString(res)
        else:
            None

    def isKindOptional(self):
        return self.__kindNumber == 0

    def isKindTypedText(self):
        return self.__kindNumber == 1

    def isKindPlaceHolder(self):
        return self.__kindNumber == 3

    def isKindInformative(self):
        return self.__kindNumber == 4

    def isKindResultType(self):
        return self.__kindNumber == 15


completionChunkKindMap = {
    0: CompletionChunk.Kind("Optional"),
    1: CompletionChunk.Kind("TypedText"),
    2: CompletionChunk.Kind("Text"),
    3: CompletionChunk.Kind("Placeholder"),
    4: CompletionChunk.Kind("Informative"),
    5: CompletionChunk.Kind("CurrentParameter"),
    6: CompletionChunk.Kind("LeftParen"),
    7: CompletionChunk.Kind("RightParen"),
    8: CompletionChunk.Kind("LeftBracket"),
    9: CompletionChunk.Kind("RightBracket"),
    10: CompletionChunk.Kind("LeftBrace"),
    11: CompletionChunk.Kind("RightBrace"),
    12: CompletionChunk.Kind("LeftAngle"),
    13: CompletionChunk.Kind("RightAngle"),
    14: CompletionChunk.Kind("Comma"),
    15: CompletionChunk.Kind("ResultType"),
    16: CompletionChunk.Kind("Colon"),
    17: CompletionChunk.Kind("SemiColon"),
    18: CompletionChunk.Kind("Equal"),
    19: CompletionChunk.Kind("HorizontalSpace"),
    20: CompletionChunk.Kind("VerticalSpace")}



class Index(ClangObject):
    """
    The Index type provides the primary interface to the Clang CIndex library,
    primarily by providing an interface for reading and parsing translation
    units.
    """

    @staticmethod
    def create(excludeDecls=False):
        """
        Create a new Index.
        Parameters:
        excludeDecls -- Exclude local declarations from translation units.
        """
        return Index(conf.lib.clang_createIndex(excludeDecls, 0))

    def __del__(self):
        conf.lib.clang_disposeIndex(self)

    def read(self, path):
        """Load a TranslationUnit from the given AST file."""
        return TranslationUnit.from_ast_file(path, self)

    def parse(self, path, args=None, unsaved_files=None, options=0):
        """Load the translation unit from the given source code file by running
        clang and generating the AST before loading. Additional command line
        parameters can be passed to clang via the args parameter.

        In-memory contents for files can be provided by passing a list of pairs
        to as unsaved_files, the first item should be the filenames to be mapped
        and the second should be the contents to be substituted for the
        file. The contents may be passed as strings or file objects.

        If an error was encountered during parsing, a TranslationUnitLoadError
        will be raised.
        """
        return TranslationUnit.from_source(path, args, unsaved_files, options,
                                           self)


class File(ClangObject):
    """
    The File class represents a particular source file that is part of a
    translation unit.
    """

    @staticmethod
    def from_name(translation_unit, file_name : str):
        """Retrieve a file handle within the given translation unit."""
        return File(conf.lib.clang_getFile(translation_unit, file_name))

    @property
    def name(self):
        """Return the complete file and path name of the file."""
        return conf.lib.clang_getFileName(self)

    @property
    def time(self):
        """Return the last modification time of the file."""
        return conf.lib.clang_getFileTime(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<File: {}>".format(self.name)

    @staticmethod
    def from_cursor_result(res, fn, args):
        assert isinstance(res, File)

        # Copy a reference to the TranslationUnit to prevent premature GC.
        res._tu = args[0]._tu
        return res


class CompileCommand(object):
    """Represents the compile command used to build a file"""

    def __init__(self, cmd, ccmds):
        self.cmd = cmd
        # Keep a reference to the originating CompileCommands
        # to prevent garbage collection
        self.ccmds = ccmds

    @property
    def directory(self):
        """Get the working directory for this CompileCommand"""
        return conf.lib.clang_CompileCommand_getDirectory(self.cmd)

    @property
    def filename(self):
        """Get the working filename for this CompileCommand"""
        return conf.lib.clang_CompileCommand_getFilename(self.cmd)

    @property
    def arguments(self):
        """
        Get an iterable object providing each argument in the
        command line for the compiler invocation as a _CXString.

        Invariant : the first argument is the compiler executable
        """
        length = conf.lib.clang_CompileCommand_getNumArgs(self.cmd)
        for i in range(length):
            yield conf.lib.clang_CompileCommand_getArg(self.cmd, i)


class CompileCommands(object):
    """
    CompileCommands is an iterable object containing all CompileCommand
    that can be used for building a specific file.
    """

    def __init__(self, ccmds):
        self.ccmds = ccmds

    def __del__(self):
        conf.lib.clang_CompileCommands_dispose(self.ccmds)

    def __len__(self):
        return int(conf.lib.clang_CompileCommands_getSize(self.ccmds))

    def __getitem__(self, i):
        cc = conf.lib.clang_CompileCommands_getCommand(self.ccmds, i)
        if not cc:
            raise IndexError
        return CompileCommand(cc, self)

    @staticmethod
    def from_result(res, fn, args):
        if not res:
            return None
        return CompileCommands(res)


class CompilationDatabase(ClangObject):
    """
    The CompilationDatabase is a wrapper class around
    clang::tooling::CompilationDatabase

    It enables querying how a specific source file can be built.
    """

    def __del__(self):
        conf.lib.clang_CompilationDatabase_dispose(self)

    @staticmethod
    def from_result(res, fn, args):
        if not res:
            raise CompilationDatabaseError(0,
                                           "CompilationDatabase loading failed")
        return CompilationDatabase(res)

    @staticmethod
    def fromDirectory(buildDir):
        """Builds a CompilationDatabase from the database found in buildDir"""
        errorCode = c_uint()
        try:
            cdb = conf.lib.clang_CompilationDatabase_fromDirectory(buildDir,
                                                                   byref(errorCode))
        except CompilationDatabaseError as e:
            raise CompilationDatabaseError(int(errorCode.value),
                                           "CompilationDatabase loading failed")
        return cdb

    def getCompileCommands(self, filename):
        """
        Get an iterable object providing all the CompileCommands available to
        build filename. Returns None if filename is not found in the database.
        """
        return conf.lib.clang_CompilationDatabase_getCompileCommands(self,
                                                                     filename)

    def getAllCompileCommands(self):
        """
        Get an iterable object providing all the CompileCommands available from
        the database.
        """
        return conf.lib.clang_CompilationDatabase_getAllCompileCommands(self)


# Now comes the plumbing to hook up the C library.

# Register callback types in common container.
callbacks['translation_unit_includes'] = CFUNCTYPE(None, c_object_p,
                                                   POINTER(SourceLocation), c_uint, py_object)
callbacks['cursor_visit'] = CFUNCTYPE(c_int, Cursor, Cursor, py_object)
callbacks['fields_visit'] = CFUNCTYPE(c_int, Cursor, py_object)

def register_function(lib, item, ignore_errors):
    # A function may not exist, if these bindings are used with an older or
    # incompatible version of libclang.so.
    try:
        func = getattr(lib, item[0])
    except AttributeError as e:
        msg = str(e) + ". Please ensure that your python bindings are " \
                       "compatible with your libclang.so version."
        if ignore_errors:
            return
        raise LibclangError(msg)

    if len(item) >= 2:
        func.argtypes = item[1]

    if len(item) >= 3:
        func.restype = item[2]

    if len(item) == 4:
        func.errcheck = item[3]


def register_functions(lib, ignore_errors):
    """Register function prototypes with a libclang library instance.

    This must be called as part of library instantiation so Python knows how
    to call out to the shared library.
    """

    def register(item):
        return register_function(lib, item, ignore_errors)

    for f in functionList:
        register(f)


def register_enumerations():
    for name, value in TokenKinds.__members__.items():
        TokenKind.register(value.value, name)

register_enumerations()

__all__ = [
    'AvailabilityKind',
    'CodeCompletionResults',
    'CompilationDatabase',
    'CompileCommands',
    'CompileCommand',
    'CursorKind',
    'Cursor',
    'Diagnostic',
    'File',
    'FixIt',
    'Index',
    'LinkageKind',
    'SourceLocation',
    'SourceRange',
    'TLSKind',
    'Token',
    'TranslationUnitLoadError',
    'TranslationUnit',
    'TypeKind',
    'Type',
]
