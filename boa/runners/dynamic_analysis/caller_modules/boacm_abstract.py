
"""File which contains the base class to inherit from to use
a caller module. Caller modules are those modules whose goal
must be deal with the execution and other optional steps
(e.g. instrumentation).
"""

# Std libs
from abc import abstractmethod

# Own libs
from util import get_name_from_class_instance

# This  file name has to match with constants.Meta.abstract_caller_module_name
# This class name has to match with constants.Meta.abstract_caller_module_class_name
class BOACallerModuleAbstract:
    """BOACallerModuleAbstract class.

    This class is the base class for those class whose want to
    be a Caller Module to make operations relationed to a concrete
    way of execute a software (e.g. invoke from terminal). Those
    class has to inherit from this class in order to be possible
    to invoke the methods defined here.
    """

    def __init__(self, input_generator, fails_detector, caller_command, environment_variables=None):
        """Init method which initializes the general variables which
        will be available from all the classes that inherits from this one.

        Arguments:
            input_generator (BOAInputModuleAbstract): object which provides
                inputs for the target software
            fails_detector (BOAFailsModuleAbstract): object which allows us
                to know when a specific execution have failed or not
            caller_command (list): list of commands to run the main file
                (e.g. ["python3", "/path/to/my/script.py"], ["/path/to/bin"]).
            environment_variables (dict): environment variables which will be
                provided to every execution and that might be modified by other
                methods if you want to test the behaviour.
        """
        self.input_generator = input_generator
        self.fails_detector = fails_detector
        self.caller_command = caller_command
        self.environment_variables = environment_variables
        self.who_i_am = get_name_from_class_instance(self)

    @abstractmethod
    def initialize(self):
        """Method which will be invoked to initialize what is necessary.

        Raises:
            BOACMInitializationError: when any error happens while the
                initialization is being executed. Only this exception should
                be raised.
        """

    @abstractmethod
    def run(self):
        """Method which will be invoked to begin the execution.

        Raises:
            BOACMRunError: when any error happens while the parsing
                is being executed. Only this exception should be raised.
        """

    @abstractmethod
    def tear_down(self):
        """Method which will be invoked to tear down what is necessary.

        Raises:
            BOACMTearDownError: when any error happens while the
                initialization is being executed. Only this exception should
                be raised.
        """
