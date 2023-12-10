import unittest

from Pydoc.files.provider_source import ProviderSource


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

    def test_provider_source_sort(self):
        sources = ProviderSource("input/Include/Doryen/**")
        sources.provider_sources("input/Source/**")
        self.assertTrue(len(sources) == 64 + 42)
        sources.sort_first_by_sources()
        for source in sources:
            # Assert the first file is of type source
            self.assertTrue(source.endswith(tuple(ProviderSource.TYPE_SOURCES)))
            # Only verified the first file
            break

    def test_provider_header_sort(self):
        sources = ProviderSource("input/Include/Doryen/**")
        sources.provider_sources("input/Source/**")
        self.assertTrue(len(sources) == 64 + 42)
        sources.sort_first_by_headers()
        for source in sources:
            # Assert the first file is of type source
            self.assertTrue(source.endswith(tuple(ProviderSource.TYPE_HEADERS)))
            # Only verified the first file
            break


if __name__ == '__main__':
    unittest.main()
