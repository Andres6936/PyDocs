from Clang.kinds.base_enumeration import BaseEnumeration


class RefQualifierKind(BaseEnumeration):
    """Describes a specific ref-qualifier of a type."""

    # The unique kind objects, indexed by id.
    _kinds = []
    _name_map = None

    def from_param(self):
        return self.value

    def __repr__(self):
        return 'RefQualifierKind.%s' % (self.name,)


RefQualifierKind.NONE = RefQualifierKind(0)
RefQualifierKind.LVALUE = RefQualifierKind(1)
RefQualifierKind.RVALUE = RefQualifierKind(2)
