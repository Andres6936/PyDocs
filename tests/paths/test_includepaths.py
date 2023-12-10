import unittest

from Pydoc.files.includepaths import _extract_include_paths, _add_prefix_of_inclusion


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

    def test_add_prefix_inclusion(self):
        paths = ['/home/path/directory', '/dev/path/directory']
        paths = _add_prefix_of_inclusion(paths)
        self.assertTrue(tuple(paths) == ('-I/home/path/directory', '-I/dev/path/directory'))



if __name__ == '__main__':
    unittest.main()
