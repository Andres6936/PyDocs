# Functions strictly alphabetical order.
from ctypes import c_uint, POINTER, c_int, c_void_p, c_char_p, c_longlong, c_ulonglong, py_object, CFUNCTYPE

from clang.cursor import Cursor
from clang.kinds.cursor_kind import CursorKind
from clang.kinds.template_argument_kind import TemplateArgumentKind
from clang.objects.ccr_structure import CCRStructure
from clang.objects.code_completion_results import CodeCompletionResults
from clang.objects.compilation_database import CompilationDatabase
from clang.objects.compile_commands import CompileCommands
from clang.objects.file import File
from clang.objects.index import Index
from clang.objects.translation_unit import TranslationUnit
from clang.token import Token
from clang.type import Type
from clang.utility.cx_string import _CXString
from clang.utility.diagnostic import Diagnostic
from clang.utility.source_location import SourceLocation
from clang.utility.source_range import SourceRange


# Python 3 strings are unicode, translate them to/from utf8 for C-interop.
class c_interop_string(c_char_p):

    def __init__(self, p=None):
        if p is None:
            p = ""
        if isinstance(p, str):
            p = p.encode("utf8")
        super(c_char_p, self).__init__(p)

    def __str__(self):
        return self.value

    @property
    def value(self):
        if super(c_char_p, self).value is None:
            return None
        return super(c_char_p, self).value.decode("utf8")

    @classmethod
    def from_param(cls, param):
        if isinstance(param, str):
            return cls(param)
        if isinstance(param, bytes):
            return cls(param)
        if param is None:
            # Support passing null to C functions expecting char arrays
            return None
        raise TypeError("Cannot convert '{}' to '{}'".format(type(param).__name__, cls.__name__))

    @staticmethod
    def to_python_string(x, *args):
        return x.value


def b(x):
    if isinstance(x, bytes):
        return x
    return x.encode('utf8')


# ctypes doesn't implicitly convert c_void_p to the appropriate wrapper
# object. This is a problem, because it means that from_parameter will see an
# integer and pass the wrong value on platforms where int != void*. Work around
# this by marshalling object arguments as void**.
c_object_p = POINTER(c_void_p)

callbacks = {}

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

# Now comes the plumbing to hook up the C library.

# Register callback types in common container.
callbacks['translation_unit_includes'] = CFUNCTYPE(None, c_object_p,
                                                   POINTER(SourceLocation), c_uint, py_object)
callbacks['cursor_visit'] = CFUNCTYPE(c_int, Cursor, Cursor, py_object)
callbacks['fields_visit'] = CFUNCTYPE(c_int, Cursor, py_object)
