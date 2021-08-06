
"""BOA arguments manager.

This file handles the arguments which are provided to BOA.

Concretely, the ArgsManager class loads, parses and checks
the arguments. The arguments are defined in this file
"""

# Std libs
import argparse
import logging

# Own libs
from constants import Meta
from constants import Error

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
        self.parser.add_argument("target",
                                 help="Target file to analyze, which should be either a code file (e.g. /path/to/file.c) or a binary (e.g. /usr/bin/pwd)")
        self.parser.add_argument("rules_file", metavar="rules-file",
                                 help="Rules file")

        # Optional
        self.parser.add_argument("-v", "--version", action="store_true",
                                 help="Show the version and exit")
        self.parser.add_argument("--no-fail", action="store_true",
                                 help="Continue the execution even if some user module could not be loaded")
        ## Debug
        self.parser.add_argument("--print-traceback", action="store_true",
                                 help="Print traceback when an exception is raised")
        ## Logging
        self.parser.add_argument("--logging-level", metavar="N", type=int, default=20,
                                 help="Logging level. Default value is 30, which is INFO")
        self.parser.add_argument("--log-file", metavar="PATH",
                                 help="If specified, the log will be dumped to the file instead of displayed to the standar error output")
        self.parser.add_argument("--log-display", action="store_true",
                                 help="If specified besides --log-file, the log will be also displayed to the standar error output")

    # It parses the arguments to easily check if they are correct
    def parse(self):
        """It parses the arguments.

        Returns:
            int: status code
        """
        try:
            ArgsManager.args = self.parser.parse_args()
        except Exception as e:
            logging.error("error while parsing the args: %s", str(e))
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
