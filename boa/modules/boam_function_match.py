
"""BOA module to check functions match according to rules.

This module goal is to look for unsafe functions that should
be avoided or generally are misused.
"""

# Own libs
from boam_abstract import BOAModuleAbstract
from own_exceptions import BOAModuleException

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
            BOAModuleException: when a module is imported more than once.
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

        Todo:
            Right now there is a print message to warn about a match (remove it).
            When Reports are implemented, use the report instance to save all the
            matchs.
            Use a data structure to save the found threats for later report it
            with Reports in the save() method.

        Arguments:
            token: AST node.
        """
        if str(type(token)) == "<class 'pycparser.c_ast.FuncCall'>":
            function_name = token.name.name

            if function_name in self.all_methods_name:
                index = self.all_methods_name.index(function_name)
                row = str(token.coord).split(':')[-2]
                col = str(token.coord).split(':')[-1]
                severity = self.all_methods_reference[index]["severity"]
                description = self.all_methods_reference[index]["description"]

                print(f"{self.__class__.__name__}: {function_name}:{row}:{col} -> {severity} -> {description}")

    def clean(self):
        """It does nothing.
        """

    def save(self, report):
        """It does nothing.

        Todo:
            When Reports are implemented, use this method to save the
            found threats.

        Arguments:
            report: Report instante to save all the found threats.
        """

    def finish(self):
        """It does nothing.
        """
