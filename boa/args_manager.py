
"""BOA arguments manager.

This file handles the arguments which are provided to BOA.

Concretely, the ArgsManager class loads, parses and checks
the arguments. The arguments are defined in this file
"""

# Std libs
import argparse

# Own libs
from constants import Meta
from constants import Error
from util import eprint

class ArgsManager:
    """ArgsManager class.

    It handles the arguments provided to BOA CLI.
    """

    def __init__(self):
        """It creates the ArgParse parser object.
        """
        self.parser = argparse.ArgumentParser(description=Meta.description)

    # It loads the args configuration
    def load_args(self):
        """It creates the list of arguments.
        """
        # Mandatory
        self.parser.add_argument("code_file",
                                 help="code file to analyze")
        self.parser.add_argument("rules_file",
                                 help="rules file")

        # Optional
        self.parser.add_argument("--no-fail",
                                 help="continue the execution even if some user module could not be loaded",
                                 action="store_true")

    # It parses the arguments to easily check if they are correct
    def parse(self):
        """It parses the arguments.

        Returns:
            int: status code
        """
        try:
            ArgsManager.args = self.parser.parse_args()
        except:
            return Error.error_args_incorrect

        return Meta.ok_code

    # It checks if args are correctly used
    def check(self):
        """It checks if the arguments are the expected type.

        Concretely, in this method it is checked if the arguments are
        an instance of *argparse.Namespace*.

        Returns:
            int: status code
        """
        if not isinstance(ArgsManager.args, argparse.Namespace):
            return Error.error_args_type

        return Meta.ok_code
