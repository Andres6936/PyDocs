from clang.kinds.base_enumeration import BaseEnumeration


class TLSKind(BaseEnumeration):
    """Describes the kind of thread-local storage (TLS) of a cursor."""

    # The unique kind objects, indexed by id.
    _kinds = []
    _name_map = None

    def from_param(self):
        return self.value

    def __repr__(self):
        return 'TLSKind.%s' % (self.name,)


TLSKind.NONE = TLSKind(0)
TLSKind.DYNAMIC = TLSKind(1)
TLSKind.STATIC = TLSKind(2)
