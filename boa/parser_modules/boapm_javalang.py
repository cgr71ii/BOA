
"""BOA Parser Module for Javalang.

Language: Java.
"""

# Std libs
import logging

# 3rd libs
import javalang

# Own libs
from boapm_abstract import BOAParserModuleAbstract
from own_exceptions import BOAPMParseError

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
            raise BOAPMParseError(f"could not parse the file '{self.path_to_file}'") from e

    def get_ast(self):
        """It returns the AST.

        Returns:
            AST (Abstract Syntax Tree)
        """
        if self.ast is None:
            logging.warning("'%s': returning AST = None", self.who_i_am)

        return self.ast

    def load_code(self):
        """It loads the code from the file.
        """
        file_desc = None

        # Open file
        try:
            file_desc = open(self.path_to_file, "r")
        except Exception as e:
            raise BOAPMParseError(f"could not open the file '{self.path_to_file}'") from e

        # Read file
        try:
            lines = file_desc.readlines()
            self.code = ""

            for line in lines:
                self.code += line
        except Exception as e:
            raise BOAPMParseError(f"could not read the file '{self.path_to_file}'") from e

        # Close file
        try:
            file_desc.close()
        except Exception as e:
            raise BOAPMParseError(f"could not close the file '{self.path_to_file}'") from e
