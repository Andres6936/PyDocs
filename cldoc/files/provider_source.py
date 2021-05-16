import glob
from typing import List


class ProviderSource:
    """
    Store all the sources files and headers of C++ directory (glob or path
    string). If the directory or glob string is empty, none source is stored.
    """

    # Type of extension for C++ headers.
    TYPE_HEADERS = [".hpp", ".hh", ".h"]

    # Type of extension for C++ sources.
    TYPE_SOURCES = [".cpp", ".cc", ".c"]

    # Type of extension for default for C++ (sources and headers)
    TYPE_EXTENSION = TYPE_HEADERS + TYPE_SOURCES

    def __init__(self, directory: str = ""):
        """
        :param directory: A glob object or directory, default to empty string.
        """
        self.sources: List[str] = []
        self.provider_sources(directory)

    def __iter__(self):
        """
        :return: Return a iterator object over the source files stored.
        """
        return self.sources.__iter__()

    def __len__(self) -> int:
        """
        Assert: The number always will be 0 or greater to 0.
        :return: Returns the number of source files and headers stored.
        """
        return len(self.sources)

    def provider_sources(self, directory: str) -> None:
        """
        Populate a list with the sources and headers found in the directories.
        :param directory: A glob object or directory, can be a empty string.
        :return: None.
        """
        for path in glob.iglob(directory, recursive=True):
            if path.endswith(tuple(self.TYPE_EXTENSION)):
                self.sources.append(path)

    def sort_first_by_sources(self) -> None:
        """
        Sort the files stored based on whether it is of type source type.
        The files of source type will be the first in the list.
        :return: None.
        """
        self.__sort_first_by(self.TYPE_SOURCES)

    def sort_first_by_headers(self) -> None:
        """
        Sort the files stored based on whether it is of type header type.
        The files of header type will be the first in the list.
        :return:
        """
        self.__sort_first_by(self.TYPE_HEADERS)

    def __sort_first_by(self, type_extension: List[str]) -> None:
        """
        Sort the files stored based in the type extension.
        :param type_extension: List of extensions for sort the files stored,
        if the file match with the type of extension it will be placed above
        files whose extension is not of the specified type.
        :return: None.
        """
        self.sources.sort(key=lambda file: not file.endswith(tuple(type_extension)))

