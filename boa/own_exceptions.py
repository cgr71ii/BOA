
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
    """BOAModuleException exception. It implements the Exception class.

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
