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
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFORMATIONAL = 6
    DEBUG = 7
