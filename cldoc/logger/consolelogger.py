import sys

from logger.ilogger import ILogger
from logger.severitylevel import SeverityLevel


class ConsoleLogger(ILogger):
    def emergency(self, msg):
        self.message(SeverityLevel.EMERGENCY, msg)

    def alert(self, msg):
        self.message(SeverityLevel.ALERT, msg)

    def critical(self, msg):
        self.message(SeverityLevel.CRITICAL, msg)

    def error(self, msg):
        self.message(SeverityLevel.ERROR, msg)

    def warning(self, msg):
        self.message(SeverityLevel.WARNING, msg)

    def notice(self, msg):
        self.message(SeverityLevel.NOTICE, msg)

    def informational(self, msg):
        self.message(SeverityLevel.INFORMATIONAL, msg)

    def debug(self, msg):
        self.message(SeverityLevel.DEBUG, msg)

    @staticmethod
    def message(severity_level: SeverityLevel, msg: str):
        sys.stdout.write("{} - {}".format(
            SeverityLevel.abbreviation(severity_level), msg))
