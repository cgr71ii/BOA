
"""Own defined exceptions.

In this file are defined the exceptions which BOA
uses through all the files (the custom ones).
"""

# Own libs
from util import get_name_from_class_instance

class ParseError(Exception):
    """ParseError exception.

    This exceptions is raised by Pycparser and has to be
    redefined because after the installation, was not
    found by Pycparser, and it was defined in the
    expected file and path.
    """

class BOAModuleNotLoaded(Exception):
    """BOAModulesNotLoaded exception.

    This exception is raised by BOA when a module could not
    be loaded.
    """

class BOAModuleException(Exception):
    """BOAModuleException exception.

    This exception has the goal of redefine the exception base
    message to give a more verbose message about the BOA
    module which is being executed in the moment of the
    exception to be raised.

    It should be raised only in the BOA security modules due to
    the message which is displayed.
    """

    def __init__(self, message, class_instance):
        """It redefined self.message with the goal of be more
        verbose.

        Arguments:
            message (str): custom message to be displayed when the exception is raised.
            class_instance: class instance from where the exception is raised. Usually,
                this value should be the variable "self" in a BOA module.
        """
        self.message = f"BOAM exception in {get_name_from_class_instance(class_instance)}: {message}"

class BOAReportWhoNotFound(Exception):
    """BOAReportWhoNotFound exception.

    This exception should be raised when a threat record is
    attempted to be displayed and the given module is not found.
    """

class BOAReportEnumTypeNotExpected(Exception):
    """BOAReportEnumTypeNotExpected exception.

    This exception should be raised when an instance of Report
    is initialized with a non-expected enum type:\n
        * Instance that not implementes *SeverityBase*.\n
        * *SeverityBase*.
    """

class BOARulesUnexpectedFormat(Exception):
    """BOARulesUnexpectedFormat exception.

    This exception should be raised when the rules are being
    checked and some concrete requirements are not asserted.
    """

class BOARulesIncomplete(Exception):
    """BOARulesIncomplete exception.

    This exception should be raised when the rules are incomplete
    because it lacks some rule/s.
    """

class BOARulesError(Exception):
    """BOARulesError exception.

    This exception should be raised when a non-especific error
    happens when parsing rules. An example of when to be raised
    could be that if we set a rule and other rule should be set
    because of that and the second is not set, it should be raised.
    """

class BOAPMInitializationError(Exception):
    """BOAPMInitializationError exception.

    This exception should be raised when initialization is executed
    and any error happens. It is a general exception and only this
    exception should be raised in the *initialize* method in a
    BOA parser module.
    """

class BOAPMParseError(Exception):
    """BOAPMParseError exception.

    This exception should be raised when the parse method is executed
    and any error happens. It is a general exception and only this
    exception should be raised in the *parse* method in a BOA parser
    module.
    """

class BOALCException(Exception):
    """BOALCException exception.

    This exception should be raised when you want to stop the execution
    of a BOA lifecycle. Other exceptions might be raised, but this one
    will give specific information about the error to know that the
    exception has been raised because a BOA lifecycle.
    """
