import inspect
import sys

from cldoc.logger.ilogger import ILogger
from cldoc.logger.severitylevel import SeverityLevel


class ConsoleLogger(ILogger):
    def emergency(self, msg):
        self.__message(SeverityLevel.EMERGENCY, msg)

    def alert(self, msg):
        self.__message(SeverityLevel.ALERT, msg)

    def critical(self, msg):
        self.__message(SeverityLevel.CRITICAL, msg)

    def error(self, msg):
        self.__message(SeverityLevel.ERROR, msg)

    def warning(self, msg):
        self.__message(SeverityLevel.WARNING, msg)

    def notice(self, msg):
        self.__message(SeverityLevel.NOTICE, msg)

    def informational(self, msg):
        self.__message(SeverityLevel.INFORMATIONAL, msg)

    def debug(self, msg):
        self.__message(SeverityLevel.DEBUG, msg)

    @staticmethod
    def __message(severity_level: SeverityLevel, msg: str):
        sys.stdout.write("{} - F:{} - {}\n".format(
            SeverityLevel.abbreviation(severity_level), inspect.stack()[2][3], msg))
