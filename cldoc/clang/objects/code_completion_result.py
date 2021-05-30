from ctypes import Structure, c_int

from clang.kinds.cursor_kind import CursorKind
from clang.objects.completion_string import CompletionString
from clang.prototypes.functions import c_object_p


class CodeCompletionResult(Structure):
    _fields_ = [('cursorKind', c_int), ('completionString', c_object_p)]

    def __repr__(self):
        return str(CompletionString(self.completionString))

    @property
    def kind(self):
        return CursorKind.from_id(self.cursorKind)

    @property
    def string(self):
        return CompletionString(self.completionString)
