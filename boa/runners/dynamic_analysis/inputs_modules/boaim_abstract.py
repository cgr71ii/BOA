
"""File which contains the base class to inherit from to use
an input module. Input modules are those modules whose goal
is generating inputs.
"""

# Std libs
from abc import abstractmethod
import logging

# Own libs
from utils import get_name_from_class_instance

# This  file name has to match with constants.Meta.abstract_input_module_name
# This class name has to match with constants.Meta.abstract_input_module_class_name
class BOAInputModuleAbstract:
    """BOAInputModuleAbstract class.

    This class is the base class for those class whose want to
    be an Input Module to generate inputs (e.g. random strings). Those
    classes have to inherit from this class in order to be possible
    to invoke the methods defined here.
    """

    def __init__(self, args):
        """Init method which initializes the general variables which
        will be available from all the classes that inherits from this one.

        Arguments:
            args (dict): arguments.
        """
        self.args = args
        self.who_i_am = get_name_from_class_instance(self)
        self.suffix = "\n"

        if "suffix" in self.args:
            self.suffix = self.args["suffix"]

            if "\\" in self.suffix:
                self.suffix = self.suffix.encode("utf-8").decode("unicode-escape")

        logging.debug("suffix for the generated inputs: %s", self.suffix.encode())

    @abstractmethod
    def initialize(self):
        """Method which will be invoked to initialize what is necessary.
        """

    @abstractmethod
    def generate_input(self):
        """Method which will be invoked to generate an input.

        Returns:
            str: generated input.
        """

    def get_another_input(self):
        """This method is the one that actually has to be invoked
        by other modules in order to get a generated input.

        This method should not be overwritten.

        Returns:
            str: result of *self.generate_input*.
        """
        return f"{self.generate_input()}{self.suffix}"
