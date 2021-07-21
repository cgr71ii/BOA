"""BOA module abstraction.

This module is an abstraction to use by other modules they
want to be used by BOA as a security module. It defines
a class with its methods to be overriden by those modules
which will be executed after, using these methods.

In order to raise exceptions, you may use
*own_exceptions.BOAModuleException* if you want to know
descriptive information about your errors and know from
where it comes the error.
"""

# Std libs
from abc import abstractmethod
import logging

# Own libs
from util import get_name_from_class_instance
from constants import Other

# This  file name has to match with constants.Meta.abstract_module_name
# This class name has to match with constants.Meta.abstract_module_class_name
class BOAModuleAbstract:
    """BOAModuleAbstract class.

    This class is the one which modules whose want to
    implement a security module has to inherit from in
    order to be a security module.

    If you do not set a custom lifecycle, *boalc_basic.BOALCBasic*
    will be used as lifecycle for the module.
    """

    # This method sets the args and should not be overriden
    #  (override 'initialize' method instead for initialization purposes)
    def __init__(self, args):
        """It sets the args.

        It should not be overriden, and if overrided, the defined variables
        are:

        * self._dependencies (dict): if no dependencies, the value is an empty dict.

        * self._args (dict): if no args, the value is an empty dict.

        * self._who_i_am (str): expected format is '"module_name"."class_name"'.

        * self._stop (bool)

        Arguments:
            args (dict): arguments which will be used by those modules which
                implements this class.
        """
        self._dependencies = args.pop(Other.other_argument_name_for_dependencies_in_modules)
        self._args = args
        self._who_i_am = get_name_from_class_instance(self)
        self._stop = False

        if self._dependencies is None:
            self._dependencies = {}

    @abstractmethod
    def initialize(self):
        """It loads the args an initializes the module.
        """

    @abstractmethod
    def process(self, args):
        """It process the given information from the rules
        file and attempts to look for security threats.

        Arguments:
            args: given information.
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
    def dependencies(self):
        """Dependencies property. Read only.

        It contains information about the dependencies of the
        instance.
        """
        return self._dependencies

    @property
    def stop(self):
        """Stop property. Read and write.

        When this property is set to *True*, the set lifecycle will stop
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
            logging.error("not expected value in 'stop' property")
        elif not isinstance(value, bool):
            logging.error("expected type in 'stop' property is 'bool' and the actual type is '%s'", type(value))
        else:
            self._stop = value
