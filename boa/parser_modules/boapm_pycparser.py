
"""BOA Parser Module for Pycparser.

Language: C99.
"""

# Pycparser libs
from pycparser import parse_file

# Own libs
from boapm_abstract import BOAParserModuleAbstract
from util import eprint, is_key_in_dict
from own_exceptions import ParseError, BOAPMParseError

class BOAPMPycparser(BOAParserModuleAbstract):
    """BOAPMPycparser class.
    """

    def initialize(self):
        """It initializes the necessary variables.
        """
        self.ast = None
        self.pycparser_fake_libc_include_ev = None

        if is_key_in_dict(self.environment_variables, "PYCPARSER_FAKE_LIBC_INCLUDE_PATH"):
            self.pycparser_fake_libc_include_ev = self.environment_variables["PYCPARSER_FAKE_LIBC_INCLUDE_PATH"]

    def parse(self):
        """It parses the file and save the necessary data structures.
        """
        # parse_file (__init__.py) returns an AST or ParseError if could not parse successfully
        try:
            if self.pycparser_fake_libc_include_ev is not None:
                # use_cpp = Use CPreProcessor
                self.ast = parse_file(self.path_to_file, use_cpp=True, cpp_path="gcc",
                                      cpp_args=["-E", f"-I{self.pycparser_fake_libc_include_ev}"])
            else:
                self.ast = parse_file(self.path_to_file, use_cpp=False)
        except ParseError as e:
            raise BOAPMParseError(f"could not parse the file '{self.path_to_file}'")
        except Exception as e:
            raise BOAPMParseError(f"{e} (if  preprocessor directives are being used (e.g."
                                  " #include), try defining the environment variable"
                                  " PYCPARSER_FAKE_LIBC_INCLUDE_PATH in order to solve the problem)")

    def get_ast(self):
        """It returns the AST.

        Returns:
            AST (Abstract Syntax Tree)
        """
        if self.ast is None:
            eprint(f"Warning: '{self.who_i_am}': returning AST = None.")

        return self.ast
