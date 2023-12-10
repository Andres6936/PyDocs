from abc import ABC, abstractmethod


class ILogger(ABC):
    @abstractmethod
    def emergency(self, msg):
        pass

    @abstractmethod
    def alert(self, msg):
        pass

    @abstractmethod
    def critical(self, msg):
        pass

    @abstractmethod
    def error(self, msg):
        pass

    @abstractmethod
    def warning(self, msg):
        pass

    @abstractmethod
    def notice(self, msg):
        pass

    @abstractmethod
    def informational(self, msg):
        pass

    @abstractmethod
    def debug(self, msg):
        pass
