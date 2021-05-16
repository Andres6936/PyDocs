import unittest

from files.provider_source import ProviderSource


class MyTestCase(unittest.TestCase):
    def test_glob_cpp_headers(self):
        headers = ProviderSource("input/Include/Doryen/**")
        self.assertTrue(len(headers) == 64)

    def test_glob_cpp_sources(self):
        sources = ProviderSource("input/Source/**")
        self.assertTrue(len(sources) == 42)

    def test_glob_empty(self):
        files = ProviderSource()
        self.assertTrue(len(files) == 0)


if __name__ == '__main__':
    unittest.main()
