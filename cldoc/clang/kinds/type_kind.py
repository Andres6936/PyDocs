from clang.kinds.base_enumeration import BaseEnumeration


### Type Kinds ###
class TypeKind(BaseEnumeration):
    """
    Describes the kind of type.
    """

    # The unique kind objects, indexed by id.
    _kinds = []
    _name_map = None

    @property
    def spelling(self):
        """Retrieve the spelling of this TypeKind."""
        return conf.lib.clang_getTypeKindSpelling(self.value)

    def __repr__(self):
        return 'TypeKind.%s' % (self.name,)


TypeKind.INVALID = TypeKind(0)
TypeKind.UNEXPOSED = TypeKind(1)
TypeKind.VOID = TypeKind(2)
TypeKind.BOOL = TypeKind(3)
TypeKind.CHAR_U = TypeKind(4)
TypeKind.UCHAR = TypeKind(5)
TypeKind.CHAR16 = TypeKind(6)
TypeKind.CHAR32 = TypeKind(7)
TypeKind.USHORT = TypeKind(8)
TypeKind.UINT = TypeKind(9)
TypeKind.ULONG = TypeKind(10)
TypeKind.ULONGLONG = TypeKind(11)
TypeKind.UINT128 = TypeKind(12)
TypeKind.CHAR_S = TypeKind(13)
TypeKind.SCHAR = TypeKind(14)
TypeKind.WCHAR = TypeKind(15)
TypeKind.SHORT = TypeKind(16)
TypeKind.INT = TypeKind(17)
TypeKind.LONG = TypeKind(18)
TypeKind.LONGLONG = TypeKind(19)
TypeKind.INT128 = TypeKind(20)
TypeKind.FLOAT = TypeKind(21)
TypeKind.DOUBLE = TypeKind(22)
TypeKind.LONGDOUBLE = TypeKind(23)
TypeKind.NULLPTR = TypeKind(24)
TypeKind.OVERLOAD = TypeKind(25)
TypeKind.DEPENDENT = TypeKind(26)
TypeKind.OBJCID = TypeKind(27)
TypeKind.OBJCCLASS = TypeKind(28)
TypeKind.OBJCSEL = TypeKind(29)
TypeKind.FLOAT128 = TypeKind(30)
TypeKind.HALF = TypeKind(31)
TypeKind.COMPLEX = TypeKind(100)
TypeKind.POINTER = TypeKind(101)
TypeKind.BLOCKPOINTER = TypeKind(102)
TypeKind.LVALUEREFERENCE = TypeKind(103)
TypeKind.RVALUEREFERENCE = TypeKind(104)
TypeKind.RECORD = TypeKind(105)
TypeKind.ENUM = TypeKind(106)
TypeKind.TYPEDEF = TypeKind(107)
TypeKind.OBJCINTERFACE = TypeKind(108)
TypeKind.OBJCOBJECTPOINTER = TypeKind(109)
TypeKind.FUNCTIONNOPROTO = TypeKind(110)
TypeKind.FUNCTIONPROTO = TypeKind(111)
TypeKind.CONSTANTARRAY = TypeKind(112)
TypeKind.VECTOR = TypeKind(113)
TypeKind.INCOMPLETEARRAY = TypeKind(114)
TypeKind.VARIABLEARRAY = TypeKind(115)
TypeKind.DEPENDENTSIZEDARRAY = TypeKind(116)
TypeKind.MEMBERPOINTER = TypeKind(117)
TypeKind.AUTO = TypeKind(118)
TypeKind.ELABORATED = TypeKind(119)
TypeKind.PIPE = TypeKind(120)
TypeKind.OCLIMAGE1DRO = TypeKind(121)
TypeKind.OCLIMAGE1DARRAYRO = TypeKind(122)
TypeKind.OCLIMAGE1DBUFFERRO = TypeKind(123)
TypeKind.OCLIMAGE2DRO = TypeKind(124)
TypeKind.OCLIMAGE2DARRAYRO = TypeKind(125)
TypeKind.OCLIMAGE2DDEPTHRO = TypeKind(126)
TypeKind.OCLIMAGE2DARRAYDEPTHRO = TypeKind(127)
TypeKind.OCLIMAGE2DMSAARO = TypeKind(128)
TypeKind.OCLIMAGE2DARRAYMSAARO = TypeKind(129)
TypeKind.OCLIMAGE2DMSAADEPTHRO = TypeKind(130)
TypeKind.OCLIMAGE2DARRAYMSAADEPTHRO = TypeKind(131)
TypeKind.OCLIMAGE3DRO = TypeKind(132)
TypeKind.OCLIMAGE1DWO = TypeKind(133)
TypeKind.OCLIMAGE1DARRAYWO = TypeKind(134)
TypeKind.OCLIMAGE1DBUFFERWO = TypeKind(135)
TypeKind.OCLIMAGE2DWO = TypeKind(136)
TypeKind.OCLIMAGE2DARRAYWO = TypeKind(137)
TypeKind.OCLIMAGE2DDEPTHWO = TypeKind(138)
TypeKind.OCLIMAGE2DARRAYDEPTHWO = TypeKind(139)
TypeKind.OCLIMAGE2DMSAAWO = TypeKind(140)
TypeKind.OCLIMAGE2DARRAYMSAAWO = TypeKind(141)
TypeKind.OCLIMAGE2DMSAADEPTHWO = TypeKind(142)
TypeKind.OCLIMAGE2DARRAYMSAADEPTHWO = TypeKind(143)
TypeKind.OCLIMAGE3DWO = TypeKind(144)
TypeKind.OCLIMAGE1DRW = TypeKind(145)
TypeKind.OCLIMAGE1DARRAYRW = TypeKind(146)
TypeKind.OCLIMAGE1DBUFFERRW = TypeKind(147)
TypeKind.OCLIMAGE2DRW = TypeKind(148)
TypeKind.OCLIMAGE2DARRAYRW = TypeKind(149)
TypeKind.OCLIMAGE2DDEPTHRW = TypeKind(150)
TypeKind.OCLIMAGE2DARRAYDEPTHRW = TypeKind(151)
TypeKind.OCLIMAGE2DMSAARW = TypeKind(152)
TypeKind.OCLIMAGE2DARRAYMSAARW = TypeKind(153)
TypeKind.OCLIMAGE2DMSAADEPTHRW = TypeKind(154)
TypeKind.OCLIMAGE2DARRAYMSAADEPTHRW = TypeKind(155)
TypeKind.OCLIMAGE3DRW = TypeKind(156)
TypeKind.OCLSAMPLER = TypeKind(157)
TypeKind.OCLEVENT = TypeKind(158)
TypeKind.OCLQUEUE = TypeKind(159)
TypeKind.OCLRESERVEID = TypeKind(160)