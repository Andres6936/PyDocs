import glob
import unittest

from files.provider_source import ProviderSource


class MyTestCase(unittest.TestCase):
    def test_glob_cpp_sources(self):
        self.headers = ProviderSource("input/Include/Doryen/**")
        self.sources = ProviderSource("input/Source/**")
        self.assertTrue(len(self.headers) == 64)
        self.assertTrue(len(self.sources) == 42)

        self.files = ProviderSource()
        self.assertTrue(len(self.files) == 0)


if __name__ == '__main__':
    unittest.main()
