# This file is part of Pydoc.  Pydoc is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from Clang.kinds.cursor_kind import CursorKind
from Nodes.node import Node
from Nodes.method import Method
from Nodes.function import Function
from Nodes.templated import Templated


class FunctionTemplate(Templated, Function):
    kind = None

    def __init__(self, cursor, comment):
        super(FunctionTemplate, self).__init__(cursor, comment)


class MethodTemplate(Templated, Method):
    kind = None

    def __init__(self, cursor, comment):
        super(MethodTemplate, self).__init__(cursor, comment)


class FunctionTemplatePlexer(Node):
    kind = CursorKind.FUNCTION_TEMPLATE

    def __new__(cls, cursor, comment):
        if not cursor is None and (cursor.semantic_parent.kind == CursorKind.CLASS_DECL or \
                                   cursor.semantic_parent.kind == CursorKind.CLASS_TEMPLATE or \
                                   cursor.semantic_parent.kind == CursorKind.STRUCT_DECL):
            return MethodTemplate(cursor, comment)
        else:
            return FunctionTemplate(cursor, comment)

# vi:ts=4:et
