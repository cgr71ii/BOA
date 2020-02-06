"""BOA module abstraction (interface).

This module is an abstraction to use by other modules they
want to be used by BOA as a security module. It defines
a class with its methods to be overriden by those modules
which will be executed after, using these methods.

Advice:
    Use exception with descriptive messages if you want
    to know descriptive information about your errors.
    You can use `own_exceptions.BOAModuleException` for that purpose.

Note:
    This "interface" can be seen as a ``lifecycle``, and surely
    other lifecycles will be implemented.
"""

# Std libs
from abc import abstractmethod

# Own libs
from util import get_name_from_class_instance, eprint

# This  file name has to match with constants.Meta.abstract_module_name
# This class name has to match with constants.Meta.abstract_module_class_name
class BOAModuleAbstract:
    """BOAModuleAbstract class.

    This class is an abstraction to be implemented by those
    modules which use an AST (Abstract Syntax Tree) and want
    to get token after token.

    Main flow:\n
    * initialize()\n
    *  process(ast_token) \*\n
    *  clean() \*\n
    * save(report_obj)\n
    * finish()\n
    * \*: for each AST token
    """

    # This method sets the args and should not be overriden
    #  (override 'initialize' method instead for initialization purposes)
    def __init__(self, args):
        """It sets the args.

        Arguments:
            args (list): arguments which will be used by those modules which
                implements this class.
        """

        self._args = args
        self._who_i_am = get_name_from_class_instance(self)
        self._stop = False

    # This method loads the args and initializes the module
    @abstractmethod
    def initialize(self):
        """It loads the args an initializes the module.
        """

    # This method process each token
    @abstractmethod
    def process(self, token):
        """It process each AST token.

        Arguments:
            token: AST token.
        """

    # This method will be invoked before the next token is processed
    @abstractmethod
    def clean(self):
        """It cleans the class before the next token is processed.
        """

    # This method will be invoked after all tokens have been processed
    # This method has the responsibility of update the records in the given report
    @abstractmethod
    def save(self, report):
        """It saves the security threads found in a report.
        This method will be invoked after all tokens have been processed.

        Arguments:
            report: report which will contain the threats records.
        """

    # This method will be invoked when all the tokens have been processed
    @abstractmethod
    def finish(self):
        """This method will be invoked when all the tokens have been processed.
        """

    def set_stop_execution(self, value):
        """It allows the user to call this method to change the value of *stop*.
        This method is implemented because in *lifecycle* modules a method
        callback is given to execute methods, and no direct access is given,
        so this method can be invoked.

        Arguments:
            value (bool): value to set to the *stop* property.
        """
        self.stop = value

    @property
    def args(self):
        """Args property. Read only.

        It contains the given args to the concrete instance.
        """
        return self._args

    @property
    def who_i_am(self):
        """Who I am property. Read only.

        It contains information about the module and the class
        of the instance.
        """
        return self._who_i_am

    @property
    def stop(self):
        """Stop property. Read and write.

        When this property is set to *True*, the main loop will stop
        the execution of the instance and will not even show the found
        threats in the report. The default value is *False*.
        """
        return self._stop

    @stop.setter
    def stop(self, value):
        """Stop property: setter.

        Arguments:
            value (bool): value to set if the execution has to be stopped.
        """
        if value is None:
            eprint("Error: not expected value in 'stop' property.")
        elif not isinstance(value, bool):
            eprint("Error: expected type in 'stop' property is 'bool'"
                   f" and the actual type is '{type(value)}'.")
        else:
            self._stop = value
