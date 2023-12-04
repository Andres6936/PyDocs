# This file is part of cldoc.  cldoc is free software: you can
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
from Clang.utility.token_kind import TokenKind
from Nodes.node import Node


class Enum(Node):
    kind = CursorKind.ENUM_DECL

    def __init__(self, cursor, comment):
        Node.__init__(self, cursor, comment)

        self.typedef = None
        self.process_children = True
        self.isclass = False

        if hasattr(self.cursor, 'get_tokens'):
            try:
                tokens = self.cursor.get_tokens()
                next(tokens)

                tt = next(tokens)

                if tt.kind == TokenKind.KEYWORD and tt.spelling == 'class':
                    self.isclass = True
            except StopIteration:
                pass

    @property
    def is_anonymous(self):
        return not self.isclass

    @property
    def comment(self):
        ret = Node.comment.fget(self)

        if not ret and self.typedef:
            ret = self.typedef.comment

        return ret

    @property
    def name(self):
        if not self.typedef is None:
            # The name is really the one of the typedef
            return self.typedef.name
        else:
            return Node.name.fget(self)

    def sorted_children(self):
        return list(self.children)

# vi:ts=4:et
