from ctypes import Structure, c_int

from Clang.pointers import c_object_p


class CodeCompletionResult(Structure):
    _fields_ = [('cursorKind', c_int), ('completionString', c_object_p)]

    def __repr__(self):
        from Clang.objects.completion_string import CompletionString
        return str(CompletionString(self.completionString))

    @property
    def kind(self):
        from Clang.kinds.cursor_kind import CursorKind
        return CursorKind.from_id(self.cursorKind)

    @property
    def string(self):
        from Clang.objects.completion_string import CompletionString
        return CompletionString(self.completionString)
