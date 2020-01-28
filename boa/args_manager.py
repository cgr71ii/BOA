
"""BOA arguments manager.

This file handles the arguments which are given to BOA.

Concretely, the ArgsManager class loads, parses and checks
the arguments. The arguments are loaded from the Args
class in the module *constants*.

Check *constants.Args* for details.
"""

# Std libs
import argparse

# Own libs
from constants import Meta
from constants import Args
from constants import Error

class ArgsManager:
    """ArgsManager class.

    It handles the arguments given to BOA.
    """

    def __init__(self):
        """It creates the ArgParse parser object.
        """
        self.parser = argparse.ArgumentParser(description=Meta.description)

    # It loads the args configuration
    def load_args(self):
        """It loads the arguments from *constants.Args* module.

        From *constants.Args* it is possible to configure mandatory
        and optional arguments. It is possible to set the name
        and a description.
        """
        argc = len(Args.args_str)
        opt_argc = len(Args.opt_args_str)

        for i in range(argc):
            self.parser.add_argument(Args.args_str[i],
                                     help=Args.args_help[i])

        for i in range(opt_argc):
            self.parser.add_argument(Args.opt_args_str[i],
                                     help=Args.opt_args_help[i])


    # It parses the arguments to easily check if they are correct
    def parse(self):
        """It parses the arguments.
        """
        ArgsManager.args = self.parser.parse_args()

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
