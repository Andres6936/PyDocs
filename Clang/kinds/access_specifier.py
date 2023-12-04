from Clang.kinds.base_enumeration import BaseEnumeration


### C++ access specifiers ###
class AccessSpecifier(BaseEnumeration):
    """
    Describes the access of a C++ class member
    """

    # The unique kind objects, index by id.
    _kinds = []
    _name_map = None

    def from_param(self):
        return self.value

    def __repr__(self):
        return 'AccessSpecifier.%s' % (self.name,)


AccessSpecifier.INVALID = AccessSpecifier(0)
AccessSpecifier.PUBLIC = AccessSpecifier(1)
AccessSpecifier.PROTECTED = AccessSpecifier(2)
AccessSpecifier.PRIVATE = AccessSpecifier(3)
AccessSpecifier.NONE = AccessSpecifier(4)
