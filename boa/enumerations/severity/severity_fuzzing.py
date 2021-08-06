
"""Severity level for fuzzing.

This severity level defines 5 levels of severity.
"""

# Std libs
from enumerations.severity.severity_base import SeverityBase

class SeverityFuzzing(SeverityBase):
    """SeverityFuzzing class (enum).
    """
    DEBUG = 0
    FAILED_LOW_CONFIDENCE = 1
    FAILED = 2
    FAILED_HIGH_CONFIDENCE = 3
    FAILED_WITHOUT_DOUBT = 4
