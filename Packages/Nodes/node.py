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
import functools

from Clang.kinds.access_specifier import AccessSpecifier

from Pydoc import utf8
from Pydoc.util.cmp import cmp

import re

from Pydoc.comments.parser import Parser


class Node(object):
    class SortId:
        CATEGORY = 0
        NAMESPACE = 1
        TEMPLATETYPEPARAMETER = 2
        CLASS = 3
        ENUM = 4
        ENUMVALUE = 5
        FIELD = 6
        TYPEDEF = 7
        CONSTRUCTOR = 8
        DESTRUCTOR = 9
        METHOD = 10
        FUNCTION = 11

    def __init__(self, cursor, comment):
        self.cursor = cursor
        self._comment = comment
        self.children = []
        self.parent = None
        self.access = AccessSpecifier.PUBLIC
        self._comment_locations = []
        self._refs = []
        self.sort_index = 0
        self.num_anon = 0
        self.anonymous_id = 0
        self._refid = None

        self.sortid = 0
        cls = self.__class__

        while cls.__name__ != 'object':
            nm = cls.__name__.upper()

            if hasattr(Node.SortId, nm):
                self.sortid = getattr(Node.SortId, nm)
                break
            else:
                cls = cls.__base__

        self.process_children = False

        if self._comment:
            self.parse_comment()

    @property
    def refid(self):
        if not self._refid is None:
            return self._refid
        else:
            return self.qid

    @property
    def is_anonymous(self):
        return False

    def qid_from_to(self, nq, mq):
        # Find the minimal required typename from the perspective of <node>
        # to reach our type
        lnq = nq.split('::')
        lmq = mq.split('::')

        if nq == mq:
            return lmq[-1]

        for i in range(min(len(lnq), len(lmq))):
            if lnq[i] != lmq[i]:
                return "::".join(lmq[i:])

        if len(lnq) > len(lmq):
            return lmq[-1]
        else:
            return "::".join(lmq[len(lnq):])

    def qid_from(self, qid):
        return self.qid_from_to(self.qid, qid)

    def qid_to(self, qid):
        return self.qid_from_to(qid, self.qid)

    def semantic_path_until(self, parent):
        ret = []

        if parent == self:
            return [self]

        p = self

        while (not p is None) and p != parent:
            ret.insert(0, p)

            sp = p.semantic_parent
            p = p.parent

            while p != sp:
                if p == parent:
                    return ret

                p = p.parent

        return ret

    @property
    def is_unlabeled(self):
        return False

    def qlbl_from(self, other):
        p = other.semantic_path_until(self)

        i = 0

        while i < (len(p) - 1) and p[i].is_unlabeled:
            i += 1

        return utf8.utf8('::').join(filter(lambda x: x, [q.name for q in p[i:]]))

    def qlbl_to(self, other):
        return other.qlbl_from(self)

    def add_ref(self, cursor):
        self._refs.append(cursor)
        self.add_comment_location(cursor.extent.start)

    def add_comment_location(self, location):
        self._comment_locations.append(location)

    @property
    def comment_locations(self):
        if self.cursor:
            ext = self.cursor.extent

            if not ext is None:
                yield ext.start

        for loc in self._comment_locations:
            yield loc

    def parse_comment(self):
        # Just extract brief and doc
        self._parsed_comment = Parser.parse(self._comment.text)

        if len(self._parsed_comment.brief) > 0:
            self._comment.brief = self._parsed_comment.brief
            self._comment.doc = self._parsed_comment.body

    @property
    def natural_sort_name(self):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', self.name)]

    def compare_same(self, other):
        if self.name and other.name:
            return cmp(self.natural_sort_name, other.natural_sort_name)
        else:
            return 0

    def compare_sort(self, other):
        ret = cmp(self.access.value, other.access.value)

        if ret == 0:
            ret = cmp(self.sortid, other.sortid)

        if ret == 0:
            ret = self.compare_same(other)

        return ret

    @property
    def resolve_nodes(self):
        for child in self.children:
            yield child

            if child.is_anonymous:
                for ev in child.children:
                    yield ev

    @property
    def name(self):
        if self.cursor is None:
            ret = ''
        else:
            ret = self.cursor.spelling

        if ret == '' and self.anonymous_id > 0:
            return '(anonymous::' + str(self.anonymous_id) + ')'
        else:
            return ret

    def descendants(self):
        for child in self.children:
            yield child

            for d in child.descendants():
                yield d

    def sorted_children(self):
        ret = list(self.children)
        ret.sort(key=functools.cmp_to_key(lambda x, y: x.compare_sort(y)))

        return ret

    @property
    def semantic_parent(self):
        parent = self.parent

        while (not parent is None) and parent.is_anonymous:
            parent = parent.parent

        return parent

    @property
    def qid(self):
        meid = self.name

        parent = self.semantic_parent

        if not parent:
            return meid
        else:
            q = parent.qid

            if not q:
                return meid

            if not meid:
                return q

            return q + '::' + meid

    @property
    def comment(self):
        return self._comment

    @property
    def props(self):
        ret = {
            'id': self.qid,
            'name': self.name,
        }

        if self.is_anonymous:
            ret['anonymous'] = 'yes'

        if self.access == AccessSpecifier.PROTECTED:
            ret['access'] = 'protected'
        elif self.access == AccessSpecifier.PRIVATE:
            ret['access'] = 'private'

        return ret

    @property
    def classname(self):
        return self.__class__.__name__.lower()

    def append(self, child):
        child.sort_index = len(self.children)
        self.children.append(child)
        child.parent = self

        if not child.name:
            self.num_anon += 1
            child.anonymous_id = self.num_anon

    def visit(self, cursor, citer):
        return None

    def merge_comment(self, comment, override=False):
        if not comment:
            return

        if not override and self._comment:
            return

        self._comment = comment
        self.parse_comment()

    @staticmethod
    def _subclasses(cls):
        for c in cls.__subclasses__():
            yield c

            for cc in Node._subclasses(c):
                yield cc

    @staticmethod
    def subclasses():
        return Node._subclasses(Node)

    @property
    def force_page(self):
        return False

# vi:ts=4:et
