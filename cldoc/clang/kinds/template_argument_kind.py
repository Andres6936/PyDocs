from clang.kinds.base_enumeration import BaseEnumeration


### Template Argument Kinds ###
class TemplateArgumentKind(BaseEnumeration):
    """
    A TemplateArgumentKind describes the kind of entity that a template argument
    represents.
    """

    # The required BaseEnumeration declarations.
    _kinds = []
    _name_map = None


TemplateArgumentKind.NULL = TemplateArgumentKind(0)
TemplateArgumentKind.TYPE = TemplateArgumentKind(1)
TemplateArgumentKind.DECLARATION = TemplateArgumentKind(2)
TemplateArgumentKind.NULLPTR = TemplateArgumentKind(3)
TemplateArgumentKind.INTEGRAL = TemplateArgumentKind(4)