from ctypes import c_char_p

from Clang.config import conf
from Clang.exceptions.translation_unit import TranslationUnitLoadError, TranslationUnitSaveError
from Clang.objects.clang_object import ClangObject
from Clang.objects.cx_unsaved_file import _CXUnsavedFile
from Clang.objects.file import File
from Clang.objects.index import Index
from Clang.utility.diagnostic import Diagnostic
from Clang.utility.source_location import SourceLocation
from Clang.utility.source_range import SourceRange
from Clang.utility.token_group import TokenGroup


class TranslationUnit(ClangObject):
    """Represents a source code translation unit.

    This is one of the main types in the API. Any time you wish to interact
    with Clang's representation of a source file, you typically start with a
    translation unit.
    """

    # Default parsing mode.
    PARSE_NONE = 0

    # Instruct the parser to create a detailed processing record containing
    # metadata not normally retained.
    PARSE_DETAILED_PROCESSING_RECORD = 1

    # Indicates that the translation unit is incomplete. This is typically used
    # when parsing headers.
    PARSE_INCOMPLETE = 2

    # Instruct the parser to create a pre-compiled preamble for the translation
    # unit. This caches the preamble (included files at top of source file).
    # This is useful if the translation unit will be reparsed and you don't
    # want to incur the overhead of reparsing the preamble.
    PARSE_PRECOMPILED_PREAMBLE = 4

    # Cache code completion information on parse. This adds time to parsing but
    # speeds up code completion.
    PARSE_CACHE_COMPLETION_RESULTS = 8

    # Flags with values 16 and 32 are deprecated and intentionally omitted.

    # Do not parse function bodies. This is useful if you only care about
    # searching for declarations/definitions.
    PARSE_SKIP_FUNCTION_BODIES = 64

    # Used to indicate that brief documentation comments should be included
    # into the set of code completions returned from this translation unit.
    PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION = 128

    @classmethod
    def from_source(cls, filename, args=None, unsaved_files=None, options=0,
                    index=None):
        """Create a TranslationUnit by parsing source.

        This is capable of processing source code both from files on the
        filesystem as well as in-memory contents.

        Command-line arguments that would be passed to clang are specified as
        a list via args. These can be used to specify include paths, warnings,
        etc. e.g. ["-Wall", "-I/path/to/include"].

        In-memory file content can be provided via unsaved_files. This is an
        iterable of 2-tuples. The first element is the str filename. The
        second element defines the content. Content can be provided as str
        source code or as file objects (anything with a read() method). If
        a file object is being used, content will be read until EOF and the
        read cursor will not be reset to its original position.

        options is a bitwise or of TranslationUnit.PARSE_XXX flags which will
        control parsing behavior.

        index is an Index instance to utilize. If not provided, a new Index
        will be created for this TranslationUnit.

        To parse source from the filesystem, the filename of the file to parse
        is specified by the filename argument. Or, filename could be None and
        the args list would contain the filename(s) to parse.

        To parse source from an in-memory buffer, set filename to the virtual
        filename you wish to associate with this source (e.g. "test.c"). The
        contents of that file are then provided in unsaved_files.

        If an error occurs, a TranslationUnitLoadError is raised.

        Please note that a TranslationUnit with parser errors may be returned.
        It is the caller's responsibility to check tu.diagnostics for errors.

        Also note that Clang infers the source language from the extension of
        the input filename. If you pass in source code containing a C++ class
        declaration with the filename "test.c" parsing will fail.
        """
        if args is None:
            args = []

        if unsaved_files is None:
            unsaved_files = []

        if index is None:
            index = Index.create()

        args_array = None
        if len(args) > 0:
            from Clang.prototypes.functions import b
            args_array = (c_char_p * len(args))(*[b(x) for x in args])

        unsaved_array = None
        if len(unsaved_files) > 0:
            unsaved_array = (_CXUnsavedFile * len(unsaved_files))()
            for i, (name, contents) in enumerate(unsaved_files):
                if hasattr(contents, "read"):
                    contents = contents.read()

                unsaved_array[i].name = b(name)
                unsaved_array[i].contents = b(contents)
                unsaved_array[i].length = len(contents)

        ptr = conf.lib.clang_parseTranslationUnit(index, filename, args_array,
                                                  len(args), unsaved_array,
                                                  len(unsaved_files), options)

        if not ptr:
            raise TranslationUnitLoadError("Error parsing translation unit.")

        return cls(ptr, index=index)

    @classmethod
    def from_ast_file(cls, filename, index=None):
        """Create a TranslationUnit instance from a saved AST file.

        A previously-saved AST file (provided with -emit-ast or
        TranslationUnit.save()) is loaded from the filename specified.

        If the file cannot be loaded, a TranslationUnitLoadError will be
        raised.

        index is optional and is the Index instance to use. If not provided,
        a default Index will be created.
        """
        if index is None:
            index = Index.create()

        ptr = conf.lib.clang_createTranslationUnit(index, filename)
        if not ptr:
            raise TranslationUnitLoadError(filename)

        return cls(ptr=ptr, index=index)

    def __init__(self, ptr, index):
        """Create a TranslationUnit instance.

        TranslationUnits should be created using one of the from_* @classmethod
        functions above. __init__ is only called internally.
        """
        assert isinstance(index, Index)
        self.index = index
        ClangObject.__init__(self, ptr)

    def __del__(self):
        conf.lib.clang_disposeTranslationUnit(self)

    @property
    def cursor(self):
        """Retrieve the cursor that represents the given translation unit."""
        return conf.lib.clang_getTranslationUnitCursor(self)

    @property
    def spelling(self):
        """Get the original translation unit source file name."""
        return conf.lib.clang_getTranslationUnitSpelling(self)

    def get_includes(self):
        """
        Return an iterable sequence of FileInclusion objects that describe the
        sequence of inclusions in a translation unit. The first object in
        this sequence is always the input file. Note that this method will not
        recursively iterate over header files included through precompiled
        headers.
        """

        def visitor(fobj, lptr, depth, includes):
            if depth > 0:
                loc = lptr.contents
                from Clang.objects.file_inclusion import FileInclusion
                includes.append(FileInclusion(loc.file, File(fobj), loc, depth))

        # Automatically adapt CIndex/ctype pointers to python objects
        includes = []
        from Clang.prototypes.functions import callbacks
        conf.lib.clang_getInclusions(self,
                                     callbacks['translation_unit_includes'](visitor), includes)

        return iter(includes)

    def get_file(self, filename: str):
        """Obtain a File from this translation unit."""

        return File.from_name(self, filename)

    def get_location(self, filename, position):
        """Obtain a SourceLocation for a file in this translation unit.

        The position can be specified by passing:

          - Integer file offset. Initial file offset is 0.
          - 2-tuple of (line number, column number). Initial file position is
            (0, 0)
        """
        f = self.get_file(filename)

        if isinstance(position, int):
            return SourceLocation.from_offset(self, f, position)

        return SourceLocation.from_position(self, f, position[0], position[1])

    def get_extent(self, filename: str, locations):
        """Obtain a SourceRange from this translation unit.

        The bounds of the SourceRange must ultimately be defined by a start and
        end SourceLocation. For the locations argument, you can pass:

          - 2 SourceLocation instances in a 2-tuple or list.
          - 2 int file offsets via a 2-tuple or list.
          - 2 2-tuple or lists of (line, column) pairs in a 2-tuple or list.

        e.g.

        get_extent('foo.c', (5, 10))
        get_extent('foo.c', ((1, 1), (1, 15)))
        """
        f = self.get_file(filename)

        if len(locations) < 2:
            raise Exception('Must pass object with at least 2 elements')

        start_location, end_location = locations

        if hasattr(start_location, '__len__'):
            start_location = SourceLocation.from_position(self, f,
                                                          start_location[0], start_location[1])
        elif isinstance(start_location, int):
            start_location = SourceLocation.from_offset(self, f,
                                                        start_location)

        if hasattr(end_location, '__len__'):
            end_location = SourceLocation.from_position(self, f,
                                                        end_location[0], end_location[1])
        elif isinstance(end_location, int):
            end_location = SourceLocation.from_offset(self, f, end_location)

        assert isinstance(start_location, SourceLocation)
        assert isinstance(end_location, SourceLocation)

        return SourceRange.from_locations(start_location, end_location)

    @property
    def diagnostics(self):
        """
        Return an iterable (and indexable) object containing the diagnostics.
        """

        class DiagIterator:
            def __init__(self, tu):
                self.tu = tu

            def __len__(self):
                return int(conf.lib.clang_getNumDiagnostics(self.tu))

            def __getitem__(self, key):
                diag = conf.lib.clang_getDiagnostic(self.tu, key)
                if not diag:
                    raise IndexError
                return Diagnostic(diag)

        return DiagIterator(self)

    def reparse(self, unsaved_files=None, options=0):
        """
        Reparse an already parsed translation unit.

        In-memory contents for files can be provided by passing a list of pairs
        as unsaved_files, the first items should be the filenames to be mapped
        and the second should be the contents to be substituted for the
        file. The contents may be passed as strings or file objects.
        """
        if unsaved_files is None:
            unsaved_files = []

        unsaved_files_array = 0
        if len(unsaved_files):
            unsaved_files_array = (_CXUnsavedFile * len(unsaved_files))()
            for i, (name, value) in enumerate(unsaved_files):
                if not isinstance(value, str):
                    # FIXME: It would be great to support an efficient version
                    # of this, one day.
                    value = value.read()
                    print(value)
                if not isinstance(value, str):
                    raise TypeError('Unexpected unsaved file contents.')
                unsaved_files_array[i].name = name
                unsaved_files_array[i].contents = value
                unsaved_files_array[i].length = len(value)
        ptr = conf.lib.clang_reparseTranslationUnit(self, len(unsaved_files),
                                                    unsaved_files_array, options)

    def save(self, filename):
        """Saves the TranslationUnit to a file.

        This is equivalent to passing -emit-ast to the clang frontend. The
        saved file can be loaded back into a TranslationUnit. Or, if it
        corresponds to a header, it can be used as a pre-compiled header file.

        If an error occurs while saving, a TranslationUnitSaveError is raised.
        If the error was TranslationUnitSaveError.ERROR_INVALID_TU, this means
        the constructed TranslationUnit was not valid at time of save. In this
        case, the reason(s) why should be available via
        TranslationUnit.diagnostics().

        filename -- The path to save the translation unit to.
        """
        options = conf.lib.clang_defaultSaveOptions(self)
        result = int(conf.lib.clang_saveTranslationUnit(self, filename,
                                                        options))
        if result != 0:
            raise TranslationUnitSaveError(result,
                                           'Error saving TranslationUnit.')

    def codeComplete(self, path, line, column, unsaved_files=None,
                     include_macros=False, include_code_patterns=False,
                     include_brief_comments=False):
        """
        Code complete in this translation unit.

        In-memory contents for files can be provided by passing a list of pairs
        as unsaved_files, the first items should be the filenames to be mapped
        and the second should be the contents to be substituted for the
        file. The contents may be passed as strings or file objects.
        """
        options = 0

        if include_macros:
            options += 1

        if include_code_patterns:
            options += 2

        if include_brief_comments:
            options += 4

        if unsaved_files is None:
            unsaved_files = []

        unsaved_files_array = 0
        if len(unsaved_files):
            unsaved_files_array = (_CXUnsavedFile * len(unsaved_files))()
            for i, (name, value) in enumerate(unsaved_files):
                if not isinstance(value, str):
                    # FIXME: It would be great to support an efficient version
                    # of this, one day.
                    value = value.read()
                    print(value)
                if not isinstance(value, str):
                    raise TypeError('Unexpected unsaved file contents.')
                from Clang.prototypes.functions import b
                unsaved_files_array[i].name = b(name)
                unsaved_files_array[i].contents = b(value)
                unsaved_files_array[i].length = len(value)
        ptr = conf.lib.clang_codeCompleteAt(self, path, line, column,
                                            unsaved_files_array, len(unsaved_files), options)
        if ptr:
            from Clang.objects.code_completion_results import CodeCompletionResults
            return CodeCompletionResults(ptr)
        return None

    def get_tokens(self, locations=None, extent=None):
        """Obtain tokens in this translation unit.

        This is a generator for Token instances. The caller specifies a range
        of source code to obtain tokens for. The range can be specified as a
        2-tuple of SourceLocation or as a SourceRange. If both are defined,
        behavior is undefined.
        """
        if locations is not None:
            extent = SourceRange(start=locations[0], end=locations[1])

        return TokenGroup.get_tokens(self, extent)
