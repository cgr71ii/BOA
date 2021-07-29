
"""File which contains the base class to inherit from to use
an input module. Input modules are those modules whose goal
is generating inputs.
"""

# Std libs
from abc import abstractmethod

# Own libs
from util import get_name_from_class_instance

# This  file name has to match with constants.Meta.abstract_input_module_name
# This class name has to match with constants.Meta.abstract_input_module_class_name
class BOAInputModuleAbstract:
    """BOAInputModuleAbstract class.

    This class is the base class for those class whose want to
    be an Input Module to generate inputs (e.g. random strings). Those
    classes have to inherit from this class in order to be possible
    to invoke the methods defined here.
    """

    def __init__(self, inputs_examples=None, inputs_status=None):
        """Init method which initializes the general variables which
        will be available from all the classes that inherits from this one.

        Arguments:
            inputs_examples (list): list of inputs which are examples
            inputs_status (list): list of the status which the execution
                should return which the input of *input_examples* in the
                same position. The allowed values are *True*, *False* and
                *None*
        """
        self.inputs_examples = inputs_examples
        self.inputs_status = inputs_status
        self.who_i_am = get_name_from_class_instance(self)

    @abstractmethod
    def initialize(self):
        """Method which will be invoked to initialize what is necessary.
        """

    @abstractmethod
    def generate_input(self):
        """Method which will be invoked to generate an input.
        """
