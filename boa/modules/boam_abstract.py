"""BOA module abstraction (interface)

This module is an abstraction to use by other modules they
want to be used by BOA as a security module. It defines
a class with its methods to be overriden by those modules
which will be executed after, using these methods.

Advice:
    Use exception with descriptive messages if you want
    to know descriptive information about your errors.
    You can use `own_exceptions.BOAModuleException` for that purpose.

Note:
    This "interface" can be seen as a ``lifecycle``, and surely
    other lifecycles will be implemented.
"""

# Std libs
from abc import abstractmethod

# This  file name has to match with constants.Meta.abstract_module_name
# This class name has to match with constants.Meta.abstract_module_class_name
class BOAModuleAbstract:
    """Module abstraction (interface; lifecycle)

    This class is an abstraction to be implemented by those
    modules which use an AST (Abstract Syntax Tree) and want
    to get token after token.

    Main flow:
        initialize()\n
        \* process(ast_token)\n
        \* clean()\n
        save(report_obj)\n
        finish()\n
        \*: for each AST token
    """

    # This method sets the args and should not be overriden
    #  (override 'initialize' method instead for initialization purposes)
    def __init__(self, args):
        """It sets the args

        Arguments:
            args (list): arguments which will be used by those modules which
                implements this class.
        """

        self.args = args

    # This method loads the args and initializes the module
    @abstractmethod
    def initialize(self):
        """It loads the args an initializes the module."""

    # This method process each token
    @abstractmethod
    def process(self, token):
        """It process each AST token."""

    # This method will be invoked before the next token is processed
    @abstractmethod
    def clean(self):
        pass

    # This method will be invoked after all tokens have been processed
    # This method has the responsibility of update the records in the given report
    @abstractmethod
    def save(self, report):
        pass

    # This method will be invoked when all the tokens have been processed
    @abstractmethod
    def finish(self):
        pass
