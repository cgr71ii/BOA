
"""BOA module to check functions match according to rules.

This module goal is to look for unsafe functions that should
be avoided or generally are misused.
"""

# Std libs
import logging

# 3rd libs
from pycparser.c_ast import FuncCall

# Own libs
from boam_abstract import BOAModuleAbstract
from exceptions import BOAModuleException
from constants import Meta

class BOAModuleFunctionMatch(BOAModuleAbstract):
    """BOAModuleFunctionMatch class. It implements the class BOAModuleAbstract.

    This class implements the general lifecycle which uses an AST to
    handle the functions match.
    """

    def initialize(self):
        """It initializes the module.

        It creates 2 lists to iterate throught them after. These lists
        are created at the same time to have a concrete order. The goal
        of this is to avoid to iterate over all the dictionaries that
        are created in the rules file (rules file uses dictionaries to define
        dangerous functions to increasing the readibility of the rules)
        every time that a new AST token is processed.

        Raises:
            BOAModuleException: when a method is defined more than once
                in the arguments.
        """
        self.all_methods_name = []
        self.all_methods_reference = []

        for method in self.args["methods"]:
            method_name = method["method"]

            if method_name in self.all_methods_name:
                raise BOAModuleException(f"method '{method_name}' duplicated in rules", self)

            self.all_methods_name.append(method_name)
            self.all_methods_reference.append(method)

    def process(self, token):
        """It processes an AST node.

        It looks if the AST node is a function call and if so,
        it checks if it is one of the dangerous functions defined
        in the rules file.

        Arguments:
            token: AST node.
        """
        # Look for function calls
        if isinstance(token, FuncCall):
            self.pycparser_funccall(token)

    def clean(self):
        """It does nothing.
        """

    def finish(self):
        """It does nothing.
        """

    def pycparser_funccall(self, token):
        # Get the calling function name
        function_name = token.name.name

        if function_name in self.all_methods_name:
            index = self.all_methods_name.index(function_name)
            row = str(token.coord).split(':')[-2]
            col = str(token.coord).split(':')[-1]
            severity = None
            description = None
            advice = None
            append = True

            try:
                severity = self.all_methods_reference[index]["severity"]
                description = self.all_methods_reference[index]["description"]
                advice = self.all_methods_reference[index]["advice"]
            except KeyError:
                if (severity is None or description is None):
                    append = False

            if append:
                self.threats.append((self.who_i_am,
                                     description,
                                     severity,
                                     advice,
                                     int(row),
                                     int(col)))
            else:
                logging.warning("could not append a threat in '%s'", self.who_i_am)
