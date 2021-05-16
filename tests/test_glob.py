import glob
import unittest


class MyTestCase(unittest.TestCase):
    def test_glob_cpp_sources(self):
        self.headers = glob.glob("input/Include/Doryen/**", recursive=True)
        self.sources = glob.glob("input/Source/**", recursive=True)
        self.assertTrue(len(self.headers) == 89)
        self.assertTrue(len(self.sources) == 64)


if __name__ == '__main__':
    unittest.main()
