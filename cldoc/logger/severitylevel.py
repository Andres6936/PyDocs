from enum import IntEnum, unique


@unique
class SeverityLevel(IntEnum):
    """
    The meaning of severity levels other than Emergency and Debug are relative
    to the application. For example, if the purpose of the system is to process
    transactions to update customer account balance information, an error in
    the final step should be assigned Alert level. However, an error occurring
    in an attempt to display the ZIP code of the customer may be assigned Error
    or even Warning level.

    The server process which handles display of messages usually includes all
    lower (more severe) levels when display of less severe levels is requested.
    That is, if messages are separated by individual severity, a Warning level
    entry will also be included when filtering for Notice, Info and Debug
    messages.
    """
    # System is unusable
    EMERGENCY = 0
    # Action must be taken immediately
    ALERT = 1
    # Critical conditions
    CRITICAL = 2
    # Error conditions
    ERROR = 3
    # Warning conditions
    WARNING = 4
    # Normal but significant conditions
    NOTICE = 5
    # Informational messages
    INFORMATIONAL = 6
    # Debug-level messages
    DEBUG = 7

    @staticmethod
    def abbreviation(severity_level):
        abbreviation: str = severity_level.name[0]
        return "[" + abbreviation + "]"
