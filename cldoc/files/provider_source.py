import glob
from typing import List


class ProviderSource:
    """
    Provide all the sources files and headers of C++ directory (glob or path
    string).
    """

    # Type of extension for default for C++ (sources and headers)
    TYPE_EXTENSION = ["hpp", "hh", "h", "cpp", "cc", "c"]

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

