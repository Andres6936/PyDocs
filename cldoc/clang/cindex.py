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
import collections

from clang.config import conf
from clang.cursor import Cursor
from clang.decorators.cached_property import CachedProperty
from clang.exceptions.compilation_database import CompilationDatabaseError
from clang.exceptions.lib_clang import LibclangError
from clang.exceptions.translation_unit import TranslationUnitLoadError, TranslationUnitSaveError
from clang.kinds.availability_kind import AvailabilityKind
from clang.kinds.base_enumeration import BaseEnumeration
from clang.kinds.cursor_kind import CursorKind
from clang.kinds.exception_specification_kind import ExceptionSpecificationKind
from clang.kinds.linkage_kind import LinkageKind
from clang.kinds.ref_qualifier_kind import RefQualifierKind
from clang.kinds.template_argument_kind import TemplateArgumentKind
from clang.kinds.tls_kind import TLSKind
from clang.kinds.type_kind import TypeKind
from clang.objects.ccr_structure import CCRStructure
from clang.objects.code_completion_result import CodeCompletionResult
from clang.objects.code_completion_results import CodeCompletionResults
from clang.objects.completion_string import CompletionString
from clang.objects.file_inclusion import FileInclusion
from clang.objects.translation_unit import TranslationUnit
from clang.prototypes.functions import c_object_p, c_interop_string, b, callbacks
from clang.spelling_cache import SpellingCache
from clang.token_kinds import TokenKinds
from clang.utility.cx_string import _CXString
from clang.utility.diagnostic import Diagnostic
from clang.utility.fix_it import FixIt
from clang.utility.token_kind import TokenKind


### Structures and Utility Classes ###


class SourceLocation(Structure):
    """
    A SourceLocation represents a particular location within a source file.
    """
    _fields_ = [("ptr_data", c_void_p * 2), ("int_data", c_uint)]
    _data = None

    def _get_instantiation(self):
        if self._data is None:
            f, l, c, o = c_object_p(), c_uint(), c_uint(), c_uint()
            conf.lib.clang_getInstantiationLocation(self, byref(f), byref(l),
                                                    byref(c), byref(o))
            if f:
                f = File(f)
            else:
                f = None
            self._data = (f, int(l.value), int(c.value), int(o.value))
        return self._data

    @staticmethod
    def from_position(tu, file, line, column):
        """
        Retrieve the source location associated with a given file/line/column in
        a particular translation unit.
        """
        return conf.lib.clang_getLocation(tu, file, line, column)

    @staticmethod
    def from_offset(tu, file, offset):
        """Retrieve a SourceLocation from a given character offset.

        tu -- TranslationUnit file belongs to
        file -- File instance to obtain offset from
        offset -- Integer character offset within file
        """
        return conf.lib.clang_getLocationForOffset(tu, file, offset)

    @property
    def file(self):
        """Get the file represented by this source location."""
        return self._get_instantiation()[0]

    @property
    def line(self):
        """Get the line represented by this source location."""
        return self._get_instantiation()[1]

    @property
    def column(self):
        """Get the column represented by this source location."""
        return self._get_instantiation()[2]

    @property
    def offset(self):
        """Get the file offset represented by this source location."""
        return self._get_instantiation()[3]

    def __eq__(self, other):
        return conf.lib.clang_equalLocations(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        if self.file:
            filename = self.file.name
        else:
            filename = None
        return "File: {}, Line: {}, Column: {}".format(
            os.path.basename(filename), self.line, self.column
        )


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



class TokenGroup(object):
    """Helper class to facilitate token management.

    Tokens are allocated from libclang in chunks. They must be disposed of as a
    collective group.

    One purpose of this class is for instances to represent groups of allocated
    tokens. Each token in a group contains a reference back to an instance of
    this class. When all tokens from a group are garbage collected, it allows
    this class to be garbage collected. When this class is garbage collected,
    it calls the libclang destructor which invalidates all tokens in the group.

    You should not instantiate this class outside of this module.
    """

    def __init__(self, tu, memory, count):
        self._tu = tu
        self._memory = memory
        self._count = count

    def __del__(self):
        conf.lib.clang_disposeTokens(self._tu, self._memory, self._count)

    @staticmethod
    def get_tokens(tu, extent):
        """Helper method to return all tokens in an extent.

        This functionality is needed multiple places in this module. We define
        it here because it seems like a logical place.
        """
        tokens_memory = POINTER(Token)()
        tokens_count = c_uint()

        conf.lib.clang_tokenize(tu, extent, byref(tokens_memory),
                                byref(tokens_count))

        count = int(tokens_count.value)

        # If we get no tokens, no memory was allocated. Be sure not to return
        # anything and potentially call a destructor on nothing.
        if count < 1:
            return

        tokens_array = cast(tokens_memory, POINTER(Token * count)).contents

        token_group = TokenGroup(tu, tokens_memory, tokens_count)

        for i in range(0, count):
            token = Token()
            token.int_data = tokens_array[i].int_data
            token.ptr_data = tokens_array[i].ptr_data
            token._tu = tu
            token._group = token_group

            yield token

### Type Kinds ###

class Type(Structure):
    """
    The type of an element in the abstract syntax tree.
    """
    _fields_ = [("_kind_id", c_int), ("data", c_void_p * 2)]

    @property
    def kind(self):
        """Return the kind of this type."""
        return TypeKind.from_id(self._kind_id)

    def get_num_template_arguments(self):
        return conf.lib.clang_Type_getNumTemplateArguments(self)

    def get_template_argument_type(self, num):
        """Returns the CXType for the indicated template argument."""
        return conf.lib.clang_Type_getTemplateArgumentAsType(self, num)

    def argument_types(self):
        """Retrieve a container for the non-variadic arguments for this type.

        The returned object is iterable and indexable. Each item in the
        container is a Type instance.
        """

        class ArgumentsIterator(collections.Sequence):
            def __init__(self, parent):
                self.parent = parent
                self.length = None

            def __len__(self):
                if self.length is None:
                    self.length = conf.lib.clang_getNumArgTypes(self.parent)

                return self.length

            def __getitem__(self, key):
                # FIXME Support slice objects.
                if not isinstance(key, int):
                    raise TypeError("Must supply a non-negative int.")

                if key < 0:
                    raise IndexError("Only non-negative indexes are accepted.")

                if key >= len(self):
                    raise IndexError("Index greater than container length: "
                                     "%d > %d" % (key, len(self)))

                result = conf.lib.clang_getArgType(self.parent, key)
                if result.kind == TypeKind.INVALID:
                    raise IndexError("Argument could not be retrieved.")

                return result

        assert self.kind == TypeKind.FUNCTIONPROTO
        return ArgumentsIterator(self)

    @property
    def element_type(self):
        """Retrieve the Type of elements within this Type.

        If accessed on a type that is not an array, complex, or vector type, an
        exception will be raised.
        """
        result = conf.lib.clang_getElementType(self)
        if result.kind == TypeKind.INVALID:
            raise Exception('Element type not available on this type.')

        return result

    @property
    def element_count(self):
        """Retrieve the number of elements in this type.

        Returns an int.

        If the Type is not an array or vector, this raises.
        """
        result = conf.lib.clang_getNumElements(self)
        if result < 0:
            raise Exception('Type does not have elements.')

        return result

    @property
    def translation_unit(self):
        """The TranslationUnit to which this Type is associated."""
        # If this triggers an AttributeError, the instance was not properly
        # instantiated.
        return self._tu

    @staticmethod
    def from_result(res, fn, args):
        assert isinstance(res, Type)

        tu = None
        for arg in args:
            if hasattr(arg, 'translation_unit'):
                tu = arg.translation_unit
                break

        assert tu is not None
        res._tu = tu

        return res

    def get_canonical(self):
        """
        Return the canonical type for a Type.

        Clang's type system explicitly models typedefs and all the
        ways a specific type can be represented.  The canonical type
        is the underlying type with all the "sugar" removed.  For
        example, if 'T' is a typedef for 'int', the canonical type for
        'T' would be 'int'.
        """
        return conf.lib.clang_getCanonicalType(self)

    def is_const_qualified(self):
        """Determine whether a Type has the "const" qualifier set.

        This does not look through typedefs that may have added "const"
        at a different level.
        """
        return conf.lib.clang_isConstQualifiedType(self)

    def is_volatile_qualified(self):
        """Determine whether a Type has the "volatile" qualifier set.

        This does not look through typedefs that may have added "volatile"
        at a different level.
        """
        return conf.lib.clang_isVolatileQualifiedType(self)

    def is_restrict_qualified(self):
        """Determine whether a Type has the "restrict" qualifier set.

        This does not look through typedefs that may have added "restrict" at
        a different level.
        """
        return conf.lib.clang_isRestrictQualifiedType(self)

    def is_function_variadic(self):
        """Determine whether this function Type is a variadic function type."""
        assert self.kind == TypeKind.FUNCTIONPROTO

        return conf.lib.clang_isFunctionTypeVariadic(self)

    def is_pod(self):
        """Determine whether this Type represents plain old data (POD)."""
        return conf.lib.clang_isPODType(self)

    def get_pointee(self):
        """
        For pointer types, returns the type of the pointee.
        """
        return conf.lib.clang_getPointeeType(self)

    def get_declaration(self):
        """
        Return the cursor for the declaration of the given type.
        """
        return conf.lib.clang_getTypeDeclaration(self)

    def get_result(self):
        """
        Retrieve the result type associated with a function type.
        """
        return conf.lib.clang_getResultType(self)

    def get_array_element_type(self):
        """
        Retrieve the type of the elements of the array type.
        """
        return conf.lib.clang_getArrayElementType(self)

    def get_array_size(self):
        """
        Retrieve the size of the constant array.
        """
        return conf.lib.clang_getArraySize(self)

    def get_class_type(self):
        """
        Retrieve the class type of the member pointer type.
        """
        return conf.lib.clang_Type_getClassType(self)

    def get_named_type(self):
        """
        Retrieve the type named by the qualified-id.
        """
        return conf.lib.clang_Type_getNamedType(self)

    def get_align(self):
        """
        Retrieve the alignment of the record.
        """
        return conf.lib.clang_Type_getAlignOf(self)

    def get_size(self):
        """
        Retrieve the size of the record.
        """
        return conf.lib.clang_Type_getSizeOf(self)

    def get_offset(self, fieldname):
        """
        Retrieve the offset of a field in the record.
        """
        return conf.lib.clang_Type_getOffsetOf(self, fieldname)

    def get_ref_qualifier(self):
        """
        Retrieve the ref-qualifier of the type.
        """
        return RefQualifierKind.from_id(
            conf.lib.clang_Type_getCXXRefQualifier(self))

    def get_fields(self):
        """Return an iterator for accessing the fields of this type."""

        def visitor(field, children):
            assert field != conf.lib.clang_getNullCursor()

            # Create reference to TU so it isn't GC'd before Cursor.
            field._tu = self._tu
            fields.append(field)
            return 1  # continue

        fields = []
        conf.lib.clang_Type_visitFields(self,
                                        callbacks['fields_visit'](visitor), fields)
        return iter(fields)

    def get_exception_specification_kind(self):
        """
        Return the kind of the exception specification; a value from
        the ExceptionSpecificationKind enumeration.
        """
        return ExceptionSpecificationKind.from_id(
            conf.lib.clang.getExceptionSpecificationType(self))

    @property
    def spelling(self):
        """Retrieve the spelling of this Type."""
        return conf.lib.clang_getTypeSpelling(self)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return conf.lib.clang_equalTypes(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)


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


class Token(Structure):
    """Represents a single token from the preprocessor.

    Tokens are effectively segments of source code. Source code is first parsed
    into tokens before being converted into the AST and Cursors.

    Tokens are obtained from parsed TranslationUnit instances. You currently
    can't create tokens manually.
    """
    _fields_ = [
        ('int_data', c_uint * 4),
        ('ptr_data', c_void_p)
    ]

    @property
    def spelling(self):
        """The spelling of this token.

        This is the textual representation of the token in source.
        """
        return conf.lib.clang_getTokenSpelling(self._tu, self)

    @property
    def kind(self):
        """Obtain the TokenKind of the current token."""
        return TokenKind.from_value(conf.lib.clang_getTokenKind(self))

    @property
    def location(self):
        """The SourceLocation this Token occurs at."""
        return conf.lib.clang_getTokenLocation(self._tu, self)

    @property
    def extent(self):
        """The SourceRange this Token occupies."""
        return conf.lib.clang_getTokenExtent(self._tu, self)

    @property
    def cursor(self):
        """The Cursor this Token corresponds to."""
        cursor = Cursor()
        cursor._tu = self._tu

        conf.lib.clang_annotateTokens(self._tu, byref(self), 1, byref(cursor))

        return cursor


# Now comes the plumbing to hook up the C library.

# Register callback types in common container.
callbacks['translation_unit_includes'] = CFUNCTYPE(None, c_object_p,
                                                   POINTER(SourceLocation), c_uint, py_object)
callbacks['cursor_visit'] = CFUNCTYPE(c_int, Cursor, Cursor, py_object)
callbacks['fields_visit'] = CFUNCTYPE(c_int, Cursor, py_object)

# Functions strictly alphabetical order.
functionList = [
    ("clang_annotateTokens",
     [TranslationUnit, POINTER(Token), c_uint, POINTER(Cursor)]),

    ("clang_CompilationDatabase_dispose",
     [c_object_p]),

    ("clang_CompilationDatabase_fromDirectory",
     [c_interop_string, POINTER(c_uint)],
     c_object_p,
     CompilationDatabase.from_result),

    ("clang_CompilationDatabase_getAllCompileCommands",
     [c_object_p],
     c_object_p,
     CompileCommands.from_result),

    ("clang_CompilationDatabase_getCompileCommands",
     [c_object_p, c_interop_string],
     c_object_p,
     CompileCommands.from_result),

    ("clang_CompileCommands_dispose",
     [c_object_p]),

    ("clang_CompileCommands_getCommand",
     [c_object_p, c_uint],
     c_object_p),

    ("clang_CompileCommands_getSize",
     [c_object_p],
     c_uint),

    ("clang_CompileCommand_getArg",
     [c_object_p, c_uint],
     _CXString,
     _CXString.from_result),

    ("clang_CompileCommand_getDirectory",
     [c_object_p],
     _CXString,
     _CXString.from_result),

    ("clang_CompileCommand_getFilename",
     [c_object_p],
     _CXString,
     _CXString.from_result),

    ("clang_CompileCommand_getNumArgs",
     [c_object_p],
     c_uint),

    ("clang_codeCompleteAt",
     [TranslationUnit, c_interop_string, c_int, c_int, c_void_p, c_int, c_int],
     POINTER(CCRStructure)),

    ("clang_codeCompleteGetDiagnostic",
     [CodeCompletionResults, c_int],
     Diagnostic),

    ("clang_codeCompleteGetNumDiagnostics",
     [CodeCompletionResults],
     c_int),

    ("clang_createIndex",
     [c_int, c_int],
     c_object_p),

    ("clang_createTranslationUnit",
     [Index, c_interop_string],
     c_object_p),

    ("clang_CXXConstructor_isConvertingConstructor",
     [Cursor],
     bool),

    ("clang_CXXConstructor_isCopyConstructor",
     [Cursor],
     bool),

    ("clang_CXXConstructor_isDefaultConstructor",
     [Cursor],
     bool),

    ("clang_CXXConstructor_isMoveConstructor",
     [Cursor],
     bool),

    ("clang_CXXField_isMutable",
     [Cursor],
     bool),

    ("clang_CXXMethod_isConst",
     [Cursor],
     bool),

    ("clang_CXXMethod_isDefaulted",
     [Cursor],
     bool),

    ("clang_CXXMethod_isPureVirtual",
     [Cursor],
     bool),

    ("clang_CXXMethod_isStatic",
     [Cursor],
     bool),

    ("clang_CXXMethod_isVirtual",
     [Cursor],
     bool),

    ("clang_defaultDiagnosticDisplayOptions",
     [],
     c_uint),

    ("clang_defaultSaveOptions",
     [TranslationUnit],
     c_uint),

    ("clang_disposeCodeCompleteResults",
     [CodeCompletionResults]),

    # ("clang_disposeCXTUResourceUsage",
    #  [CXTUResourceUsage]),

    ("clang_disposeDiagnostic",
     [Diagnostic]),

    ("clang_defaultDiagnosticDisplayOptions",
     [],
     c_uint),

    ("clang_formatDiagnostic",
     [Diagnostic, c_uint],
     _CXString,
     _CXString.from_result),

    ("clang_disposeIndex",
     [Index]),

    ("clang_disposeString",
     [_CXString]),

    ("clang_disposeTokens",
     [TranslationUnit, POINTER(Token), c_uint]),

    ("clang_disposeTranslationUnit",
     [TranslationUnit]),

    ("clang_equalCursors",
     [Cursor, Cursor],
     bool),

    ("clang_equalLocations",
     [SourceLocation, SourceLocation],
     bool),

    ("clang_equalRanges",
     [SourceRange, SourceRange],
     bool),

    ("clang_equalTypes",
     [Type, Type],
     bool),

    ("clang_formatDiagnostic",
     [Diagnostic, c_uint],
     _CXString,
     _CXString.from_result),

    ("clang_getArgType",
     [Type, c_uint],
     Type,
     Type.from_result),

    ("clang_getArrayElementType",
     [Type],
     Type,
     Type.from_result),

    ("clang_getArraySize",
     [Type],
     c_longlong),

    ("clang_getFieldDeclBitWidth",
     [Cursor],
     c_int),

    ("clang_getCanonicalCursor",
     [Cursor],
     Cursor,
     Cursor.from_cursor_result),

    ("clang_getCanonicalType",
     [Type],
     Type,
     Type.from_result),

    ("clang_getChildDiagnostics",
     [Diagnostic],
     c_object_p),

    ("clang_getCompletionAvailability",
     [c_void_p],
     c_int),

    ("clang_getCompletionBriefComment",
     [c_void_p],
     _CXString,
     _CXString.from_result),

    ("clang_getCompletionChunkCompletionString",
     [c_void_p, c_int],
     c_object_p),

    ("clang_getCompletionChunkKind",
     [c_void_p, c_int],
     c_int),

    ("clang_getCompletionChunkText",
     [c_void_p, c_int],
     _CXString,
     _CXString.from_result),

    ("clang_getCompletionPriority",
     [c_void_p],
     c_int),

    ("clang_getCString",
     [_CXString],
     c_interop_string,
     c_interop_string.to_python_string),

    ("clang_getCursor",
     [TranslationUnit, SourceLocation],
     Cursor),

    ("clang_getCursorAvailability",
     [Cursor],
     c_int),

    ("clang_getCursorDefinition",
     [Cursor],
     Cursor,
     Cursor.from_result),

    ("clang_getCursorDisplayName",
     [Cursor],
     _CXString,
     _CXString.from_result),

    ("clang_getCursorExtent",
     [Cursor],
     SourceRange),

    ("clang_getCursorLexicalParent",
     [Cursor],
     Cursor,
     Cursor.from_cursor_result),

    ("clang_getCursorLocation",
     [Cursor],
     SourceLocation),

    ("clang_getCursorReferenced",
     [Cursor],
     Cursor,
     Cursor.from_result),

    ("clang_getCursorReferenceNameRange",
     [Cursor, c_uint, c_uint],
     SourceRange),

    ("clang_getCursorSemanticParent",
     [Cursor],
     Cursor,
     Cursor.from_cursor_result),

    ("clang_getCursorSpelling",
     [Cursor],
     _CXString,
     _CXString.from_result),

    ("clang_getCursorType",
     [Cursor],
     Type,
     Type.from_result),

    ("clang_getCursorUSR",
     [Cursor],
     _CXString,
     _CXString.from_result),

    ("clang_Cursor_getMangling",
     [Cursor],
     _CXString,
     _CXString.from_result),

    # ("clang_getCXTUResourceUsage",
    #  [TranslationUnit],
    #  CXTUResourceUsage),

    ("clang_getCXXAccessSpecifier",
     [Cursor],
     c_uint),

    ("clang_getDeclObjCTypeEncoding",
     [Cursor],
     _CXString,
     _CXString.from_result),

    ("clang_getDiagnostic",
     [c_object_p, c_uint],
     c_object_p),

    ("clang_getDiagnosticCategory",
     [Diagnostic],
     c_uint),

    ("clang_getDiagnosticCategoryText",
     [Diagnostic],
     _CXString,
     _CXString.from_result),

    ("clang_getDiagnosticFixIt",
     [Diagnostic, c_uint, POINTER(SourceRange)],
     _CXString,
     _CXString.from_result),

    ("clang_getDiagnosticInSet",
     [c_object_p, c_uint],
     c_object_p),

    ("clang_getDiagnosticLocation",
     [Diagnostic],
     SourceLocation),

    ("clang_getDiagnosticNumFixIts",
     [Diagnostic],
     c_uint),

    ("clang_getDiagnosticNumRanges",
     [Diagnostic],
     c_uint),

    ("clang_getDiagnosticOption",
     [Diagnostic, POINTER(_CXString)],
     _CXString,
     _CXString.from_result),

    ("clang_getDiagnosticRange",
     [Diagnostic, c_uint],
     SourceRange),

    ("clang_getDiagnosticSeverity",
     [Diagnostic],
     c_int),

    ("clang_getDiagnosticSpelling",
     [Diagnostic],
     _CXString,
     _CXString.from_result),

    ("clang_getElementType",
     [Type],
     Type,
     Type.from_result),

    ("clang_getEnumConstantDeclUnsignedValue",
     [Cursor],
     c_ulonglong),

    ("clang_getEnumConstantDeclValue",
     [Cursor],
     c_longlong),

    ("clang_getEnumDeclIntegerType",
     [Cursor],
     Type,
     Type.from_result),

    ("clang_getFile",
     [TranslationUnit, c_interop_string],
     c_object_p),

    ("clang_getFileName",
     [File],
     _CXString,
     _CXString.from_result),

    ("clang_getFileTime",
     [File],
     c_uint),

    ("clang_getIBOutletCollectionType",
     [Cursor],
     Type,
     Type.from_result),

    ("clang_getIncludedFile",
     [Cursor],
     File,
     File.from_cursor_result),

    ("clang_getInclusions",
     [TranslationUnit, callbacks['translation_unit_includes'], py_object]),

    ("clang_getInstantiationLocation",
     [SourceLocation, POINTER(c_object_p), POINTER(c_uint), POINTER(c_uint),
      POINTER(c_uint)]),

    ("clang_getLocation",
     [TranslationUnit, File, c_uint, c_uint],
     SourceLocation),

    ("clang_getLocationForOffset",
     [TranslationUnit, File, c_uint],
     SourceLocation),

    ("clang_getNullCursor",
     None,
     Cursor),

    ("clang_getNumArgTypes",
     [Type],
     c_uint),

    ("clang_getNumCompletionChunks",
     [c_void_p],
     c_int),

    ("clang_getNumDiagnostics",
     [c_object_p],
     c_uint),

    ("clang_getNumDiagnosticsInSet",
     [c_object_p],
     c_uint),

    ("clang_getNumElements",
     [Type],
     c_longlong),

    ("clang_getNumOverloadedDecls",
     [Cursor],
     c_uint),

    ("clang_getOverloadedDecl",
     [Cursor, c_uint],
     Cursor,
     Cursor.from_cursor_result),

    ("clang_getPointeeType",
     [Type],
     Type,
     Type.from_result),

    ("clang_getRange",
     [SourceLocation, SourceLocation],
     SourceRange),

    ("clang_getRangeEnd",
     [SourceRange],
     SourceLocation),

    ("clang_getRangeStart",
     [SourceRange],
     SourceLocation),

    ("clang_getResultType",
     [Type],
     Type,
     Type.from_result),

    ("clang_getSpecializedCursorTemplate",
     [Cursor],
     Cursor,
     Cursor.from_cursor_result),

    ("clang_getTemplateCursorKind",
     [Cursor],
     c_uint),

    ("clang_getTokenExtent",
     [TranslationUnit, Token],
     SourceRange),

    ("clang_getTokenKind",
     [Token],
     c_uint),

    ("clang_getTokenLocation",
     [TranslationUnit, Token],
     SourceLocation),

    ("clang_getTokenSpelling",
     [TranslationUnit, Token],
     _CXString,
     _CXString.from_result),

    ("clang_getTranslationUnitCursor",
     [TranslationUnit],
     Cursor,
     Cursor.from_result),

    ("clang_getTranslationUnitSpelling",
     [TranslationUnit],
     _CXString,
     _CXString.from_result),

    ("clang_getTUResourceUsageName",
     [c_uint],
     c_interop_string,
     c_interop_string.to_python_string),

    ("clang_getTypeDeclaration",
     [Type],
     Cursor,
     Cursor.from_result),

    ("clang_getTypedefDeclUnderlyingType",
     [Cursor],
     Type,
     Type.from_result),

    ("clang_getTypeKindSpelling",
     [c_uint],
     _CXString,
     _CXString.from_result),

    ("clang_getTypeSpelling",
     [Type],
     _CXString,
     _CXString.from_result),

    ("clang_hashCursor",
     [Cursor],
     c_uint),

    ("clang_isAttribute",
     [CursorKind],
     bool),

    ("clang_isConstQualifiedType",
     [Type],
     bool),

    ("clang_isCursorDefinition",
     [Cursor],
     bool),

    ("clang_isDeclaration",
     [CursorKind],
     bool),

    ("clang_isExpression",
     [CursorKind],
     bool),

    ("clang_isFileMultipleIncludeGuarded",
     [TranslationUnit, File],
     bool),

    ("clang_isFunctionTypeVariadic",
     [Type],
     bool),

    ("clang_isInvalid",
     [CursorKind],
     bool),

    ("clang_isPODType",
     [Type],
     bool),

    ("clang_isPreprocessing",
     [CursorKind],
     bool),

    ("clang_isReference",
     [CursorKind],
     bool),

    ("clang_isRestrictQualifiedType",
     [Type],
     bool),

    ("clang_isStatement",
     [CursorKind],
     bool),

    ("clang_isTranslationUnit",
     [CursorKind],
     bool),

    ("clang_isUnexposed",
     [CursorKind],
     bool),

    ("clang_isVirtualBase",
     [Cursor],
     bool),

    ("clang_isVolatileQualifiedType",
     [Type],
     bool),

    ("clang_parseTranslationUnit",
     [Index, c_interop_string, c_void_p, c_int, c_void_p, c_int, c_int],
     c_object_p),

    ("clang_reparseTranslationUnit",
     [TranslationUnit, c_int, c_void_p, c_int],
     c_int),

    ("clang_saveTranslationUnit",
     [TranslationUnit, c_interop_string, c_uint],
     c_int),

    ("clang_tokenize",
     [TranslationUnit, SourceRange, POINTER(POINTER(Token)), POINTER(c_uint)]),

    ("clang_visitChildren",
     [Cursor, callbacks['cursor_visit'], py_object],
     c_uint),

    ("clang_Cursor_getNumArguments",
     [Cursor],
     c_int),

    ("clang_Cursor_getArgument",
     [Cursor, c_uint],
     Cursor,
     Cursor.from_result),

    ("clang_Cursor_getNumTemplateArguments",
     [Cursor],
     c_int),

    ("clang_Cursor_getTemplateArgumentKind",
     [Cursor, c_uint],
     TemplateArgumentKind.from_id),

    ("clang_Cursor_getTemplateArgumentType",
     [Cursor, c_uint],
     Type,
     Type.from_result),

    ("clang_Cursor_getTemplateArgumentValue",
     [Cursor, c_uint],
     c_longlong),

    ("clang_Cursor_getTemplateArgumentUnsignedValue",
     [Cursor, c_uint],
     c_ulonglong),

    ("clang_Cursor_isAnonymous",
     [Cursor],
     bool),

    ("clang_Cursor_isBitField",
     [Cursor],
     bool),

    ("clang_Cursor_getBriefCommentText",
     [Cursor],
     _CXString,
     _CXString.from_result),

    ("clang_Cursor_getRawCommentText",
     [Cursor],
     _CXString,
     _CXString.from_result),

    ("clang_Cursor_getOffsetOfField",
     [Cursor],
     c_longlong),

    ("clang_Type_getNumTemplateArguments",
     [Type],
     c_int),

    ("clang_Type_getTemplateArgumentAsType",
     [Type, c_uint],
     Type,
     Type.from_result),

    ("clang_Type_getAlignOf",
     [Type],
     c_longlong),

    ("clang_Type_getClassType",
     [Type],
     Type,
     Type.from_result),

    ("clang_Type_getOffsetOf",
     [Type, c_interop_string],
     c_longlong),

    ("clang_Type_getSizeOf",
     [Type],
     c_longlong),

    ("clang_Type_getCXXRefQualifier",
     [Type],
     c_uint),

    ("clang_Type_getNamedType",
     [Type],
     Type,
     Type.from_result),

    ("clang_Type_visitFields",
     [Type, callbacks['fields_visit'], py_object],
     c_uint),
]





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
