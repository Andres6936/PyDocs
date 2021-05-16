import glob
from typing import List


class ProviderSource:
    TYPE_EXTENSION = ["hpp", "hh", "h", "cpp", "cc", "c"]

    def __init__(self, directory: str):
        self.sources: List[str] = []
        self.provider_sources(directory)

    def provider_sources(self, directory: str) -> None:
        for path in glob.iglob(directory, recursive=True):
            if path.endswith(tuple(self.TYPE_EXTENSION)):
                self.sources.append(path)

