"""This module creates a basic CFG only containing function calls.
"""

# Pycparser libs
import pycparser.c_ast as ast

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from util import eprint, is_key_in_dict
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
from auxiliary_modules.pycparser_cfg import CFG
import auxiliary_modules.pycparser_util as pycutil

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

        #print(function_invoked_by)

        for function_name, invoked in function_invoked_by.items():
            self.process_cfg.resolve_succs(function_name, invoked)

        #graph = self.process_cfg.basic_cfg
        #self.display_graph(graph)

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
        """It process a concrete function for the CFG.
        It completes the CFG incrementally.

        Parameters:
            function_name (str): function name.
            function (pycparser.c_ast.FuncDef): code of the function.
        """
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

        # Append first instruction (it should be FuncDef)
        self.basic_cfg.append_instruction(function_name, function)

        # Append the rest of instructions
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

    def resolve_succs_return_calls(self, from_function_name, to_function_name,
                                   instruction):
        """It resolves the *FuncCall* to functions which have
        the Return statment recursevely. Also, it resolves
        the invocations from one method to another recursively.

        Parameters:
            from_function_name (str): function which contains
                the Return statement or, because of recursion,
                other *FuncCall*.
            to_function_name (str): function which invokes to
                *from_function_name* function.
            instruction (pycparser.c_ast.Node): instruction which
                is going to be linked from *from_function_name*
                to *to_function_name*.
        """
        print(" ********************************** YOU'RE IN")
        from_function_instructions_cfg = self.basic_cfg.get_cfg(from_function_name)
        to_function_instructions_cfg = self.basic_cfg.get_cfg(to_function_name)
        to_function_instructions = list(map(lambda instr: instr.get_instruction(),
                                            to_function_instructions_cfg))
        func_call_instructions = pycutil.get_instructions_of_instance(\
                                    ast.FuncCall, to_function_instructions)

        #print("******************************")
        #print(f" * from: {from_function_name}")
        #print(f" * to: {to_function_name}")
        #print(f" * func call instrs: {list(map(lambda x: type(x), func_call_instructions))}")

        for fc_instruction in func_call_instructions:
            #print(f" ** {fc_instruction.name.name}")
            if fc_instruction.name.name == from_function_name:
                next_instruction = pycutil.get_real_next_instruction(\
                    to_function_instructions[0], fc_instruction)

                if next_instruction is None:
                    # Tail recursion optimization -> instead of return to the
                    #  original function which invoked the function, return to
                    #  function which continues the execution (recursively),
                    #  that is not the original because there is not next
                    #  instruction
                    function_invoked_by = self.basic_cfg.get_function_invoked_by()
                    #function_invoked_by = function_invoked_by[]
                    
                    #for invoke in function_invoked_by
                else:
                    to_function_index = list(map(lambda instr:
                                                 instr.get_instruction(),
                                                 self.basic_cfg.get_cfg\
                                                     (to_function_name)))\
                                                     .index(next_instruction)
                    from_function_index = list(map(lambda instr:
                                                   instr.get_instruction(),
                                                   self.basic_cfg.get_cfg\
                                                       (from_function_name)))\
                                                       .index(instruction)
                    #print(f" ** to_function_index: {to_function_index}")
                    #print(f" ** from_function_index: {from_function_index}")
                    #print(f" ** function: {to_function_name}")
                    #print(f" ** instruction: {to_function_instructions_cfg[to_function_index].get_type()}")
                    #print(f" ** function: {from_function_name}")
                    #print(f" ** instruction: {from_function_instructions_cfg[from_function_index].get_type()}")
                    from_function_instructions_cfg[from_function_index]\
                        .append_succ(to_function_instructions_cfg\
                                        [to_function_index])


    def resolve_succs_return(self, function_name, rtn_instruction,
                             function_instructions, function_invoked_by):
        """It resolves the successive instructions of a
        return statement and all the dependencies.

        Parameters:
            function_name (str): name of the function which contains
                the Return statement.
            rtn_instruction (pycparser_cfg.Instruction): return instruction.
            function_instructions (list): list of instructions of
                the function which contains the Return statement.
                The type is *pycparser_cfg.Instruction*.
            function_invoked_by (list): list of function which
                invokes the function which contains the Return statement.
        """
        real_instruction = rtn_instruction.get_instruction()
        rtn_instrs = pycutil.get_instruction_path(real_instruction)
        index = function_instructions.index(rtn_instruction)
        instr_to_functions = real_instruction   # Function which its succs are
                                                #  other functions

        # The Return instruction is the only one without
        #  successive instruction
        if len(rtn_instrs) != 0:
            rtn_instruction.append_succ(function_instructions[index + 1])

            instr_to_functions = rtn_instrs[-1]

        for invoke in function_invoked_by:
            self.resolve_succs_return_calls(function_name, invoke,
                                            instr_to_functions)
            #rtn_instrs[-1].append_succ(
            #    self.basic_cfg.get_cfg(invoke)[0])

    def resolve_succs(self, function_name, function_invoked_by):
        """It resolves the successives instructions of
        a concrete function.

        Arguments:
            function_name (str): function.
            function_invoked_by (list): functions which
                invokes *function*.
        """
        instructions = self.basic_cfg.get_cfg(function_name)

        print(f" -------------{'-' * len(function_name)}---")
        print(f" -- Function: {function_name} --")
        print(f" -------------{'-' * len(function_name)}---")

        index = 0

        while index < len(instructions):
            instruction = instructions[index]
            real_instruction = instruction.get_instruction()

            print(f" -- Instruction: {instruction.get_type()}")
            if instruction.get_type() in self.branching_instr:
                if isinstance(real_instruction, ast.Return):
                    print("-- RETURN --")
                    print("------------")

                    self.resolve_succs_return(function_name, instruction,
                                              instructions, function_invoked_by)
            else:
                # Normal instruction (not branching)
                if index + 1 != len(instructions):
                    # Is not the last instruction
                    instruction.append_succ(instructions[index + 1])
                else:
                    # Is the last instruction -> successive instruction will
                    #  be the function which invokes to the current function
                    pass

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
