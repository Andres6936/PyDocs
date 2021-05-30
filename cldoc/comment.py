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

import bisect
import re

import utf8
from Struct import Struct


class Sorted(list):
    def __init__(self, key=None):
        if key is None:
            key = lambda x: x

        self.keys = []
        self.key = key

    def insert_bisect(self, item, bi):
        k = self.key(item)
        idx = bi(self.keys, k)

        self.keys.insert(idx, k)
        return super(Sorted, self).insert(idx, item)

    def insert(self, item):
        return self.insert_bisect(item, bisect.bisect_left)

    insert_left = insert

    def insert_right(self, item):
        return self.insert_bisect(item, bisect.bisect_right)

    def bisect(self, item, bi):
        k = self.key(item)

        return bi(self.keys, k)

    def bisect_left(self, item):
        return self.bisect(item, bisect.bisect_left)

    def bisect_right(self, item):
        return self.bisect(item, bisect.bisect_right)

    def find(self, key):
        i = bisect.bisect_left(self.keys, key)

        if i != len(self.keys) and self.keys[i] == key:
            return self[i]
        else:
            return None


class Comment(object):
    class Example(str):
        def __new__(self, s, strip=True):
            if strip:
                s = '\n'.join([self._strip_prefix(x) for x in s.split('\n')])

            return str.__new__(self, s)

        @staticmethod
        def _strip_prefix(s):
            if s.startswith('    '):
                return s[4:]
            else:
                return s

    class String(object):
        def __init__(self, s):
            self.components = [utf8.utf8(s)]

        def _utf8(self):
            return utf8.utf8("").join([utf8.utf8(x) for x in self.components])

        def __str__(self):
            return str(self._utf8())

        def __unicode__(self):
            return unicode(self._utf8())

        def __bytes__(self):
            return bytes(self._utf8())

        def __eq__(self, other):
            if isinstance(other, str):
                return str(self) == other
            elif isinstance(other, unicode):
                return unicode(self) == other
            elif isinstance(other, bytes):
                return bytes(self) == other
            else:
                return object.__cmp__(self, other)

        def __nonzero__(self):
            l = len(self.components)

            return l > 0 and (l > 1 or len(self.components[0]) > 0)

    class MarkdownCode(utf8.utf8):
        pass

    class UnresolvedReference(utf8.utf8):
        reescape = re.compile('[*_]', re.I)

        def __new__(cls, s):
            ns = Comment.UnresolvedReference.reescape.sub(lambda x: '\\' + x.group(0), s)
            ret = utf8.utf8.__new__(cls, utf8.utf8('&lt;{0}&gt;').format(utf8.utf8(ns)))

            ret.orig = s
            return ret

    redocref = re.compile('(?P<isregex>[$]?)<(?:\\[(?P<refname>[^\\]]*)\\])?(?P<ref>operator(?:>>|>|>=)|[^>\n]+)>')
    redoccode = re.compile('^    \\[code\\]\n(?P<code>(?:(?:    .*|)\n)*)', re.M)
    redocmcode = re.compile('(^ *(`{3,}|~{3,}).*?\\2)', re.M | re.S)

    def __init__(self, text, location):
        self.__dict__['docstrings'] = []
        self.__dict__['text'] = text

        self.__dict__['location'] = location
        self.__dict__['_resolved'] = False

        self.doc = text
        self.brief = ''

    def __setattr__(self, name, val):
        if not name in self.docstrings:
            self.docstrings.append(name)

        if isinstance(val, dict):
            for key in val:
                if not isinstance(val[key], Comment.String):
                    val[key] = Comment.String(val[key])
        elif not isinstance(val, Comment.String):
            val = Comment.String(val)

        self.__dict__[name] = val

    def __nonzero__(self):
        return (bool(self.brief) and not (self.brief == u'*documentation missing...*')) or (
                    bool(self.doc) and not (self.doc == u'*documentation missing...*'))

    def redoccode_split(self, doc):
        # Split on C/C++ code
        components = Comment.redoccode.split(doc)
        ret = []

        for i in range(0, len(components), 2):
            r = Comment.redocmcode.split(components[i])

            for j in range(0, len(r), 3):
                ret.append(r[j])

                if j < len(r) - 1:
                    ret.append(Comment.MarkdownCode(r[j + 1]))

            if i < len(components) - 1:
                ret.append(Comment.Example(components[i + 1]))

        return ret

    def redoc_split(self, doc):
        ret = []

        # First split examples
        components = self.redoccode_split(doc)

        for c in components:
            if isinstance(c, Comment.Example) or isinstance(c, Comment.MarkdownCode):
                ret.append((c, None, None))
            else:
                lastpos = 0

                for m in Comment.redocref.finditer(c):
                    span = m.span(0)

                    prefix = c[lastpos:span[0]]
                    lastpos = span[1]

                    ref = m.group('ref')
                    refname = m.group('refname')

                    if not refname:
                        refname = None

                    if len(m.group('isregex')) > 0:
                        ref = re.compile(ref)

                    ret.append((prefix, ref, refname))

                ret.append((c[lastpos:], None, None))

        return ret

    def resolve_refs_for_doc(self, doc, resolver, root):
        comps = self.redoc_split(utf8.utf8(doc))
        components = []

        for pair in comps:
            prefix, name, refname = pair
            components.append(prefix)

            if name is None:
                continue

            if isinstance(name, utf8.string):
                names = name.split('::')
            else:
                names = [name]

            nds = [root]

            for j in range(len(names)):
                newnds = []

                for n in nds:
                    newnds += resolver(n, names[j], j == 0)

                if len(newnds) == 0:
                    break

                nds = newnds

            if len(newnds) > 0:
                components.append((newnds, refname))
            else:
                components.append(Comment.UnresolvedReference(name))

        doc.components = components

    def resolve_refs(self, resolver, root):
        if self.__dict__['_resolved']:
            return

        self.__dict__['_resolved'] = True

        for name in self.docstrings:
            doc = getattr(self, name)

            if not doc:
                continue

            if isinstance(doc, dict):
                for key in doc:
                    if not isinstance(doc[key], Comment.String):
                        doc[key] = Comment.String(doc[key])

                    self.resolve_refs_for_doc(doc[key], resolver, root)
            else:
                self.resolve_refs_for_doc(doc, resolver, root)

    def __repr__(self) -> str:
        return self.__dict__["text"]


class RangeMap(Sorted):
    Item = Struct.define('Item', obj=None, start=0, end=0)

    def __init__(self):
        super(RangeMap, self).__init__(key=lambda x: x.start)

        self.stack = []

    def push(self, obj, start):
        self.stack.append(RangeMap.Item(obj=obj, start=start, end=start))

    def pop(self, end):
        item = self.stack.pop()
        item.end = end

        self.insert(item)

    def insert(self, item, start=None, end=None):
        if not isinstance(item, RangeMap.Item):
            item = RangeMap.Item(obj=item, start=start, end=end)

        self.insert_right(item)

    def find(self, i):
        # Finds object for which i falls in the range of that object
        idx = bisect.bisect_right(self.keys, i)

        # Go back up until falls within end
        while idx > 0:
            idx -= 1

            o = self[idx]

            if i <= o.end:
                return o.obj

        return None



# vi:ts=4:et
