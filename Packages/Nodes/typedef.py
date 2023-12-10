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
from Nodes.ctype import Type


class Typedef(Node):
    kind = CursorKind.TYPEDEF_DECL

    def __init__(self, cursor, comment):
        Node.__init__(self, cursor, comment)

        children = [child for child in cursor.get_children()]

        if len(children) == 1 and children[0].kind == CursorKind.TYPE_REF:
            typecursor = children[0]
        else:
            self.process_children = True
            typecursor = cursor

        self.type = Type(cursor.underlying_typedef_type, typecursor)

# vi:ts=4:et
