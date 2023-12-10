from Clang.kinds.base_enumeration import BaseEnumeration


class LinkageKind(BaseEnumeration):
    """Describes the kind of linkage of a cursor."""

    # The unique kind objects, indexed by id.
    _kinds = []
    _name_map = None

    def from_param(self):
        return self.value

    def __repr__(self):
        return 'LinkageKind.%s' % (self.name,)


LinkageKind.INVALID = LinkageKind(0)
LinkageKind.NO_LINKAGE = LinkageKind(1)
LinkageKind.INTERNAL = LinkageKind(2)
LinkageKind.UNIQUE_EXTERNAL = LinkageKind(3)
LinkageKind.EXTERNAL = LinkageKind(4)
