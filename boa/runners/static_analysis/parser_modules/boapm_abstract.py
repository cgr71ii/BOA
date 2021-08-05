
"""File which contains the base class to inherit from to use
a parser module. Parser modules are those modules whose goal
must be deal with the real file and process it in order to
get processed information that should make easier to deal with it
when we have to analyze it (e.g. Abstract Syntax Tree).
"""

# Std libs
from abc import abstractmethod
import logging

# Own libs
from utils import get_environment_varibles, get_name_from_class_instance

# This  file name has to match with constants.Meta.abstract_parser_module_name
# This class name has to match with constants.Meta.abstract_parser_module_class_name
class BOAParserModuleAbstract:
    """BOAParserModuleAbstract class.

    This class is the base class for those class whose want to
    be a Parser Module to make operations relationed to a concrete
    parser (e.g. pycparser). Those classes have to inherit from this
    class in order to be possible to invoke the methods defined
    here.
    """

    def __init__(self, path_to_file):
        """Init method which initializes the general variables which
        will be available from all the classes that inherits from this one.

        Arguments:
            path_to_file (str): path to the file which is going to be analyzed.

        Note:
            Is not guaranteed that all the given environment variables are loaded,
            so that should be in mind when a parser module uses environmental
            variables and should contain default values for those environmental
            variables not found or a default behaviour.
        """
        self.path_to_file = path_to_file
        self.environment_variables = {}
        self.who_i_am = get_name_from_class_instance(self)

    @abstractmethod
    def initialize(self):
        """Method which will be invoked to initialize what is necessary.

        Raises:
            BOAPMInitializationError: when any error happens while the
                initialization is being executed. Only this exception should
                be raised.
        """

    @abstractmethod
    def parse(self):
        """Method which will be invoked to parse the file and process
        whatever is necessary.

        Raises:
            BOAPMParseError: when any error happens while the parsing
                is being executed. Only this exception should be raised.
        """
