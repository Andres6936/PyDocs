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
        self.assertEqual(len(database_comments), 3, "The amount of comments in the database not is 3 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 3", "The representation of object not is equal")


if __name__ == '__main__':
    unittest.main()
