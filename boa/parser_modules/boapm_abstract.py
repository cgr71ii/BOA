
"""
"""

# Std libs
from abc import abstractmethod

# Own libs
from util import get_environment_varibles, get_name_from_class_instance
from util import get_name_from_class_instance

# This  file name has to match with constants.Meta.abstract_parser_module_name
# This class name has to match with constants.Meta.abstract_parser_module_class_name
class BOAParserModuleAbstract:
    """
    """

    def __init__(self, path_to_file, environment_variable_names=None):
        """
        """
        self.path_to_file = path_to_file
        self.environment_variable_names = environment_variable_names
        self.environment_variables = None
        self.who_i_am = get_name_from_class_instance(self)

        if self.environment_variable_names is not None:
            if isinstance(environment_variable_names, (list, str)):
                self.environment_variables = get_environment_varibles(environment_variable_names,
                                                                      True,
                                                                      "Warning: could not load an "
                                                                      "environment variable in "
                                                                      f"'{self.who_i_am}'")
            else:
                print("Warning: any environment variable will not be loaded"
                      " because not a list nor a string were given in "
                      f"'{get_name_from_class_instance(self)}'.")

    @abstractmethod
    def initialize(self):
        """
        """

    @abstractmethod
    def parse(self):
        """
        """
