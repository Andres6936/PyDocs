from clang.config import conf
from clang.kinds.base_enumeration import BaseEnumeration


class CursorKind(BaseEnumeration):
    """
    A CursorKind describes the kind of entity that a cursor points to.
    """

    # The required BaseEnumeration declarations.
    _kinds = []
    _name_map = None

    @staticmethod
    def get_all_kinds():
        """Return all CursorKind enumeration instances."""
        return [x for x in CursorKind._kinds if not x is None]

    def is_declaration(self):
        """Test if this is a declaration kind."""
        return conf.lib.clang_isDeclaration(self)

    def is_reference(self):
        """Test if this is a reference kind."""
        return conf.lib.clang_isReference(self)

    def is_expression(self):
        """Test if this is an expression kind."""
        return conf.lib.clang_isExpression(self)

    def is_statement(self):
        """Test if this is a statement kind."""
        return conf.lib.clang_isStatement(self)

    def is_attribute(self):
        """Test if this is an attribute kind."""
        return conf.lib.clang_isAttribute(self)

    def is_invalid(self):
        """Test if this is an invalid kind."""
        return conf.lib.clang_isInvalid(self)

    def is_translation_unit(self):
        """Test if this is a translation unit kind."""
        return conf.lib.clang_isTranslationUnit(self)

    def is_preprocessing(self):
        """Test if this is a preprocessing kind."""
        return conf.lib.clang_isPreprocessing(self)

    def is_unexposed(self):
        """Test if this is an unexposed kind."""
        return conf.lib.clang_isUnexposed(self)

    def __repr__(self):
        return 'CursorKind.{}'.format(self.name)


###
# Declaration Kinds

# A declaration whose specific kind is not exposed via this interface.
#
# Unexposed declarations have the same operations as any other kind of
# declaration; one can extract their location information, spelling, find their
# definitions, etc. However, the specific kind of the declaration is not
# reported.
CursorKind.UNEXPOSED_DECL = CursorKind(1)

# A C or C++ struct.
CursorKind.STRUCT_DECL = CursorKind(2)

# A C or C++ union.
CursorKind.UNION_DECL = CursorKind(3)

# A C++ class.
CursorKind.CLASS_DECL = CursorKind(4)

# An enumeration.
CursorKind.ENUM_DECL = CursorKind(5)

# A field (in C) or non-static data member (in C++) in a struct, union, or C++
# class.
CursorKind.FIELD_DECL = CursorKind(6)

# An enumerator constant.
CursorKind.ENUM_CONSTANT_DECL = CursorKind(7)

# A function.
CursorKind.FUNCTION_DECL = CursorKind(8)

# A variable.
CursorKind.VAR_DECL = CursorKind(9)

# A function or method parameter.
CursorKind.PARM_DECL = CursorKind(10)

# An Objective-C @interface.
CursorKind.OBJC_INTERFACE_DECL = CursorKind(11)

# An Objective-C @interface for a category.
CursorKind.OBJC_CATEGORY_DECL = CursorKind(12)

# An Objective-C @protocol declaration.
CursorKind.OBJC_PROTOCOL_DECL = CursorKind(13)

# An Objective-C @property declaration.
CursorKind.OBJC_PROPERTY_DECL = CursorKind(14)

# An Objective-C instance variable.
CursorKind.OBJC_IVAR_DECL = CursorKind(15)

# An Objective-C instance method.
CursorKind.OBJC_INSTANCE_METHOD_DECL = CursorKind(16)

# An Objective-C class method.
CursorKind.OBJC_CLASS_METHOD_DECL = CursorKind(17)

# An Objective-C @implementation.
CursorKind.OBJC_IMPLEMENTATION_DECL = CursorKind(18)

# An Objective-C @implementation for a category.
CursorKind.OBJC_CATEGORY_IMPL_DECL = CursorKind(19)

# A typedef.
CursorKind.TYPEDEF_DECL = CursorKind(20)

# A C++ class method.
CursorKind.CXX_METHOD = CursorKind(21)

# A C++ namespace.
CursorKind.NAMESPACE = CursorKind(22)

# A linkage specification, e.g. 'extern "C"'.
CursorKind.LINKAGE_SPEC = CursorKind(23)

# A C++ constructor.
CursorKind.CONSTRUCTOR = CursorKind(24)

# A C++ destructor.
CursorKind.DESTRUCTOR = CursorKind(25)

# A C++ conversion function.
CursorKind.CONVERSION_FUNCTION = CursorKind(26)

# A C++ template type parameter
CursorKind.TEMPLATE_TYPE_PARAMETER = CursorKind(27)

# A C++ non-type template parameter.
CursorKind.TEMPLATE_NON_TYPE_PARAMETER = CursorKind(28)

# A C++ template template parameter.
CursorKind.TEMPLATE_TEMPLATE_PARAMETER = CursorKind(29)

# A C++ function template.
CursorKind.FUNCTION_TEMPLATE = CursorKind(30)

# A C++ class template.
CursorKind.CLASS_TEMPLATE = CursorKind(31)

# A C++ class template partial specialization.
CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION = CursorKind(32)

# A C++ namespace alias declaration.
CursorKind.NAMESPACE_ALIAS = CursorKind(33)

# A C++ using directive
CursorKind.USING_DIRECTIVE = CursorKind(34)

# A C++ using declaration
CursorKind.USING_DECLARATION = CursorKind(35)

# A Type alias decl.
CursorKind.TYPE_ALIAS_DECL = CursorKind(36)

# A Objective-C synthesize decl
CursorKind.OBJC_SYNTHESIZE_DECL = CursorKind(37)

# A Objective-C dynamic decl
CursorKind.OBJC_DYNAMIC_DECL = CursorKind(38)

# A C++ access specifier decl.
CursorKind.CXX_ACCESS_SPEC_DECL = CursorKind(39)

###
# Reference Kinds

CursorKind.OBJC_SUPER_CLASS_REF = CursorKind(40)
CursorKind.OBJC_PROTOCOL_REF = CursorKind(41)
CursorKind.OBJC_CLASS_REF = CursorKind(42)

# A reference to a type declaration.
#
# A type reference occurs anywhere where a type is named but not
# declared. For example, given:
#   typedef unsigned size_type;
#   size_type size;
#
# The typedef is a declaration of size_type (CXCursor_TypedefDecl),
# while the type of the variable "size" is referenced. The cursor
# referenced by the type of size is the typedef for size_type.
CursorKind.TYPE_REF = CursorKind(43)
CursorKind.CXX_BASE_SPECIFIER = CursorKind(44)

# A reference to a class template, function template, template
# template parameter, or class template partial specialization.
CursorKind.TEMPLATE_REF = CursorKind(45)

# A reference to a namespace or namepsace alias.
CursorKind.NAMESPACE_REF = CursorKind(46)

# A reference to a member of a struct, union, or class that occurs in
# some non-expression context, e.g., a designated initializer.
CursorKind.MEMBER_REF = CursorKind(47)

# A reference to a labeled statement.
CursorKind.LABEL_REF = CursorKind(48)

# A reference to a set of overloaded functions or function templates
# that has not yet been resolved to a specific function or function template.
CursorKind.OVERLOADED_DECL_REF = CursorKind(49)

# A reference to a variable that occurs in some non-expression
# context, e.g., a C++ lambda capture list.
CursorKind.VARIABLE_REF = CursorKind(50)

###
# Invalid/Error Kinds

CursorKind.INVALID_FILE = CursorKind(70)
CursorKind.NO_DECL_FOUND = CursorKind(71)
CursorKind.NOT_IMPLEMENTED = CursorKind(72)
CursorKind.INVALID_CODE = CursorKind(73)

###
# Expression Kinds

# An expression whose specific kind is not exposed via this interface.
#
# Unexposed expressions have the same operations as any other kind of
# expression; one can extract their location information, spelling, children,
# etc. However, the specific kind of the expression is not reported.
CursorKind.UNEXPOSED_EXPR = CursorKind(100)

# An expression that refers to some value declaration, such as a function,
# varible, or enumerator.
CursorKind.DECL_REF_EXPR = CursorKind(101)

# An expression that refers to a member of a struct, union, class, Objective-C
# class, etc.
CursorKind.MEMBER_REF_EXPR = CursorKind(102)

# An expression that calls a function.
CursorKind.CALL_EXPR = CursorKind(103)

# An expression that sends a message to an Objective-C object or class.
CursorKind.OBJC_MESSAGE_EXPR = CursorKind(104)

# An expression that represents a block literal.
CursorKind.BLOCK_EXPR = CursorKind(105)

# An integer literal.
CursorKind.INTEGER_LITERAL = CursorKind(106)

# A floating point number literal.
CursorKind.FLOATING_LITERAL = CursorKind(107)

# An imaginary number literal.
CursorKind.IMAGINARY_LITERAL = CursorKind(108)

# A string literal.
CursorKind.STRING_LITERAL = CursorKind(109)

# A character literal.
CursorKind.CHARACTER_LITERAL = CursorKind(110)

# A parenthesized expression, e.g. "(1)".
#
# This AST node is only formed if full location information is requested.
CursorKind.PAREN_EXPR = CursorKind(111)

# This represents the unary-expression's (except sizeof and
# alignof).
CursorKind.UNARY_OPERATOR = CursorKind(112)

# [C99 6.5.2.1] Array Subscripting.
CursorKind.ARRAY_SUBSCRIPT_EXPR = CursorKind(113)

# A builtin binary operation expression such as "x + y" or
# "x <= y".
CursorKind.BINARY_OPERATOR = CursorKind(114)

# Compound assignment such as "+=".
CursorKind.COMPOUND_ASSIGNMENT_OPERATOR = CursorKind(115)

# The ?: ternary operator.
CursorKind.CONDITIONAL_OPERATOR = CursorKind(116)

# An explicit cast in C (C99 6.5.4) or a C-style cast in C++
# (C++ [expr.cast]), which uses the syntax (Type)expr.
#
# For example: (int)f.
CursorKind.CSTYLE_CAST_EXPR = CursorKind(117)

# [C99 6.5.2.5]
CursorKind.COMPOUND_LITERAL_EXPR = CursorKind(118)

# Describes an C or C++ initializer list.
CursorKind.INIT_LIST_EXPR = CursorKind(119)

# The GNU address of label extension, representing &&label.
CursorKind.ADDR_LABEL_EXPR = CursorKind(120)

# This is the GNU Statement Expression extension: ({int X=4; X;})
CursorKind.StmtExpr = CursorKind(121)

# Represents a C11 generic selection.
CursorKind.GENERIC_SELECTION_EXPR = CursorKind(122)

# Implements the GNU __null extension, which is a name for a null
# pointer constant that has integral type (e.g., int or long) and is the same
# size and alignment as a pointer.
#
# The __null extension is typically only used by system headers, which define
# NULL as __null in C++ rather than using 0 (which is an integer that may not
# match the size of a pointer).
CursorKind.GNU_NULL_EXPR = CursorKind(123)

# C++'s static_cast<> expression.
CursorKind.CXX_STATIC_CAST_EXPR = CursorKind(124)

# C++'s dynamic_cast<> expression.
CursorKind.CXX_DYNAMIC_CAST_EXPR = CursorKind(125)

# C++'s reinterpret_cast<> expression.
CursorKind.CXX_REINTERPRET_CAST_EXPR = CursorKind(126)

# C++'s const_cast<> expression.
CursorKind.CXX_CONST_CAST_EXPR = CursorKind(127)

# Represents an explicit C++ type conversion that uses "functional"
# notion (C++ [expr.type.conv]).
#
# Example:
# \code
#   x = int(0.5);
# \endcode
CursorKind.CXX_FUNCTIONAL_CAST_EXPR = CursorKind(128)

# A C++ typeid expression (C++ [expr.typeid]).
CursorKind.CXX_TYPEID_EXPR = CursorKind(129)

# [C++ 2.13.5] C++ Boolean Literal.
CursorKind.CXX_BOOL_LITERAL_EXPR = CursorKind(130)

# [C++0x 2.14.7] C++ Pointer Literal.
CursorKind.CXX_NULL_PTR_LITERAL_EXPR = CursorKind(131)

# Represents the "this" expression in C++
CursorKind.CXX_THIS_EXPR = CursorKind(132)

# [C++ 15] C++ Throw Expression.
#
# This handles 'throw' and 'throw' assignment-expression. When
# assignment-expression isn't present, Op will be null.
CursorKind.CXX_THROW_EXPR = CursorKind(133)

# A new expression for memory allocation and constructor calls, e.g:
# "new CXXNewExpr(foo)".
CursorKind.CXX_NEW_EXPR = CursorKind(134)

# A delete expression for memory deallocation and destructor calls,
# e.g. "delete[] pArray".
CursorKind.CXX_DELETE_EXPR = CursorKind(135)

# Represents a unary expression.
CursorKind.CXX_UNARY_EXPR = CursorKind(136)

# ObjCStringLiteral, used for Objective-C string literals i.e. "foo".
CursorKind.OBJC_STRING_LITERAL = CursorKind(137)

# ObjCEncodeExpr, used for in Objective-C.
CursorKind.OBJC_ENCODE_EXPR = CursorKind(138)

# ObjCSelectorExpr used for in Objective-C.
CursorKind.OBJC_SELECTOR_EXPR = CursorKind(139)

# Objective-C's protocol expression.
CursorKind.OBJC_PROTOCOL_EXPR = CursorKind(140)

# An Objective-C "bridged" cast expression, which casts between
# Objective-C pointers and C pointers, transferring ownership in the process.
#
# \code
#   NSString *str = (__bridge_transfer NSString *)CFCreateString();
# \endcode
CursorKind.OBJC_BRIDGE_CAST_EXPR = CursorKind(141)

# Represents a C++0x pack expansion that produces a sequence of
# expressions.
#
# A pack expansion expression contains a pattern (which itself is an
# expression) followed by an ellipsis. For example:
CursorKind.PACK_EXPANSION_EXPR = CursorKind(142)

# Represents an expression that computes the length of a parameter
# pack.
CursorKind.SIZE_OF_PACK_EXPR = CursorKind(143)

# Represents a C++ lambda expression that produces a local function
# object.
#
#  \code
#  void abssort(float *x, unsigned N) {
#    std::sort(x, x + N,
#              [](float a, float b) {
#                return std::abs(a) < std::abs(b);
#              });
#  }
#  \endcode
CursorKind.LAMBDA_EXPR = CursorKind(144)

# Objective-c Boolean Literal.
CursorKind.OBJ_BOOL_LITERAL_EXPR = CursorKind(145)

# Represents the "self" expression in a ObjC method.
CursorKind.OBJ_SELF_EXPR = CursorKind(146)

# OpenMP 4.0 [2.4, Array Section].
CursorKind.OMP_ARRAY_SECTION_EXPR = CursorKind(147)

# Represents an @available(...) check.
CursorKind.OBJC_AVAILABILITY_CHECK_EXPR = CursorKind(148)

# A statement whose specific kind is not exposed via this interface.
#
# Unexposed statements have the same operations as any other kind of statement;
# one can extract their location information, spelling, children, etc. However,
# the specific kind of the statement is not reported.
CursorKind.UNEXPOSED_STMT = CursorKind(200)

# A labelled statement in a function.
CursorKind.LABEL_STMT = CursorKind(201)

# A compound statement
CursorKind.COMPOUND_STMT = CursorKind(202)

# A case statement.
CursorKind.CASE_STMT = CursorKind(203)

# A default statement.
CursorKind.DEFAULT_STMT = CursorKind(204)

# An if statement.
CursorKind.IF_STMT = CursorKind(205)

# A switch statement.
CursorKind.SWITCH_STMT = CursorKind(206)

# A while statement.
CursorKind.WHILE_STMT = CursorKind(207)

# A do statement.
CursorKind.DO_STMT = CursorKind(208)

# A for statement.
CursorKind.FOR_STMT = CursorKind(209)

# A goto statement.
CursorKind.GOTO_STMT = CursorKind(210)

# An indirect goto statement.
CursorKind.INDIRECT_GOTO_STMT = CursorKind(211)

# A continue statement.
CursorKind.CONTINUE_STMT = CursorKind(212)

# A break statement.
CursorKind.BREAK_STMT = CursorKind(213)

# A return statement.
CursorKind.RETURN_STMT = CursorKind(214)

# A GNU-style inline assembler statement.
CursorKind.ASM_STMT = CursorKind(215)

# Objective-C's overall @try-@catch-@finally statement.
CursorKind.OBJC_AT_TRY_STMT = CursorKind(216)

# Objective-C's @catch statement.
CursorKind.OBJC_AT_CATCH_STMT = CursorKind(217)

# Objective-C's @finally statement.
CursorKind.OBJC_AT_FINALLY_STMT = CursorKind(218)

# Objective-C's @throw statement.
CursorKind.OBJC_AT_THROW_STMT = CursorKind(219)

# Objective-C's @synchronized statement.
CursorKind.OBJC_AT_SYNCHRONIZED_STMT = CursorKind(220)

# Objective-C's autorealease pool statement.
CursorKind.OBJC_AUTORELEASE_POOL_STMT = CursorKind(221)

# Objective-C's for collection statement.
CursorKind.OBJC_FOR_COLLECTION_STMT = CursorKind(222)

# C++'s catch statement.
CursorKind.CXX_CATCH_STMT = CursorKind(223)

# C++'s try statement.
CursorKind.CXX_TRY_STMT = CursorKind(224)

# C++'s for (* : *) statement.
CursorKind.CXX_FOR_RANGE_STMT = CursorKind(225)

# Windows Structured Exception Handling's try statement.
CursorKind.SEH_TRY_STMT = CursorKind(226)

# Windows Structured Exception Handling's except statement.
CursorKind.SEH_EXCEPT_STMT = CursorKind(227)

# Windows Structured Exception Handling's finally statement.
CursorKind.SEH_FINALLY_STMT = CursorKind(228)

# A MS inline assembly statement extension.
CursorKind.MS_ASM_STMT = CursorKind(229)

# The null statement.
CursorKind.NULL_STMT = CursorKind(230)

# Adaptor class for mixing declarations with statements and expressions.
CursorKind.DECL_STMT = CursorKind(231)

# OpenMP parallel directive.
CursorKind.OMP_PARALLEL_DIRECTIVE = CursorKind(232)

# OpenMP SIMD directive.
CursorKind.OMP_SIMD_DIRECTIVE = CursorKind(233)

# OpenMP for directive.
CursorKind.OMP_FOR_DIRECTIVE = CursorKind(234)

# OpenMP sections directive.
CursorKind.OMP_SECTIONS_DIRECTIVE = CursorKind(235)

# OpenMP section directive.
CursorKind.OMP_SECTION_DIRECTIVE = CursorKind(236)

# OpenMP single directive.
CursorKind.OMP_SINGLE_DIRECTIVE = CursorKind(237)

# OpenMP parallel for directive.
CursorKind.OMP_PARALLEL_FOR_DIRECTIVE = CursorKind(238)

# OpenMP parallel sections directive.
CursorKind.OMP_PARALLEL_SECTIONS_DIRECTIVE = CursorKind(239)

# OpenMP task directive.
CursorKind.OMP_TASK_DIRECTIVE = CursorKind(240)

# OpenMP master directive.
CursorKind.OMP_MASTER_DIRECTIVE = CursorKind(241)

# OpenMP critical directive.
CursorKind.OMP_CRITICAL_DIRECTIVE = CursorKind(242)

# OpenMP taskyield directive.
CursorKind.OMP_TASKYIELD_DIRECTIVE = CursorKind(243)

# OpenMP barrier directive.
CursorKind.OMP_BARRIER_DIRECTIVE = CursorKind(244)

# OpenMP taskwait directive.
CursorKind.OMP_TASKWAIT_DIRECTIVE = CursorKind(245)

# OpenMP flush directive.
CursorKind.OMP_FLUSH_DIRECTIVE = CursorKind(246)

# Windows Structured Exception Handling's leave statement.
CursorKind.SEH_LEAVE_STMT = CursorKind(247)

# OpenMP ordered directive.
CursorKind.OMP_ORDERED_DIRECTIVE = CursorKind(248)

# OpenMP atomic directive.
CursorKind.OMP_ATOMIC_DIRECTIVE = CursorKind(249)

# OpenMP for SIMD directive.
CursorKind.OMP_FOR_SIMD_DIRECTIVE = CursorKind(250)

# OpenMP parallel for SIMD directive.
CursorKind.OMP_PARALLELFORSIMD_DIRECTIVE = CursorKind(251)

# OpenMP target directive.
CursorKind.OMP_TARGET_DIRECTIVE = CursorKind(252)

# OpenMP teams directive.
CursorKind.OMP_TEAMS_DIRECTIVE = CursorKind(253)

# OpenMP taskgroup directive.
CursorKind.OMP_TASKGROUP_DIRECTIVE = CursorKind(254)

# OpenMP cancellation point directive.
CursorKind.OMP_CANCELLATION_POINT_DIRECTIVE = CursorKind(255)

# OpenMP cancel directive.
CursorKind.OMP_CANCEL_DIRECTIVE = CursorKind(256)

# OpenMP target data directive.
CursorKind.OMP_TARGET_DATA_DIRECTIVE = CursorKind(257)

# OpenMP taskloop directive.
CursorKind.OMP_TASK_LOOP_DIRECTIVE = CursorKind(258)

# OpenMP taskloop simd directive.
CursorKind.OMP_TASK_LOOP_SIMD_DIRECTIVE = CursorKind(259)

# OpenMP distribute directive.
CursorKind.OMP_DISTRIBUTE_DIRECTIVE = CursorKind(260)

# OpenMP target enter data directive.
CursorKind.OMP_TARGET_ENTER_DATA_DIRECTIVE = CursorKind(261)

# OpenMP target exit data directive.
CursorKind.OMP_TARGET_EXIT_DATA_DIRECTIVE = CursorKind(262)

# OpenMP target parallel directive.
CursorKind.OMP_TARGET_PARALLEL_DIRECTIVE = CursorKind(263)

# OpenMP target parallel for directive.
CursorKind.OMP_TARGET_PARALLELFOR_DIRECTIVE = CursorKind(264)

# OpenMP target update directive.
CursorKind.OMP_TARGET_UPDATE_DIRECTIVE = CursorKind(265)

# OpenMP distribute parallel for directive.
CursorKind.OMP_DISTRIBUTE_PARALLELFOR_DIRECTIVE = CursorKind(266)

# OpenMP distribute parallel for simd directive.
CursorKind.OMP_DISTRIBUTE_PARALLEL_FOR_SIMD_DIRECTIVE = CursorKind(267)

# OpenMP distribute simd directive.
CursorKind.OMP_DISTRIBUTE_SIMD_DIRECTIVE = CursorKind(268)

# OpenMP target parallel for simd directive.
CursorKind.OMP_TARGET_PARALLEL_FOR_SIMD_DIRECTIVE = CursorKind(269)

# OpenMP target simd directive.
CursorKind.OMP_TARGET_SIMD_DIRECTIVE = CursorKind(270)

# OpenMP teams distribute directive.
CursorKind.OMP_TEAMS_DISTRIBUTE_DIRECTIVE = CursorKind(271)

###
# Other Kinds

# Cursor that represents the translation unit itself.
#
# The translation unit cursor exists primarily to act as the root cursor for
# traversing the contents of a translation unit.
CursorKind.TRANSLATION_UNIT = CursorKind(300)

###
# Attributes

# An attribute whoe specific kind is note exposed via this interface
CursorKind.UNEXPOSED_ATTR = CursorKind(400)

CursorKind.IB_ACTION_ATTR = CursorKind(401)
CursorKind.IB_OUTLET_ATTR = CursorKind(402)
CursorKind.IB_OUTLET_COLLECTION_ATTR = CursorKind(403)

CursorKind.CXX_FINAL_ATTR = CursorKind(404)
CursorKind.CXX_OVERRIDE_ATTR = CursorKind(405)
CursorKind.ANNOTATE_ATTR = CursorKind(406)
CursorKind.ASM_LABEL_ATTR = CursorKind(407)
CursorKind.PACKED_ATTR = CursorKind(408)
CursorKind.PURE_ATTR = CursorKind(409)
CursorKind.CONST_ATTR = CursorKind(410)
CursorKind.NODUPLICATE_ATTR = CursorKind(411)
CursorKind.CUDACONSTANT_ATTR = CursorKind(412)
CursorKind.CUDADEVICE_ATTR = CursorKind(413)
CursorKind.CUDAGLOBAL_ATTR = CursorKind(414)
CursorKind.CUDAHOST_ATTR = CursorKind(415)
CursorKind.CUDASHARED_ATTR = CursorKind(416)

CursorKind.VISIBILITY_ATTR = CursorKind(417)

CursorKind.DLLEXPORT_ATTR = CursorKind(418)
CursorKind.DLLIMPORT_ATTR = CursorKind(419)

###
# Preprocessing
CursorKind.PREPROCESSING_DIRECTIVE = CursorKind(500)
CursorKind.MACRO_DEFINITION = CursorKind(501)
CursorKind.MACRO_INSTANTIATION = CursorKind(502)
CursorKind.INCLUSION_DIRECTIVE = CursorKind(503)

###
# Extra declaration

# A module import declaration.
CursorKind.MODULE_IMPORT_DECL = CursorKind(600)
# A type alias template declaration
CursorKind.TYPE_ALIAS_TEMPLATE_DECL = CursorKind(601)
# A static_assert or _Static_assert node
CursorKind.STATIC_ASSERT = CursorKind(602)
# A friend declaration
CursorKind.FRIEND_DECL = CursorKind(603)

# A code completion overload candidate.
CursorKind.OVERLOAD_CANDIDATE = CursorKind(700)