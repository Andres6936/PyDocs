from clang.kinds.base_enumeration import BaseEnumeration


### Exception Specification Kinds ###
class ExceptionSpecificationKind(BaseEnumeration):
    """
    An ExceptionSpecificationKind describes the kind of exception specification
    that a function has.
    """

    # The required BaseEnumeration declarations.
    _kinds = []
    _name_map = None

    def __repr__(self):
        return 'ExceptionSpecificationKind.{}'.format(self.name)


ExceptionSpecificationKind.NONE = ExceptionSpecificationKind(0)
ExceptionSpecificationKind.DYNAMIC_NONE = ExceptionSpecificationKind(1)
ExceptionSpecificationKind.DYNAMIC = ExceptionSpecificationKind(2)
ExceptionSpecificationKind.MS_ANY = ExceptionSpecificationKind(3)
ExceptionSpecificationKind.BASIC_NOEXCEPT = ExceptionSpecificationKind(4)
ExceptionSpecificationKind.COMPUTED_NOEXCEPT = ExceptionSpecificationKind(5)
ExceptionSpecificationKind.UNEVALUATED = ExceptionSpecificationKind(6)
ExceptionSpecificationKind.UNINSTANTIATED = ExceptionSpecificationKind(7)
ExceptionSpecificationKind.UNPARSED = ExceptionSpecificationKind(8)