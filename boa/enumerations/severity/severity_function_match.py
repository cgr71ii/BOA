
"""Severity level for the BOAModuleFunctionMatch.

This severity level defines 3 levels of severity.
"""

# Own libs
from enumerations.severity.severity_base import SeverityBase

class SeverityFunctionMatch(SeverityBase):
    """SeverityFunctionMatch enum.
    """
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3
