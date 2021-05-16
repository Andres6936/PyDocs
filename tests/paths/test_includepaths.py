import unittest

from includepaths import _extract_include_paths


class MyTestCase(unittest.TestCase):
    def test_extract_include_paths(self):
        compilation_flags = '-I/home/path/directory -fPIC -xc++ -I/dev/path/directory -wired -X:null'
        compilation_flags = _extract_include_paths(compilation_flags)
        self.assertTrue(compilation_flags == '-I/home/path/directory -I/dev/path/directory')

    def test_extract_empty_include_paths(self):
        compilation_flags = ''
        compilation_flags = _extract_include_paths(compilation_flags)
        self.assertTrue(compilation_flags == '')

    def test_extract_only_include_paths(self):
        compilation_flags = '-I/home/path/directory -fPIC -xc++'
        compilation_flags = _extract_include_paths(compilation_flags)
        self.assertTrue(compilation_flags == '-I/home/path/directory')


if __name__ == '__main__':
    unittest.main()
