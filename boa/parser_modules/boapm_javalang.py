
"""BOA Parser Module for Javalang.

Language: Java.
"""

# Javalang libs
import javalang

# Own libs
from boapm_abstract import BOAParserModuleAbstract
from util import eprint, is_key_in_dict
from own_exceptions import ParseError, BOAPMParseError

class BOAPMJavalang(BOAParserModuleAbstract):
    """BOAPMJavalang class.
    """

    def initialize(self):
        """It initializes the necessary variables.
        """
        self.ast = None
        self.code = ""

    def parse(self):
        """It parses the file and save the necessary data structures.
        """
        self.load_code()

        try:
            self.ast = javalang.parse.parse(self.code)
        except Exception as e:
            raise BOAPMParseError(f"could not parse the file '{self.path_to_file}'")

    def get_ast(self):
        """It returns the AST.

        Returns:
            AST (Abstract Syntax Tree)
        """
        if self.ast is None:
            eprint(f"Warning: '{self.who_i_am}': returning AST = None.")

        return self.ast

    def load_code(self):
        """It loads the code from the file.
        """
        file_desc = None

        # Open file
        try:
            file_desc = open(self.path_to_file, "r")
        except Exception as e:
            raise BOAPMParseError(f"could not open the file '{self.path_to_file}'")

        # Read file
        try:
            lines = file_desc.readlines()
            self.code = ""

            for line in lines:
                self.code += line
        except Exception as e:
            raise BOAPMParseError(f"could not read the file '{self.path_to_file}'")
        
        # Close file
        try:
            file_desc.close()
        except Exception as e:
            raise BOAPMParseError(f"could not close the file '{self.path_to_file}'")
