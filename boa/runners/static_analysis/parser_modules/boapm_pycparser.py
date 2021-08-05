
"""BOA Parser Module for Pycparser.

Language: C99.
"""

# Std libs
import logging

# 3rd libs
from pycparser import parse_file

# Own libs
from boapm_abstract import BOAParserModuleAbstract
from utils import is_key_in_dict
from exceptions import ParseError, BOAPMParseError
from utils import get_environment_varibles

class BOAPMPycparser(BOAParserModuleAbstract):
    """BOAPMPycparser class.
    """

    def initialize(self):
        """It initializes the necessary variables.
        """
        self.ast = None
        self.pycparser_fake_libc_include_ev = None
        self.compiler_args = []

        env_vars = get_environment_varibles(["PYCPARSER_FAKE_LIBC_INCLUDE_PATH", "PYCPARSER_CPP_ARGS",
                                             "PYCPARSER_CPP_ARGS_SPLIT_CHAR"])

        if "PYCPARSER_FAKE_LIBC_INCLUDE_PATH" in env_vars:
            self.pycparser_fake_libc_include_ev = env_vars["PYCPARSER_FAKE_LIBC_INCLUDE_PATH"]
        if "PYCPARSER_CPP_ARGS" in env_vars:
            split_char = ";"
            self.compiler_args = env_vars["PYCPARSER_CPP_ARGS"]

            if "PYCPARSER_CPP_ARGS_SPLIT_CHAR" in env_vars:
                if len(env_vars["PYCPARSER_CPP_ARGS_SPLIT_CHAR"]) != 1:
                    logging.warning("environment variable 'PYCPARSER_CPP_ARGS_SPLIT_CHAR'"
                                    " has to contain only 1 character when defined")
                else:
                    split_char = env_vars["PYCPARSER_CPP_ARGS_SPLIT_CHAR"]

            self.compiler_args = self.compiler_args.split(split_char)

    def parse(self):
        """It parses the file and save the necessary data structures.
        """
        # parse_file (__init__.py) returns an AST or ParseError if could not parse successfully
        try:
            if self.pycparser_fake_libc_include_ev is not None:
                # use_cpp = Use CPreProcessor
                self.ast = parse_file(self.path_to_file, use_cpp=True, cpp_path="gcc",
                                      cpp_args=["-E", f"-I{self.pycparser_fake_libc_include_ev}"]
                                      + self.compiler_args)
            else:
                self.ast = parse_file(self.path_to_file, use_cpp=False)
        except ParseError as e:
            raise BOAPMParseError(f"could not parse the file '{self.path_to_file}'") from e
        except Exception as e:
            raise BOAPMParseError(f"could not parse the file '{self.path_to_file}' (if preprocessor directives are being used (e.g."
                                  " #include), try defining the environment variable"
                                  f" 'PYCPARSER_FAKE_LIBC_INCLUDE_PATH' in order to solve the problem)") from e

    def get_ast(self):
        """It returns the AST.

        Returns:
            AST (Abstract Syntax Tree)
        """
        if self.ast is None:
            logging.warning("'%s': returning AST = None", self.who_i_am)

        return self.ast
