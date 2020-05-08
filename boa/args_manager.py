
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
from util import eprint

class ArgsManager:
    """ArgsManager class.

    It handles the arguments given to BOA.
    """

    def __init__(self):
        """It creates the ArgParse parser object.
        """
        self.parser = argparse.ArgumentParser(description=Meta.description)

    def str2bool(self, value):
        """Method that parses string to bool.

        Arguments:
            value (string): value to be parsed to boolean.

        Returns:
            bool: boolean value from a string.
        """
        if isinstance(value, bool):
            return value
        if value.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        if value.lower() in ('no', 'false', 'f', 'n', '0'):
            return False

        raise argparse.ArgumentTypeError('boolean value expected.')

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
            if Args.args_bool[i] is not None:
                self.parser.add_argument(Args.args_str[i],
                                         help=Args.args_help[i],
                                         type=self.str2bool, nargs='?',
                                         const=True, default=Args.args_bool[i])
            else:
                self.parser.add_argument(Args.args_str[i],
                                         help=Args.args_help[i])

        for i in range(opt_argc):
            if Args.opt_args_bool[i] is not None:
                self.parser.add_argument(Args.opt_args_str[i],
                                         help=Args.opt_args_help[i],
                                         type=self.str2bool, nargs='?',
                                         const=True, default=Args.opt_args_bool[i])
            else:
                self.parser.add_argument(Args.opt_args_str[i],
                                         help=Args.opt_args_help[i])


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
