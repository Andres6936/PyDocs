import glob
from typing import List


class ProviderSource:
    TYPE_EXTENSION = ["hpp", "hh", "h", "cpp", "cc", "c"]

    def __init__(self, directory: str = ""):
        """
        :param directory: A glob object or directory, default to empty string.
        """
        self.sources: List[str] = []
        self.provider_sources(directory)

    def provider_sources(self, directory: str) -> None:
        """
        Populate a list with the sources and headers find in the directories.
        :param directory:  A glob object or directory.
        :return: None.
        """
        for path in glob.iglob(directory, recursive=True):
            if path.endswith(tuple(self.TYPE_EXTENSION)):
                self.sources.append(path)

