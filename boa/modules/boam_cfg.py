"""This module creates a basic CFG only containing function calls.
"""

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from util import eprint, is_key_in_dict
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
from auxiliary_modules.pycparser_cfg import CFG

# Pycparser libs
import pycparser.c_ast as ast

class BOAModuleControlFlowGraph(BOAModuleAbstract):
    """It defines the necessary functions to create the CFG.
    """

    def initialize(self):
        """It initialices the class.
        """
        #self.functions = {}
        self.process_cfg = ProcessCFG()

    def process(self, token):
        if isinstance(token, ast.FuncDef):
            function = token
            function_name = function.decl.name

            # Store the declaration identified by name
            #self.functions[function_name] = function

            self.process_cfg.process(function_name, function)

    def clean(self):
        """It does nothing.
        """

    def save(self, report):
        """It does nothing
        """

    def display_graph(self, graph):
        """It displays the graph iterating over it.

        Arguments:
            graph (CFG): graph.
        """
        print("****************************************")
        print("****************************************")
        print("****************************************")

        for function in graph.get_function_calls():
            print(f"---{'-' * len(function)}---")
            print(f"-- {function} --")
            print(f"---{'-' * len(function)}---")
            print()

            for instruction in graph.get_cfg(function):
                print(f"-- {instruction.get_type()} --")
                for dependency in instruction.get_succs():
                    print(f"** {dependency.get_type()} **")
                    for inner_function in graph.get_function_calls():
                        try:
                            print(f"{graph.get_cfg(inner_function).index(dependency)}"
                                  f" in '{inner_function}'.")
                        except:
                            pass

                print()

    def finish(self):
        """It resolves the succs of the instructions.
        """
        function_calls = self.get_function_calls()
        function_invoked_by = self.process_cfg.get_function_invoked_by()

        print(function_invoked_by)

        for function, invoked in function_invoked_by.items():
            self.process_cfg.solve_succs(function, invoked)

        graph = self.process_cfg.basic_cfg

        self.display_graph(graph)

    def get_function_calls(self):
        """It returns a graph with the function calls
        which have been found in the program.

        Returns:
            dict: function calls graph
        """
        return self.process_cfg.get_function_calls()

    def get_basic_cfg(self):
        """It returns the basic CFG. Basic blocks (bb)
        are not being used in this basic CFG. The way
        it has been built is instruction by instruction.

        Returns:
            dict: basic CFG
        """
        return self.process_cfg.get_basic_cfg()

class ProcessCFG():

    def __init__(self):
        self.basic_cfg = CFG()
        self.funcion_calls = {}
        self.branching_instr = [ast.FuncCall, ast.If, ast.For, ast.While,
                                ast.DoWhile, ast.Goto, ast.Switch, ast.Break,
                                ast.Continue, ast.Return]

    def process(self, function_name, function):
        self.compute_function_cfg(function_name, function)

    def compute_function_cfg(self, function_name, function):
        """It computes the CFG for a function.

        Arguments:
            function_name (str): function name.
            function (pycparser.c_ast.FuncDef): code of the function.
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

        # Even if there was any function call, the node has to be in the graph
        if not function_name in self.funcion_calls.keys():
            # There was any function call and we create the node
            self.funcion_calls[function_name] = []
            self.basic_cfg.append_function_call(function_name, None)

        # Remove self.compute_function_cfg_function
        del self.compute_function_cfg_function

    def compute_function_cfg_callback(self, node):
        """Callback which will be invoked from the PreorderVisitor.

        Arguments:
            node: AST node.
        """
        # It checks if self.compute_function_cfg_function exists
        try:
            self.compute_function_cfg_function
        except Exception:
            eprint("Error: variable 'self.compute_function_cfg_function' should exist.")

        current_function_name = self.compute_function_cfg_function

        if isinstance(node, ast.FuncCall):
            # Create a list if no element was inserted before
            if not is_key_in_dict(self.funcion_calls, current_function_name):
                self.funcion_calls[current_function_name] = []
                #self.basic_cfg[current_function_name] = []
                self.basic_cfg.append_function_call(current_function_name, None)

            # Insert element in list
            self.funcion_calls[current_function_name].append(node.name.name)
            #self.basic_cfg[current_function_name].append(node)
            self.basic_cfg.append_function_call(current_function_name,
                                                node.name.name)

        # Append instruction
        self.basic_cfg.append_instruction(current_function_name, node)

    def solve_succs(self, function, function_invoked_by):
        """It solves the successives instructions of
        a concrete function.

        Arguments:
            function (str): function.
            function_invoked_by (list): functions which
                invokes *function*.
        """
        instructions = self.basic_cfg.get_cfg(function)
        visitor = PreorderVisitor()

        print(f" -------------{'-' * len(function)}---")
        print(f" -- Function: {function} --")
        print(f" -------------{'-' * len(function)}---")

        index = 0

        while index < len(instructions):
            instruction = instructions[index]
            real_instruction = instruction.get_instruction()

            print(f" -- Instruction: {instruction.get_type()}")
            if instruction.get_type() in self.branching_instr:
                if index + 1 != len(instructions):
                    # Is not the last instruction
                    if isinstance(real_instruction, ast.Return):
                        print("-- RETURN --")
                        print(real_instruction.children())
                        print(len(real_instruction.children()))
                        print("------------")

                        rtn_instr = visitor.visit_and_return_path(real_instruction)

                        # The Return instruction is the only one without
                        #  successive instruction
                        instruction.append_succ(instructions[index + 1])

                        # We have to change the successive instruction of
                        #  last instruction of Return to those function which
                        #  execute the current function
                        #instructions
                else:
                    # Is the last instruction -> successive instruction will
                    #  be the function which invokes to the current function
                    if isinstance(real_instruction, ast.Return):
                        print("-- RETURN --")
                        print(len(real_instruction.children()))
                        print("------------")
            else:
                # Normal instruction (not branching)
                if index + 1 != len(instructions):
                    # Is not the last instruction
                    instruction.append_succ(instructions[index + 1])
                else:
                    # Is the last instruction -> successive instruction will
                    #  be the function which invokes to the current function
                    for invoke in function_invoked_by:
                        instruction.append_succ(self.basic_cfg.get_cfg(invoke)[0])

            index += 1

    def get_basic_cfg(self):
        """It returns the basic CFG. Basic blocks (bb)
        are not being used in this basic CFG. The way
        it has been built is instruction by instruction.

        Returns:
            dict: basic CFG
        """
        return self.basic_cfg

    def get_function_calls(self):
        """It returns a graph with the function calls
        which have been found in the program.

        Returns:
            dict: function calls graph
        """
        return self.basic_cfg.get_function_calls()

    def get_function_invoked_by(self):
        """It returns the information about which functions invoked
        a concrete function.

        Returns:
            dict: functions which invokes a concrete function
        """
        return self.basic_cfg.get_function_invoked_by()
