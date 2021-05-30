import unittest

from clang.objects.index import Index
from clang.objects.translation_unit import TranslationUnit
from comments.comments_database import CommentsDatabase


class MyTestCase(unittest.TestCase):

    def get_comments_database(self, path_file: str) -> CommentsDatabase:
        """
        Create the index, generate translation unit and parser the comments.
        :path_file The path to source code C++

        Return the database of comment in the source code (translation unit).
        """
        index: Index = Index.create()
        translation_unit: TranslationUnit = index.parse(path_file)
        self.assertEqual(len(translation_unit.diagnostics), 0,
                         "The amount of diagnostic in the translation unit not is zero")
        return CommentsDatabase(path_file, translation_unit)

    def test_parser_abstract(self):
        database_comments = self.get_comments_database("../input/abstract.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0],
                         "A function of A.\n@a the argument.\n\nA longer description of f.\n\n@returns a number.")

    def test_parser_base(self):
        database_comments = self.get_comments_database("../input/base.hh")
        self.assertEqual(len(database_comments), 3, "The amount of comments in the database not is 3 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 3", "The representation of object not is equal")

        self.assertEqual(database_comments[0], "A b method.\n\nThe b method description.\n")
        self.assertEqual(database_comments[1], "\nThe class A.\n\nA longer description of A.\n")
        self.assertEqual(database_comments[2], "@inherit")

    def test_parser_constructor(self):
        database_comments = self.get_comments_database("../input/constructor.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0], "Constructor.\n\nThe constructor of A.\n")

    def test_parser_destructor(self):
        database_comments = self.get_comments_database("../input/destructor.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0], "Destructor.\n\nThe destructor of A.\n")

    def test_parser_enum(self):
        database_comments = self.get_comments_database("../input/enum.hh")
        self.assertEqual(len(database_comments), 3, "The amount of comments in the database not is 3 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 3", "The representation of object not is equal")

        self.assertEqual(database_comments[0], " The enum A.\n\nThe enum A longer description.\n")
        self.assertEqual(database_comments[1], "The A_1 value")
        self.assertEqual(database_comments[2], "The A_2 value")

    def test_parser_interface(self):
        database_comments = self.get_comments_database("../input/interface.hh")
        self.assertEqual(len(database_comments), 4, "The amount of comments in the database not is 4 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 4", "The representation of object not is equal")

    def test_parser_method(self):
        database_comments = self.get_comments_database("../input/method.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0],
                         "A function of A.\n@a the argument.\n\nA longer description of f. Use <a> to pass <A>.\n\n@returns a number.")

    def test_parser_namespace(self):
        database_comments = self.get_comments_database("../input/namespace.hh")
        self.assertEqual(len(database_comments), 6, "The amount of comments in the database not is 6 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 6", "The representation of object not is equal")

        self.assertEqual(database_comments[0], " The namespace A.\n\nLonger description of namespace A.\n")
        self.assertEqual(database_comments[1], "Class B.\n\nClass B in namespace A.\n")
        self.assertEqual(database_comments[2], "Function b.\n\nFunction b in namespace A.\n")
        self.assertEqual(database_comments[3], "Enum E.\n\nEnum E in namespace A.\n")
        self.assertEqual(database_comments[4], "E_1 value.")
        self.assertEqual(database_comments[5], "E_2 value.")

    def test_parser_struct(self):
        database_comments = self.get_comments_database("../input/struct.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0], " The struct A.\n\nA longer description of A.\n")

    def test_parser_template(self):
        database_comments = self.get_comments_database("../input/template.hh")
        self.assertEqual(len(database_comments), 2, "The amount of comments in the database not is 2 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 2", "The representation of object not is equal")

    def test_parser_union(self):
        database_comments = self.get_comments_database("../input/union.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0], "\nThe union A.\n\nA longer description of A.\n")

    def test_parser_union_struct(self):
        database_comments = self.get_comments_database("../input/unionanonstruct.hh")
        self.assertEqual(len(database_comments), 5, "The amount of comments in the database not is 5 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 5", "The representation of object not is equal")

        self.assertEqual(database_comments[0], "\nThe union A.\n\nA longer description of A.\n")
        self.assertEqual(database_comments[1], "The a field.")
        self.assertEqual(database_comments[2], "The b field.")
        self.assertEqual(database_comments[3], "The x field.")
        self.assertEqual(database_comments[4], "The y field.")

    def test_parser_utf8(self):
        database_comments = self.get_comments_database("../input/utf8.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0], "Copyright ©")

    def test_parser_virtual(self):
        database_comments = self.get_comments_database("../input/virtual.hh")
        self.assertEqual(len(database_comments), 1, "The amount of comments in the database not is 1 (comments)")
        self.assertEqual(repr(database_comments), "Comments: 1", "The representation of object not is equal")

        self.assertEqual(database_comments[0],
                         "A function of A.\n@a the argument.\n\nA longer description of f.\n\n@returns a number.")


if __name__ == '__main__':
    unittest.main()
