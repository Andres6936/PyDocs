import unittest

from clang.objects.index import Index
from clang.objects.translation_unit import TranslationUnit
from comments.comments_database import CommentsDatabase


class MyTestCase(unittest.TestCase):
    def test_parser_enum(self):
        index: Index = Index.create()
        translation_unit: TranslationUnit = index.parse('../input/enum.hh')
        self.assertTrue(len(translation_unit.diagnostics) == 0)
        database_comments = CommentsDatabase('../input/enum.hh', translation_unit)
        self.assertTrue(len(database_comments) == 3)
        self.assertTrue(repr(database_comments) == "Comments: 3")


if __name__ == '__main__':
    unittest.main()
