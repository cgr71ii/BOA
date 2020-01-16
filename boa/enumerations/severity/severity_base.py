
"""Severity levels.

In this file is defined the base enum for defining
severity levels, whose can be overridden and new ones
can be defined.
"""

# Std libs
from enum import IntEnum, unique

@unique
class SeverityBase(IntEnum):
    """SeverityBase class (enum).

    You can inherit from this class and implement your own
    severity levels. An approach could be to use the standard
    risk model (risk = likelyhood [0-N] * impact [0-N]). To
    allow the inheritance we have to let this enum empty.

    The enum values mean the priority (higher means more
    critical). This values will be used for sorting the
    records.
    """
