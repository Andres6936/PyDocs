import unittest

from clang.objects.index import Index
from clang.objects.translation_unit import TranslationUnit
from comments.comments_database import CommentsDatabase


class MyTestCase(unittest.TestCase):
    def test_parser_enum(self):
        path_file: str = "../input/enum.hh"
        index: Index = Index.create()
        translation_unit: TranslationUnit = index.parse(path_file)
        self.assertEqual(len(translation_unit.diagnostics), 0,
                         "The amount of diagnostic in the translation unit not is zero")
        database_comments = CommentsDatabase(path_file, translation_unit)
        self.assertEqual(len(database_comments), 3, "The amount of comments in the database not is 3 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 3", "The representation of object not is equal")


if __name__ == '__main__':
    unittest.main()
