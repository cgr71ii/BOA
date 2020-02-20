
"""Severity level for the BOAModuleFunctionMatch.

This severity level defines 3 levels of severity.
"""

# Own libs
from enumerations.severity.severity_base import SeverityBase

class SeverityFunctionMatch(SeverityBase):
    """SeverityFunctionMatch enum.
    """
    VERY_LOW = 1
    LOW = 2
    MISUSED = 3
    FREQUENTLY_MISUSED = 4
    HIGH = 5
    CRITICAL = 6
