
"""BOA module to check functions match according to rules.

This module goal is to look for unsafe functions that should
be avoided or generally are misused.
"""

# Javalang libs
import javalang

# Own libs
from boam_abstract import BOAModuleAbstract
from own_exceptions import BOAModuleException
from constants import Meta
from util import eprint

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
        self.threats = []

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
        #if isinstance(token, FuncCall):
        #    self.javalang_funccall(token)
        #print(token["ast"].types)
        for path, node in token["ast"]:
            #print(type(node))
            if isinstance(node, javalang.tree.MethodInvocation):
                #print(node.qualifier)
                #print(node.member)
                self.javalang_funccall(node)

    def clean(self):
        """It does nothing.
        """

    def save(self, report):
        """It appends the found threats.

        Arguments:
            report: Report instante to save all the found threats.
        """
        index = 0

        for threat in self.threats:
            severity = report.get_severity_enum_instance_by_who(self.who_i_am)

            if severity is None:
                eprint(f"Error: could not append the threat record #{index} in '{self.who_i_am}'. Wrong severity enum instance.")
            else:
                severity = severity[threat[2]]
                rtn_code = report.add(threat[0], threat[1], severity, threat[3], threat[4], threat[5])

                if rtn_code != Meta.ok_code:
                    eprint(f"Error: could not append the threat record #{index} (status code: {rtn_code}) in '{self.who_i_am}'.")

            index += 1

    def finish(self):
        """It does nothing.
        """

    def javalang_funccall(self, token):
        # Get the calling function name
        function_name = token.member

        if function_name in self.all_methods_name:
            index = self.all_methods_name.index(function_name)
            row = token.position.line
            col = token.position.column
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
                eprint(f"Warning: could not append a threat in '{self.who_i_am}'.")
