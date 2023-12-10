from ctypes import POINTER

from Clang.config import conf
from Clang.objects.ccr_structure import CCRStructure
from Clang.objects.clang_object import ClangObject


class CodeCompletionResults(ClangObject):
    def __init__(self, ptr, obj):
        super().__init__(obj)
        assert isinstance(ptr, POINTER(CCRStructure)) and ptr
        self.ptr = self._as_parameter_ = ptr

    def from_param(self):
        return self._as_parameter_

    def __del__(self):
        conf.lib.clang_disposeCodeCompleteResults(self)

    @property
    def results(self):
        return self.ptr.contents

    @property
    def diagnostics(self):
        class DiagnosticsItr:
            def __init__(self, ccr):
                self.ccr = ccr

            def __len__(self):
                return int(
                    conf.lib.clang_codeCompleteGetNumDiagnostics(self.ccr))

            def __getitem__(self, key):
                return conf.lib.clang_codeCompleteGetDiagnostic(self.ccr, key)

        return DiagnosticsItr(self)
