
# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from util import eprint, is_key_in_dict
from lifecycles.auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor

# Pycparser libs
from pycparser.c_ast import FuncDef
from pycparser.c_ast import FuncCall

class BOAModuleControlFlowGraph(BOAModuleAbstract):

    def initialize(self):
        self.threats = []
        self.function = {}
        self.cfg = {}

        #self.threats.append((self.who_i_am, "desc1", "CRITICAL", "adv1", 5, None))

    def compute_function_cfg(self, function_name, function):
        """It computes the CFG for a function.

        Arguments:
            function_name (str): function name.
            function (pycparser.c_ast.Decl): code of the function.
        """
        visitor = PreorderVisitor(self.compute_function_cfg_callback)

        # It checks that self.compute_function_cfg_function does not exist
        try:
            self.compute_function_cfg_function

            eprint("Error: variable 'self.compute_function_cfg_function' should not exist.")

            return
        except:
            self.compute_function_cfg_function = function_name

        visitor.visit(function)

        # Remove self.compute_function_cfg_function
        del self.compute_function_cfg_function

    def compute_function_cfg_callback(self, node):
        # It checks if self.compute_function_cfg_function exists
        try:
            self.compute_function_cfg_function
        except:
            eprint("Error: variable 'self.compute_function_cfg_function' should exist.")

        if isinstance(node, FuncCall):
            # Create a list if no element was inserted before
            if not is_key_in_dict(self.cfg, self.compute_function_cfg_function):
                self.cfg[self.compute_function_cfg_function] = []

            # Insert element in list
            self.cfg[self.compute_function_cfg_function].append(node.name.name)

    def process(self, token):
        if isinstance(token, FuncDef):
            function = token
            function_name = function.decl.name

            # Store the declaration identified by name
            self.function[function_name] = function

            self.compute_function_cfg(function_name, function)

    def clean(self):
        pass

    def save(self, report):
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
        print(f"Total function definitions: {len(self.function)}")

        for key, value in self.cfg.items():
            print(f"cfg['{key}'] = {value}")
