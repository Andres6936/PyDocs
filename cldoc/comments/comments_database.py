import os
import re
import sys

from clang.objects.translation_unit import TranslationUnit
from clang.utility.token_kind import TokenKind
from comment import RangeMap, Comment
from comments.sorted import Sorted


class CommentsDatabase:
    cldoc_instrre = re.compile('^cldoc:([a-zA-Z_-]+)(\(([^\)]*)\))?')

    def __init__(self, filename: str, tu: TranslationUnit):
        self.filename: str = filename

        self.categories: RangeMap = RangeMap()
        self.comments: Sorted = Sorted(key=lambda x: x.location.offset)

        self.extract(filename, tu)

    def parse_cldoc_instruction(self, token, s):
        m = CommentsDatabase.cldoc_instrre.match(s)

        if not m:
            return False

        func = m.group(1)
        args = m.group(3)

        if args:
            args = [x.strip() for x in args.split(",")]
        else:
            args = []

        name = 'cldoc_instruction_{0}'.format(func.replace('-', '_'))

        if hasattr(self, name):
            getattr(self, name)(token, args)
        else:
            sys.stderr.write('Invalid cldoc instruction: {0}\n'.format(func))
            sys.exit(1)

        return True

    @property
    def category_names(self):
        for item in self.categories:
            yield item.obj

    def location_to_str(self, loc):
        return '{0}:{1}:{2}'.format(loc.file.name, loc.line, loc.column)

    def cldoc_instruction_begin_category(self, token, args):
        if len(args) != 1:
            sys.stderr.write('No category name specified (at {0})\n'.format(self.location_to_str(token.location)))

            sys.exit(1)

        category = args[0]
        self.categories.push(category, token.location.offset)

    def cldoc_instruction_end_category(self, token, args):
        if len(self.categories.stack) == 0:
            sys.stderr.write('Failed to end cldoc category: no category to end (at {0})\n'.format(
                self.location_to_str(token.location)))

            sys.exit(1)

        last = self.categories.stack[-1]

        if len(args) == 1 and last.obj != args[0]:
            sys.stderr.write(
                'Failed to end cldoc category: current category is `{0}\', not `{1}\' (at {2})\n'.format(last.obj,
                                                                                                         args[0],
                                                                                                         self.location_to_str(
                                                                                                             token.location)))

            sys.exit(1)

        self.categories.pop(token.extent.end.offset)

    def lookup_category(self, location):
        if location.file.name != self.filename:
            return None

        return self.categories.find(location.offset)

    def lookup(self, location):
        if location.file.name != self.filename:
            return None

        return self.comments.find(location.offset)

    def extract(self, filename: str, tu: TranslationUnit):
        """
        extract extracts comments from a translation unit for a given file by
        iterating over all the tokens in the TU, locating the COMMENT tokens and
        finding out to which cursors the comments semantically belong.
        """
        # The variable st_size is: Size of the file in bytes, if it is a
        # regular file or a symbolic link. The size of a symbolic link is the
        # length of the pathname it contains, without a terminating null byte.
        it = tu.get_tokens(extent=tu.get_extent(filename, (0, os.stat(filename).st_size)))

        while True:
            try:
                self.extract_loop(it)
            except StopIteration:
                break

    def extract_one(self, token, s):
        # Parse special cldoc:<instruction>() comments for instructions
        if self.parse_cldoc_instruction(token, s.strip()):
            return

        comment = Comment(s, token.location)
        self.comments.insert(comment)

    def extract_loop(self, iter):
        token = next(iter)

        # Skip until comment found
        while token.kind != TokenKind.COMMENT:
            token = next(iter)

        comments = []
        prev = None

        # Concatenate individual comments together, but only if they are strictly
        # adjacent
        while token.kind == TokenKind.COMMENT:
            cleaned = self.clean(token)

            # Process instructions directly, now
            if (not cleaned is None) and (not CommentsDatabase.cldoc_instrre.match(cleaned) is None):
                comments = [cleaned]
                break

            # Check adjacency
            if not prev is None and prev.extent.end.line + 1 < token.extent.start.line:
                # Empty previous comment
                comments = []

            if not cleaned is None:
                comments.append(cleaned)

            prev = token
            token = next(iter)

        if len(comments) > 0:
            self.extract_one(token, "\n".join(comments))

    def clean(self, token):
        prelen = token.extent.start.column - 1
        comment = token.spelling.strip()

        if comment.startswith('//'):
            if len(comment) > 2 and comment[2] == '-':
                return None

            return comment[2:].strip()
        elif comment.startswith('/*') and comment.endswith('*/'):
            if comment[2] == '-':
                return None

            lines = comment[2:-2].splitlines()

            if len(lines) == 1 and len(lines[0]) > 0 and lines[0][0] == ' ':
                return lines[0][1:].rstrip()

            retl = []

            for line in lines:
                if prelen == 0 or line[0:prelen].isspace():
                    line = line[prelen:].rstrip()

                    if line.startswith(' *') or line.startswith('  '):
                        line = line[2:]

                        if len(line) > 0 and line[0] == ' ':
                            line = line[1:]

                retl.append(line)

            return "\n".join(retl)
        else:
            return comment

    def __repr__(self) -> str:
        return "Comments: {}".format(len(self.comments))
