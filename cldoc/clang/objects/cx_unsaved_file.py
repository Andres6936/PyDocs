class _CXUnsavedFile(Structure):
    """Helper for passing unsaved file arguments."""
    _fields_ = [("name", c_char_p), ("contents", c_char_p), ('length', c_ulong)]
