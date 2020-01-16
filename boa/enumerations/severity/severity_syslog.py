
"""Severity level based on syslog (RFC 5424).

This severity level defines 8 levels of severity.
"""

# Std libs
from enumerations.severity.severity_base import SeverityBase

class SeveritySyslog(SeverityBase):
    """SeveritySyslog class (enum).

    There are multiple ways of defining severity levels.
    For the severity base we are using an approach based
    on Syslog Message Severities (RFC 5424).
    """
    DEBUG = 0
    INFORMATIONAL = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5
    ALERT = 6
    EMERGENCY = 7
