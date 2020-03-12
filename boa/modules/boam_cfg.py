"""This module creates a basic CFG only containing function calls.
"""

# Std libs
import sys

# Pycparser libs
import pycparser.c_ast as ast

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from util import eprint, is_key_in_dict, get_just_type
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
import auxiliary_modules.pycparser_cfg as cfg
import auxiliary_modules.pycparser_util as pycutil
from own_exceptions import BOAModuleException

class CFGConstants:
    """Class which contains the necessary constants
    for working with the CFG.
    """
    exit_functions = ["exit"]   # Append the ones you need

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

    def display_graph(self, graph, show_only_return_and_end_rel=False):
        """It displays the graph iterating over it.

        Arguments:
            graph (CFG): graph.
            show_only_return_and_end_rel (bool): if *True*, it
                will show only the relations between different
                functions, return statement and last statement.
                This option can lead to false positives when
                using recursion.
        """
        for function in graph.get_function_calls():
            print()
            print(f"---{'-' * len(function)}---")
            print(f"-- {function} --")
            print(f"---{'-' * len(function)}---")
            print()

            index = 0
            instructions = graph.get_cfg(function)
            is_return = False
            return_instrs = []

            for instruction in instructions:
                if isinstance(instruction.get_instruction(), ast.Return):
                    is_return = True
                    return_instrs = pycutil.get_instruction_path(instruction.get_instruction())
                    print("**** RETURN ****")
                    print()
                elif (is_return and instruction.get_instruction() not in return_instrs):
                    is_return = False
                    return_instrs = []
                    print("****************")

                print(f"-- {index} {get_just_type(None, instruction.get_type())} --")

                for dependency in instruction.get_succs():
                    if not show_only_return_and_end_rel:
                        print(f"** {get_just_type(None, dependency.get_type())} **")
                    for inner_function in graph.get_function_calls():
                        try:
                            if not show_only_return_and_end_rel:
                                print(f"{graph.get_cfg(inner_function).index(dependency)}"
                                      f" in '{inner_function}'.")
                                print()
                            elif (inner_function != function or
                                  is_return or
                                  index + 1 == len(instructions)):
                                graph.get_cfg(inner_function).index(dependency)
                                print(f"** {get_just_type(None, dependency.get_type())} **")
                                print(f"** {graph.get_cfg(inner_function).index(dependency)}"
                                      f" in '{inner_function}' **")
                                print()
                        except:
                            pass
                index += 1

    def finish(self):
        """It resolves the succs of the instructions.
        """
        function_invoked_by = self.process_cfg.get_function_invoked_by()

        # Resolve special nodes

        # Special node: end of function
        self.process_cfg.append_end_of_function_nodes()

        # Special node: functions not invoked
        #self.process_cfg.resolve_functions_not_invoked()

        # Special node: end of graph (e.g. last instruction in main,
        #  exit(), ...)
        self.process_cfg.resolve_end_of_graph_nodes()

        # Resolve dependencies (successive instructions)
        for function_name, invoked in function_invoked_by.items():
            self.process_cfg.resolve_succs(function_name, invoked)

        # Resolve those dependencies which could not be resolved before
        #  for some reason
        self.process_cfg.resolve_broken_succs()

        graph = self.process_cfg.basic_cfg
        self.display_graph(graph, False)

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
        self.basic_cfg = cfg.CFG()
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
                self.basic_cfg.append_function_call(current_function_name, None)

            # Insert element in list
            self.funcion_calls[current_function_name].append(node.name.name)
            self.basic_cfg.append_function_call(current_function_name,
                                                node.name.name)

        # Append instruction
        self.basic_cfg.append_instruction(current_function_name, node)

    def resolve_succs_return_calls(self, from_function_name, to_function_name,
                                   first_from_function_name, instruction,
                                   recursion_functions_list, force_next_real_instr=True):
        """It resolves the *FuncCall* to functions which have
        the Return statment recursevely. Also, it resolves
        the invocations from one method to another recursively.

        Parameters:
            from_function_name (str): function which contains
                the Return statement or, because of recursion,
                other *FuncCall*.
            to_function_name (str): function which invokes to
                *from_function_name* function.
            first_from_function_name (str): function which contains
                the Return statement or, because of recursion,
                other *FuncCall*. It is not modified when doing
                recursion.
            instruction (pycparser.c_ast.Node): instruction which
                is going to be linked from *from_function_name*
                to *to_function_name*.
            recursion_functions_list (list): list of *tuple* which
                contains (*from_function_name*, *to_function_name*,
                *first_from_function_name*) in order to detect
                infinite loops and stop them (e.g. f(){g();} g()
                {f();})
            force_next_real_instr (bool): if *True*, which is the
                default value, it will take the next real instruction
                of *instruction* to append the dependencie. If *False*,
                the *instruction* itself will be used. This parameter
                is used with *recursion_functions_list* to avoid infinite
                loops.
        """
        to_function_instructions_cfg = self.basic_cfg.get_cfg(to_function_name)
        to_function_instructions = list(map(lambda instr: instr.get_instruction(),
                                            to_function_instructions_cfg))
        func_call_instructions = pycutil.get_instructions_of_instance(\
                                    ast.FuncCall, to_function_instructions)

        for fc_instruction in func_call_instructions:
            # Find the instruction that is making the func call
            #  to *from_function_name*
            if fc_instruction.name.name == from_function_name:
                # FuncCall in *to_function_name* to *from_function_name* found

                if force_next_real_instr:
                    next_instruction = pycutil.get_real_next_instruction(\
                        to_function_instructions[0], fc_instruction)
                else:
                    next_instruction = fc_instruction

                if next_instruction is None:
                    # Tail recursion optimization -> instead of return to the
                    #  original function which invoked the function, return to
                    #  function which continues the execution (recursively),
                    #  that is not the original because there is not next
                    #  instruction
                    function_invoked_by = self.basic_cfg.get_function_invoked_by()
                    function_invoked_by = function_invoked_by[to_function_name]
                    instructions = pycutil.get_instruction_path(fc_instruction)
                    index = to_function_instructions.index(instructions[-1])

                    for invoke in function_invoked_by:
                        if invoke == to_function_name:
                            # Recursion detected. We have to avoid infinite loop
                            to_function_instructions_cfg[index].remove_all_succs()

                            # Get the body of the function
                            compound =\
                            pycutil.get_instructions_of_instance(ast.Compound,
                                                                 to_function_instructions)

                            if len(compound) != 0:
                                # Try to get the first instruction of the function

                                first_compound_element = compound[0].block_items
                                if compound[0].block_items is not None:
                                    first_compound_element = compound[0].block_items[0]

                                # Append the first instruction or the 'Compound' element
                                to_function_instructions_cfg[index].append_succ(
                                    to_function_instructions_cfg
                                    [to_function_instructions.index(first_compound_element)])
                        else:
                            # Resolve recursively the dependencies that are not recursion
                            current_recursion_functions = [(to_function_name, invoke,
                                                            first_from_function_name)]
                            force_next_real_instr_aux = True

                            if current_recursion_functions[0] in recursion_functions_list:
                                # Avoiding infinite loop: stop taking the next instruction
                                #  because it is in the same function itself or in a loop
                                #  of functions
                                force_next_real_instr_aux = False

                            self.resolve_succs_return_calls(to_function_name, invoke,
                                                            first_from_function_name,
                                                            instruction,
                                                            recursion_functions_list +
                                                            current_recursion_functions,
                                                            force_next_real_instr_aux
                                                            )
                else:
                    # There is next instruction, so append it to 'instruction'
                    # Get indexes to append
                    to_function_index = list(map(lambda instr:
                                                 instr.get_instruction(),
                                                 self.basic_cfg.get_cfg\
                                                     (to_function_name)))\
                                                     .index(next_instruction)
                    from_function_index = list(map(lambda instr:
                                                   instr.get_instruction(),
                                                   self.basic_cfg.get_cfg\
                                                       (first_from_function_name)))\
                                                       .index(instruction)

                    # Get initial function where we have to append the jump
                    from_function_instructions_cfg = self.basic_cfg.get_cfg\
                                                         (first_from_function_name)

                    if (from_function_instructions_cfg[from_function_index] ==\
                        to_function_instructions_cfg[to_function_index] and
                            to_function_name == from_function_name):
                        # Recursion and attempt of insert a dependency of itself
                        from_function_instructions = list(map(lambda x: x.get_instruction(),
                                                              from_function_instructions_cfg))
                        compound = pycutil.get_instructions_of_instance(
                            ast.Compound,
                            from_function_instructions)

                        if len(compound) == 0:
                            raise BOAModuleException("could not get the 'Compound' element"
                                                     " when a dependency tried to be dependent"
                                                     " of itself", self)

                        if compound[0].block_items is None:
                            to_function_index =\
                                from_function_instructions.index(compound[0])
                        else:
                            to_function_index =\
                                from_function_instructions.index(compound[0].block_items[0])

                    # Append the jump
                    from_function_instructions_cfg[from_function_index]\
                        .append_succ(to_function_instructions_cfg\
                                        [to_function_index])

    def resolve_functions_not_invoked(self):
        """It resolves the functions which are not invoked.
        For that purpose, we append a node to those functions
        to know that we are in that situation and make
        easier the dependencies resolution.
        """
        function_invoked_by = self.get_function_invoked_by()

        for function_name, invoked_by in function_invoked_by.items():

            if function_name == "main":
                # Main function is always invoked
                continue

            if len(invoked_by) == 0:
                # This function is not being invoked
                instructions = list(map(lambda instr: instr.get_instruction(),
                                        self.basic_cfg.get_cfg(function_name)))
                not_invoked_node = cfg.NotInvoked()

                if not pycutil.append_element_to_function(not_invoked_node,
                                                          func_def=instructions[0]):
                    eprint(f"Warning: could not insert 'NotInvoked' node in '{function_name}'.")
                    continue

                self.basic_cfg.append_instruction(function_name,
                                                  not_invoked_node)

    def append_end_of_function_nodes(self):
        """It appends the special node *EndOfFunc* to avoid
        problems with recursion when resolving CFG.

        Example:
            The following code would cause an infinite loop
            if the node *EndOfFunc* was not appended.

            void foo()
            {
                bar();
            }

            void bar()
            {
                foo();
            }
        """
        functions = self.get_function_calls()

        for function_name in functions.keys():
            function_cfg = self.basic_cfg.get_cfg(function_name)
            function = list(map(lambda x: x.get_instruction(), function_cfg))
            end_of_func = cfg.EndOfFunc()

            if not pycutil.append_element_to_function(end_of_func, func_def=function[0]):
                eprint(f"Warning: could not insert 'EndOfFunc' node in '{function_name}'.")
                continue

            self.basic_cfg.append_instruction(function_name, end_of_func)

    def resolve_end_of_graph_nodes(self):
        """It resolves those nodes which are the end of
        our CFG (e.g. last instruction of main, exit(), ...).
        """
        functions = self.basic_cfg.get_cfg(None)

        for function_name, instructions in functions.items():
            instructions_pyc = list(map(lambda x: x.get_instruction(),
                                        instructions))

            # Main function
            if function_name == "main":
                end_of_graph_node = cfg.FinalNode()

                if not pycutil.append_element_to_function(end_of_graph_node,
                                                          func_def=instructions_pyc[0]):
                    eprint(f"Warning: could not insert 'FinalNode' node in '{function_name}'.")
                    continue

                self.basic_cfg.append_instruction(function_name, end_of_graph_node)

            last_compound = None

            # Exit functions
            for instr in instructions_pyc:
                if isinstance(instr, ast.Compound):
                    last_compound = instr
                elif (isinstance(instr, ast.FuncCall) and
                      instr.name.name in CFGConstants.exit_functions):
                    if last_compound is None:
                        eprint("Warning: trying to append a 'FinalNode', but"
                               " no 'Compound' was found (exit function out"
                               " of a function?).")

                    end_of_graph_node = cfg.FinalNode()
                    pycutil.append_element_to_function(end_of_graph_node,
                                                       func_def=instructions_pyc[0])
                    instr_position = -1
                    func_call_instrs =\
                        pycutil.get_real_next_instruction(instructions_pyc[0],
                                                          instr)

                    if func_call_instrs is not None:
                        instr_position = instructions_pyc.index(func_call_instrs)

                     # It appends the new node
                    self.basic_cfg.append_instruction(function_name,
                                                      end_of_graph_node,
                                                      instr_position)

    def resolve_broken_succs(self):
        """It resolves those dependencies which could not
        be resolved before because of complexity.
        """
        functions = self.basic_cfg.get_cfg(None)

        for function_name, instructions in functions.items():
            types = list(map(lambda x: x.get_type(), instructions))
            instructions_pyc = list(map(lambda x: x.get_instruction(),
                                        instructions))

            # Resolve dependencies of functions that are not invoked
            if cfg.NotInvoked in types:
                previous_instr = None

                for instr in instructions_pyc:
                    if (isinstance(instr, cfg.NotInvoked) and
                            isinstance(previous_instr, ast.Return)):
                        # Structure found: [Return, NotInvoked]
                        # Append dependencie from Return to NotInvoked
                        index = instructions_pyc.index(previous_instr)
                        instructions[index].append_succ(instructions[index + 1])

                    previous_instr = instr

                continue

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
                                            function_name, instr_to_functions,
                                            [(function_name, invoke, function_name)])
            #rtn_instrs[-1].append_succ(
            #    self.basic_cfg.get_cfg(invoke)[0])

        if len(rtn_instruction.get_succs()) == 0:
            # The return statement does not have dependencies yet
            #  so append the next instruction if possible as dependency
            index = function_instructions.index(rtn_instruction)

            if index + 1 != len(function_instructions):
                rtn_instruction.append_succ(function_instructions[index + 1])

    def resolve_succs(self, function_name, function_invoked_by):
        """It resolves the successives instructions of
        a concrete function.

        Arguments:
            function_name (str): function.
            function_invoked_by (list): functions which
                invokes *function*.
        """
        instructions = self.basic_cfg.get_cfg(function_name)

        #print(f" -------------{'-' * len(function_name)}---")
        #print(f" -- Function: {function_name} --")
        #print(f" -------------{'-' * len(function_name)}---")

        if instructions is None:
            #print(" -- Not present (C library?)")
            return

        index = 0

        while index < len(instructions):
            instruction = instructions[index]
            real_instruction = instruction.get_instruction()

            #print(f" -- Instruction: {instruction.get_type()}")
            if instruction.get_type() in self.branching_instr:
                if isinstance(real_instruction, ast.Return):
                    self.resolve_succs_return(function_name, instruction,
                                              instructions, function_invoked_by)
            else:
                # Normal instruction (not branching)
                if isinstance(real_instruction, cfg.FinalNode):
                    # The end of the graph must not have successive instructions
                    index += 1
                    continue

                if index + 1 != len(instructions):
                    # Is not the last instruction
                    if len(instruction.get_succs()) == 0:
                        # If contains previous dependencies, this default
                        #  appendinness should not happen
                        instruction.append_succ(instructions[index + 1])
                else:
                    # Is the last instruction -> successive instruction will
                    #  be the function which invokes to the current function
                    self.resolve_succs_return(function_name, instruction,
                                              instructions, function_invoked_by)

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
