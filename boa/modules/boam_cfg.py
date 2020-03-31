"""This module creates a basic CFG only containing function calls.
"""

# Std libs
import sys
from copy import deepcopy
import random

# Pycparser libs
import pycparser.c_ast as ast

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from util import eprint, is_key_in_dict, get_just_type, get_name_from_class_instance
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
import auxiliary_modules.pycparser_cfg as cfg
import auxiliary_modules.pycparser_util as pycutil
from own_exceptions import BOAModuleException

__matplotlib_loaded__ = False

try:
    import matplotlib.pyplot as plt
    __matplotlib_loaded__ = True
except ModuleNotFoundError as e:
    print(f"Info: BOAModuleControlFlowGraph: {e}.")
except ImportError as e:
    print(f"Info: BOAModuleControlFlowGraph: {e}.")

class CFGConstants:
    """Class which contains the necessary constants
    for working with the CFG.
    """
    branching_instr = (ast.FuncCall, ast.If, ast.For, ast.While,
                       ast.DoWhile, ast.Goto, ast.Switch, ast.Break,
                       ast.Continue, ast.Return)

    exit_functions = ["exit"]   # Append the ones you need
    default_recursion_limit = 1000

    # Plot constants
    x_initial = 1.0             # Where the first function is plotted in x coordinate
    y_initial = 1.0             # Where the first instruction is plotted in y coordinate
    x_increment = 0.5           # Distance between instructions in x coordinate
    y_increment = 10.0          # Distance between instructions in y coordinate
    funcs_distance = 1.0        # Distance between functions
    max_plot_x_offset = 0.05    # Max x coordinate offset if applied
                                #  It should be lesser than x_increment in order to avoid
                                #  problems with visualization, but it will work anyways
    max_plot_y_offset = 5.0     # Max y coordinate offset if applied.
                                #  It should be lesser than y_increment in order to avoid
                                #  problems with visualization, but it will work anyways

class BOAModuleControlFlowGraph(BOAModuleAbstract):
    """It defines the necessary functions to create the CFG.
    """

    def initialize(self):
        """It initialices the class.
        """
        # Check if a recursion limit was specified
        if is_key_in_dict(self.args, "recursion_limit"):
            recursion_limit = CFGConstants.default_recursion_limit

            try:
                recursion_limit = int(self.args["recursion_limit"])
            except ValueError:
                raise BOAModuleException("the argument 'recursion_limit' has to"
                                         " have a numeric value (check your rules"
                                         " file)", self)

            sys.setrecursionlimit(recursion_limit)

        # Arguments from rules file
        # Plot
        self.display_cfg = False
        self.plot_cfg = False
        self.lines_clip = True
        self.random_x_offset = False
        self.random_y_offset = False
        # Other
        self.propagate_func_call = True

        # Check and set the rules from the rules file
        self.check_and_set_args()

        self.process_cfg = ProcessCFG(self.propagate_func_call)
        self.is_matplotlib_loaded = __matplotlib_loaded__

    def check_and_set_args(self):
        """It checks if the arguments from the rules file are correct and, if
        any of the allowed rules are defined, it sets the value which is set
        in the rules file.
        """
        if is_key_in_dict(self.args, "display_cfg"):
            if self.args["display_cfg"].lower() == "true":
                self.display_cfg = True
            elif self.args["display_cfg"].lower() != "false":
                raise BOAModuleException("the argument 'display_cfg' only allows"
                                         " the values 'true' or 'false'")

        if is_key_in_dict(self.args, "plot_cfg"):
            if self.args["plot_cfg"].lower() == "true":
                self.plot_cfg = True
            elif self.args["plot_cfg"].lower() != "false":
                raise BOAModuleException("the argument 'plot_cfg' only allows"
                                         " the values 'true' or 'false'")

        if is_key_in_dict(self.args, "lines_clip"):
            if self.args["lines_clip"].lower() == "false":
                self.lines_clip = False
            elif self.args["lines_clip"].lower() != "true":
                raise BOAModuleException("the argument 'lines_clip' only allows"
                                         " the values 'true' or 'false'")

        if is_key_in_dict(self.args, "random_x_offset"):
            if self.args["random_x_offset"].lower() == "true":
                self.random_x_offset = True
            elif self.args["random_x_offset"].lower() != "false":
                raise BOAModuleException("the argument 'random_x_offset' only allows"
                                         " the values 'true' or 'false'")

        if is_key_in_dict(self.args, "random_y_offset"):
            if self.args["random_y_offset"].lower() == "true":
                self.random_y_offset = True
            elif self.args["random_y_offset"].lower() != "false":
                raise BOAModuleException("the argument 'random_y_offset' only allows"
                                         " the values 'true' or 'false'")

        if is_key_in_dict(self.args, "propagate_func_call"):
            if self.args["propagate_func_call"].lower() == "false":
                self.propagate_func_call = False
            elif self.args["propagate_func_call"].lower() != "true":
                raise BOAModuleException("the argument 'propagate_func_call' only allows"
                                         " the values 'true' or 'false'")

    def process(self, token):
        """It process every FuncDef which is found.

        Arguments:
            token (pycparser.c_ast.Node): node from
                the AST.
        """
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

    def plot_graph(self, graph):
        """It plots the graph iterating over it.

        Arguments:
            graph (CFG): graph.
        """
        if not self.is_matplotlib_loaded:
            eprint("Warning: 'matplotlib' could not be loaded. It will not"
                   " be possible to plot the graph.")
            return

        # Variables for plotting
        # Instructions
        functions = []  # Function of the concrete instruction (x, y)
        x = []          # x coordinate of the instruction
        y = []          # y coordinate of the instruction
        txt = []        # Descriptive information to visualizate per instruction
        # Dependencies (its format is different throughout the process)
        x_line = []     # x coordinate of dependencies
                        #  final format: [x_origin, [x_dependency_1, ...]]
        y_line = []     # y coordinate of dependencies
                        #  final format: [y_origin, [y_dependency_1, ...]]

        function_x = CFGConstants.x_initial    # x coordinate of the current function

        fig, ax = plt.subplots()

        for function in graph.get_function_calls():
            index = 0
            instructions = graph.get_cfg(function)
            is_func_def = False
            func_instrs = []
            func_instrs_parents = {}

            # Offset variables to control the x and y coordinates
            function_y = CFGConstants.y_initial # Height of the instruction which is modified
                                                #  as an offset itself throughout the process
            max_deepness = 0                    # Max reached deepness in the current function
                                                #  in order to know how much width we need to
                                                #  add
            deepness = 0                        # Current deepness of the instruction to modify
                                                #  the width of the instruction itself

            for instruction in instructions:
                if isinstance(instruction.get_instruction(), ast.FuncDef):
                    # Initialize the necessary variables when a new function is reached
                    is_func_def = True
                    func_instrs = pycutil.get_instruction_path(instruction.get_instruction())
                    func_instrs.insert(0, instruction.get_instruction())
                    func_instrs_parents = pycutil.get_parents(func_instrs)
                elif (is_func_def and instruction.get_instruction() not in func_instrs):
                    # Reset the variables
                    is_func_def = False
                    func_instrs = []
                    func_instrs_parents = {}
                    deepness = 0
                elif is_func_def:
                    # Get the deepness in order to have a "good" visualization of the function
                    deepness = pycutil.get_deepness_level(instruction.get_instruction(),
                                                          func_instrs_parents,
                                                          instruction.get_instruction(),
                                                          func_instrs[0])
                    max_deepness = max(deepness, max_deepness)

                # Get the most verbose part of the instruction
                instr_type = get_just_type(None, instruction.get_type()).split(".")[2]

                # Store the necessary information for plot the instructions
                functions.append(function)
                x_offset = 0.0
                y_offset = 0.0

                # Check if the offset will be applied
                if self.random_x_offset:
                    sign = random.random()
                    x_offset = random.random() * CFGConstants.max_plot_x_offset

                    if sign < 0.5:
                        sign = 1
                    else:
                        sign = -1

                    x_offset *= sign
                if self.random_y_offset:
                    sign = random.random()
                    y_offset = random.random() * CFGConstants.max_plot_y_offset

                    if sign < 0.5:
                        sign = 1
                    else:
                        sign = -1

                    y_offset *= sign

                # Store the coordinates
                x.append(function_x +
                         deepness * CFGConstants.x_increment +
                         x_offset)  # deepness is used in order
                                    #  to plot the instructions
                                    #  in a way that can be
                                    #  "easily" visualized
                y.append(function_y + y_offset)

                # Store the origin of the instruction for, later, plot the dependencies (lines)
                x_line_aux = [x[-1]]
                y_line_aux = [y[-1]]

                # Set the text which is going to be visualized in each instruction
                txt.append(f"{function}.{instr_type}")

                for dependency in instruction.get_succs():
                    for inner_function in graph.get_function_calls():
                        try:
                            # Append the necessary information that will be necessary after
                            #  all the process is done in order to calculate the dependencies
                            #  and plot the lines. It is not done the calculus now because
                            #  there are instructions that are dependencies that have not been
                            #  reached yet. Once all those instructions are reached, which means
                            #  have finished the process, it will be possible to process the
                            #  dependencies and have the coordinates to plot the lines
                            dependency_index = graph.get_cfg(inner_function).index(dependency)
                            x_line_aux.append([inner_function, dependency_index])
                            x_line.append(x_line_aux)
                            y_line.append(y_line_aux)
                        except:
                            # Avoid the throwness of exceptions
                            pass

                function_y += CFGConstants.y_increment
                index += 1

            # Where a new function starts the x coordinate
            function_x += CFGConstants.funcs_distance + max_deepness * CFGConstants.x_increment

        index = 0

        # Now that all the instructions have been processed, we have all
        #  the necessary information for process the dependencies/lines
        while index < len(x_line):
            # x_lines = [origin_x, [target_function_1, index_1], [...], ...]
            target_dest = []

            # Get the coordinates of the dependencies
            for target in x_line[index][1:]:
                target_function = target[0]
                target_function_index = target[1]
                x_index = functions.index(target_function) + target_function_index

                target_dest.append([x[x_index], y[x_index]])

            # Redefine x_line and y_line: [origin, [dependencie_1, ...]]
            x_line[index] = [x_line[index][0], []]
            y_line[index] = [y_line[index][0], []]

            # Store all the dependencies
            for target in target_dest:
                # [origin_x, [dest_x_1, dest_x_2, ...]]
                x_line[index][1].append(target[0])
                # [origin_y, [dest_y_1, dest_y_2, ...]]
                y_line[index][1].append(target[1])

            index += 1

        # Plot the verbose text for the instructions
        for i, _txt in enumerate(txt):
            ax.annotate(_txt, (x[i] + 0.1, y[i] - 0.1), size=10.0)

        # Plot dependencies (lines)
        for _x_line, _y_line in zip(x_line, y_line):
            index = 0

            # For the current instruction, plot all dependencies (lines)
            while index < len(_x_line[1]):
                plt.annotate(s="", xy=(_x_line[0], _y_line[0]), xytext=(_x_line[1][index],
                                                                        _y_line[1][index]),
                             arrowprops=dict(arrowstyle='<-', color='darkblue', linewidth=2.0),
                             annotation_clip=self.lines_clip)
                index += 1

        # Plot the instructions (points)
        plt.plot(x, y, 'ro')
        # Show it
        plt.show()

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
                            # Avoid the throwness of exceptions
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
        #self.process_cfg.resolve_broken_succs()

        graph = self.process_cfg.basic_cfg

        if self.display_cfg:
            self.display_graph(graph, False)
        if (self.is_matplotlib_loaded and self.plot_cfg):
            self.plot_graph(graph)

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
    """Class which builds the CFG.
    """

    def __init__(self, propagate_func_call):
        """It initializes the necessary variables.

        Arguments:
            propagate_func_call (bool): if *True*, the function calls, if call to
                a function which is defined in the same file, will be linked with
                that function. Otherwise, the function call will be linked with the
                following instruction.
        """
        self.basic_cfg = cfg.CFG()
        self.funcion_calls = {}
        self.propagate_func_call = propagate_func_call

    def process(self, function_name, function):
        """It process a concrete function for the CFG.
        It completes the CFG incrementally.

        Arguments:
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
            name = node

            # Get iteratively the name
            while not isinstance(name, str):
                name = name.name

            self.funcion_calls[current_function_name].append(name)
            self.basic_cfg.append_function_call(current_function_name,
                                                name)

        # Append instruction
        self.basic_cfg.append_instruction(current_function_name, node)

    def resolve_succs_return_calls(self, from_function_name, to_function_name,
                                   first_from_function_name, instruction,
                                   recursion_functions_list, force_next_real_instr=True):
        """It resolves the *FuncCall* to functions which have
        the Return statment recursevely. Also, it resolves
        the invocations from one method to another recursively.

        Arguments:
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
            name = fc_instruction.name

            # Get iteratively the name
            while not isinstance(name, str):
                name = name.name

            if name == from_function_name:
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
                elif isinstance(instr, ast.FuncCall):
                    name = instr

                    # Get iteratively the name
                    while not isinstance(name, str):
                        name = name.name

                    if name in CFGConstants.exit_functions:
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

        Arguments:
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

    def resolve_succs_goto(self, instruction, instructions):
        """It resolves the Goto and Label statements.

        Arguments:
            instruction (pycparser_cfg.Instruction):
                Goto statement.
            instructions (list): list of instructions of
                the function which contains the Goto
                (and Label) statement(s). The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = list(map(lambda x: x.get_instruction(), instructions))
        index = real_instructions.index(real_instruction)
        label_instruction = None
        label_index = 0

        for instr in real_instructions:
            if isinstance(instr, ast.Label):
                instr_name = instr
                real_instruction_name = real_instruction

                # Get iteratively the name
                while not isinstance(instr_name, str):
                    instr_name = instr_name.name

                # Get iteratively the name
                while not isinstance(real_instruction_name, str):
                    real_instruction_name = real_instruction_name.name

                if instr_name == real_instruction_name:
                    label_instruction = instr
                    break
            label_index += 1

        if label_instruction is None:
            eprint("Warning: found 'goto' statement without 'label' statement.")
            return

        instructions[index].append_succ(instructions[label_index])

    def resolve_succs_for(self, instruction, instructions):
        """It resolves the For statement dependencies.

        Arguments:
            instruction (pycparser_cfg.Instruction):
                For statement.
            instructions (list): list of instructions of
                the function which contains the For
                statement. The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = list(map(lambda x: x.get_instruction(), instructions))
        init = real_instruction.init
        cond = real_instruction.cond
        after_for_instruction = real_instruction.next
        for_statement = real_instruction.stmt
        for_statement_instructions = pycutil.get_instruction_path(for_statement)
        for_last_instruction = None
        next_instruction = pycutil.get_real_next_instruction(real_instructions[0],
                                                             real_instruction)

        if init is not None:
            # Get the last instruction of init
            last_instr_init = pycutil.get_instruction_path(init)

            if len(last_instr_init) != 0:
                last_instr_init = last_instr_init[-1]
            else:
                last_instr_init = init
        if cond is not None:
            # Get the last instruction of cond
            last_instr_cond = pycutil.get_instruction_path(cond)

            if len(last_instr_cond) != 0:
                last_instr_cond = last_instr_cond[-1]
            else:
                last_instr_cond = cond
        if after_for_instruction is not None:
            # Get the last instruction of after_for_instruction
            last_instr_after_for_instruction = pycutil.get_instruction_path\
                                                (after_for_instruction)

            if len(last_instr_after_for_instruction) != 0:
                last_instr_after_for_instruction = last_instr_after_for_instruction[-1]
            else:
                last_instr_after_for_instruction = after_for_instruction
        if for_statement is not None:
            for_last_instruction = for_statement_instructions

            if len(for_last_instruction) != 0:
                for_last_instruction = for_last_instruction[-1]

        append_succ = lambda container, to_be_appended: \
            instructions[real_instructions.index(container)].append_succ\
                (instructions[real_instructions.index(to_be_appended)])
        remove_all_succs = lambda instr: instructions[real_instructions.index(instr)]\
                                                        .remove_all_succs()

        # Succ of For statement
        remove_all_succs(real_instruction)
        target = None

        if init is not None:
            target = init
        elif cond is not None:
            target = cond
        elif for_statement is not None:
            target = for_statement
        elif after_for_instruction is not None:
            target = after_for_instruction
        else:
            # Inifinite loop (code: "for (;;);")
            target = real_instruction

        append_succ(real_instruction, target)
        # Is the condition the one that finishes the loop
        #append_succ(real_instruction, next_instruction)

        # Succ of init
        if init is not None:
            remove_all_succs(last_instr_init)
            target = None

            if cond is not None:
                target = cond
            elif for_statement is not None:
                target = for_statement
            elif after_for_instruction is not None:
                target = after_for_instruction
            else:
                # Infinite loop (code: "for (init;;);")
                target = real_instruction

            append_succ(last_instr_init, target)

        # Succ of condition
        if cond is not None:
            remove_all_succs(last_instr_cond)
            target = None

            if for_statement is not None:
                target = for_statement
            elif after_for_instruction is not None:
                target = after_for_instruction
            else:
                # Infinite loop (code: "for (?;cond;);")
                target = real_instruction

            append_succ(last_instr_cond, target)
            append_succ(last_instr_cond, next_instruction)

        # Succ of instruction after looping
        if after_for_instruction is not None:
            remove_all_succs(last_instr_after_for_instruction)
            target = None

            if cond is not None:
                target = cond
            elif for_statement is not None:
                target = for_statement
            else:
                # Infinite loop (code: "for (?;;after_for_instruction);")
                target = real_instruction

            append_succ(last_instr_after_for_instruction, target)

        # Succ of last instruction of For statement
        if (for_statement is not None and for_last_instruction is not None):
            # for_last_instruction will be always EndOfLoop, so
            #  no importants dependencies will be removed (e.g.
            #  Return statement dependencies which may be from
            #  other functions)
            remove_all_succs(for_last_instruction)
            target = None

            if after_for_instruction is not None:
                target = after_for_instruction
            elif cond is not None:
                target = cond
            #elif for_statement is not None:
            else:
                target = for_statement
            #else:
                # It should be impossible
                # Infinite loop (code: "for (?;;)?")
                #target = real_instruction

            append_succ(for_last_instruction, target)

    def append_end_of_loop_element(self, function_name, instruction):
        """It appends a node at the end of the For, While and
        DoWhile statements to avoid problems when resolving
        dependencies.

        Arguments:
            function_name (str): name of the function that
                contains the For statement.
            instruction (pycparser.c_ast.Node): For, While
                or DoWhile statement.
        """
        instructions = self.basic_cfg.get_cfg(function_name)
        real_instructions = list(map(lambda x: x.get_instruction(), instructions))
        index = real_instructions.index(instruction)
        end_of_loop = cfg.EndOfLoop()
        for_instructions_before = pycutil.get_instruction_path(real_instructions[index])

        pycutil.append_element_to_loop_stmt(end_of_loop, instruction)

        for_instructions_after = pycutil.get_instruction_path(real_instructions[index])

        if len(for_instructions_after) - len(for_instructions_before) == 2:
            # Compound element inserted artificially in AST, so now
            #  we need to insert it in CFG
            compound = pycutil.get_instructions_of_instance(ast.Compound, for_instructions_after)[0]
            compound_index = real_instructions.index(for_instructions_after\
                                                        [for_instructions_after.index(compound) + 1])

            self.basic_cfg.append_instruction(function_name, compound,
                                              compound_index)

        self.basic_cfg.append_instruction(function_name, end_of_loop,
                                          index + len(for_instructions_after))

    def resolve_succs_while_and_do(self, instruction, instructions):
        """It resolves the While and DoWhile statements
        dependencies.

        Arguments:
            instruction (pycparser_cfg.Instruction):
                While or DoWhile statement.
            instructions (list): list of instructions of
                the function which contains the While or
                DoWhile statement. The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = list(map(lambda x: x.get_instruction(), instructions))
        index = real_instructions.index(real_instruction)
        cond = real_instruction.cond # It will not be None because of C's semantics
        cond_instructions = pycutil.get_instruction_path(cond)

        if len(cond_instructions) == 0:
            # It contains a single primitive instruction (e.g. a constant number)
            cond_instructions = [cond]

        first_cond_instruction_index = index + 1
        last_cond_instruction_index = real_instructions.index(cond_instructions[-1])
        stmt = real_instruction.stmt # It will not be None and will be Compound
        while_instructions = stmt.block_items
        first_instruction_index = real_instructions.index(stmt)
        last_instruction_index = real_instructions.index(while_instructions[-1])
        next_instruction = pycutil.get_real_next_instruction(real_instructions[0],
                                                             real_instruction)
        next_instruction_index = real_instructions.index(next_instruction)

        # Append succ of While statement
        if isinstance(real_instruction, ast.While):
            instruction.append_succ(instructions[first_cond_instruction_index])
        else:
            instruction.append_succ(instructions[first_instruction_index])

        # Append succ of last cond instruction
        instructions[last_cond_instruction_index].append_succ(instructions[next_instruction_index])

        if isinstance(real_instruction, ast.While):
            instructions[last_cond_instruction_index].append_succ(
                instructions[last_cond_instruction_index + 1])
        else:
            instructions[last_cond_instruction_index].append_succ(
                instructions[first_instruction_index])

        # Remove and append succ of last instruction
        instructions[last_instruction_index].remove_all_succs()
        instructions[last_instruction_index].append_succ(instructions\
                                                            [first_cond_instruction_index])

    def resolve_succs_func_call(self, instruction, instructions):
        """It resolves the FuncCall statements dependencies.

        Arguments:
            instruction (pycparser_cfg.Instruction): FuncCall
                statement.
            instructions (list): list of instructions of
                the function which contains the FuncCall
                statement. The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = cfg.Instruction.get_instructions(instructions)
        index = instructions.index(instruction)
        func_call_instrs = [real_instruction] + pycutil.get_instruction_path(
            real_instructions[index])
        func_call_name = instruction.get_instruction()

        # Get iteratively the name
        while not isinstance(func_call_name, str):
            func_call_name = func_call_name.name

        own_defined_functions = list(self.basic_cfg.get_function_calls().keys())
        last_instruction_index = real_instructions.index(func_call_instrs[-1])

        # Append the dependency of the FuncCall instruction, which at least
        #  will have other statement
        instruction.append_succ(instructions[index + 1])

        if (self.propagate_func_call and func_call_name in own_defined_functions):
            # Link the caller to the callee FuncDef
            callee_instructions = self.basic_cfg.get_cfg(func_call_name)

            instructions[last_instruction_index].append_succ(callee_instructions[0])

    def resolve_succs_if(self, instruction, instructions):
        """It resolves the If statements dependencies.

        Arguments:
            instruction (pycparser_cfg.Instruction): If
                statement.
            instructions (list): list of instructions of
                the function which contains the If
                statement. The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = cfg.Instruction.get_instructions(instructions)
        cond = pycutil.get_instruction_path(real_instruction.cond)          # Never None
        if_true = pycutil.get_instruction_path(real_instruction.iftrue)     # Never None
        if_false = real_instruction.iffalse                                 # It may be None

        if if_false is not None:
            if_false = pycutil.get_instruction_path(real_instruction.iffalse)
            if_false.insert(0, real_instruction.iffalse)

        cond.insert(0, real_instruction.cond)
        if_true.insert(0, real_instruction.iftrue)

        if_true_first_instr = if_true
        last_cond_instr = cond
        last_if_true_instr = if_true
        next_instruction = pycutil.get_real_next_instruction(real_instructions[0],
                                                             real_instruction)
        next_instruction_index = real_instructions.index(next_instruction)

        # Append dependency of If statement
        if isinstance(cond, list):
            instruction.append_succ(instructions[real_instructions.index(cond[0])])

            last_cond_instr = cond[-1]
        else:
            instruction.append_succ(instructions[real_instructions.index(cond)])

        # Append dependencies to the true and false branch from cond

        if isinstance(if_true, list):
            if_true_first_instr = if_true[0]
            last_if_true_instr = if_true[-1]

        if_true_first_instr_index = real_instructions.index(if_true_first_instr)
        last_cond_instr_index = real_instructions.index(last_cond_instr)

        # Append dependency from the condition to the true branch
        instructions[last_cond_instr_index].append_succ(
            instructions[if_true_first_instr_index])

        # Append dependency from the condition to the false branch
        if if_false is not None:
            # There is an else statement, so we have to append a dependency to the
            #  last instruction of the if statemenet to jump over the else statement
            last_if_true_instr_index = real_instructions.index(last_if_true_instr)

            instructions[last_if_true_instr_index].append_succ(
                instructions[next_instruction_index])

            if_false_first_instr = if_false

            # Now, append dependency from the condition to the false branch
            if isinstance(if_false, list):
                if_false_first_instr = if_false[0]

            if_false_first_instr_index = real_instructions.index(if_false_first_instr)

            instructions[last_cond_instr_index].append_succ(
                instructions[if_false_first_instr_index])
        else:
            # If there is not else statement, the condition might not even execute
            #  the if statement
            instructions[last_cond_instr_index].append_succ(
                instructions[next_instruction_index])

    def append_end_of_if_else(self, instruction, instructions):
        """It appends a node at the end of the If statements to
        avoid problems when resolving dependencies.

        Arguments:
            instruction (pycparser.c_ast.If): If statement.
            instructions (list): list of instructions of type
                *pycparser.c_ast.Node* which are the instructions
                of the function which contains *instructions*.
        """
        function_name = instructions[0].decl.name
        index = instructions.index(instruction)
        end_of_if_else_if = cfg.EndOfIfElse()   # Two objects are created in order to avoid
                                                #  references problems after
        end_of_if_else_else = cfg.EndOfIfElse() # Two objects are created in order to avoid
                                                #  references problems after
        if_else_instructions_before = pycutil.get_instruction_path(instructions[index])
        original_instruction = deepcopy(instruction)

        pycutil.append_element_to_if_else_stmt(end_of_if_else_if, end_of_if_else_else, instruction)

        if_else_instructions_after = pycutil.get_instruction_path(instructions[index])
        len_diff = len(if_else_instructions_after) - len(if_else_instructions_before)

        if len_diff in [3, 4]:
            # Compound element inserted artificially in AST, so now
            #  we need to insert it in CFG
            if len_diff == 4:
                # Compound element was inserted in if and else statements

                if_true_compound = instruction.iftrue
                if_false_compound = instruction.iffalse
                if_true_compound_target_index = instructions.index(
                    if_else_instructions_after[if_else_instructions_after.index(
                        if_true_compound) + 1])
                if_false_compound_target_index = instructions.index(
                    if_else_instructions_after[if_else_instructions_after.index(
                        if_false_compound) + 1]) + 1    # We add 1 because we are calculating
                                                        #  the indexes before append, and when
                                                        #  the values will be append, it will be
                                                        #  1 off of the target position

                self.basic_cfg.append_instruction(function_name, if_true_compound,
                                                  if_true_compound_target_index)
                self.basic_cfg.append_instruction(function_name, if_false_compound,
                                                  if_false_compound_target_index)
            else:
                # Compound element was inserter in if or else statements, which
                #  does not mean that the other has not a Compound statement
                if (isinstance(instruction.iftrue, ast.Compound) and
                        not isinstance(original_instruction.iftrue, ast.Compound)):
                    # The Compound element has been inserted in the if statement
                    if_true_compound = instruction.iftrue
                    if_true_compound_target_index = instructions.index(
                        if_else_instructions_after[if_else_instructions_after.index(
                            if_true_compound) + 1])

                    self.basic_cfg.append_instruction(function_name, if_true_compound,
                                                      if_true_compound_target_index)
                else:
                    # The Compound element has been inserted in the else statement
                    if_false_compound = instruction.iffalse
                    if_false_compound_target_index = instructions.index(
                        if_else_instructions_after[if_else_instructions_after.index(
                            if_false_compound) + 1])

                    self.basic_cfg.append_instruction(function_name, if_false_compound,
                                                      if_false_compound_target_index)

        # Append the instruction in the CFG
        end_of_if_else_if_index = if_else_instructions_after.index(end_of_if_else_if)
        end_of_if_else_else_index = if_else_instructions_after.index(end_of_if_else_else)

        self.basic_cfg.append_instruction(function_name, end_of_if_else_if,
                                          index + end_of_if_else_if_index + 1)
        self.basic_cfg.append_instruction(function_name, end_of_if_else_else,
                                          index + end_of_if_else_else_index + 1)

    def resolve_succs_break(self, instruction, instructions):
        """It resolves the Break statements dependencies.

        The important statement for the Break statement
        are For, While, DoWhile and Switch.

        Raises:
            BOAModuleException: when the Break statement is not
                inside a For, While, DoWhile or Switch statement.

        Arguments:
            instruction (pycparser_cfg.Instruction): Break
                statement.
            instructions (list): list of instructions of
                the function which contains the Break
                statement. The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = cfg.Instruction.get_instructions(instructions)
        index = real_instructions.index(real_instruction)
        parents = pycutil.get_parents(real_instructions)

        # Look for the statement which contains the Break statement
        break_target_instruction = real_instruction

        while not isinstance(break_target_instruction,
                             (ast.For, ast.While, ast.DoWhile, ast.Switch)):
            try:
                break_target_instruction = parents[break_target_instruction]
            except KeyError:
                raise BOAModuleException("the Break statement is expected to be inside a"
                                         " For, While, DoWhile or Switch statement, but"
                                         " has not been found either of those statements", self)

        next_instruction = pycutil.get_real_next_instruction(real_instructions[0],
                                                             break_target_instruction)
        next_instruction_index = real_instructions.index(next_instruction)

        # Append the dependency of the Break statement
        instruction.append_succ(instructions[next_instruction_index])

    def resolve_succs_continue(self, instruction, instructions):
        """It resolves the Continue statements dependencies.

        The important statement for the Continue statement
        are For, While and DoWhile.

        Raises:
            BOAModuleException: when the Continue statement is not
                inside a For, While or DoWhile statement.

        Arguments:
            instruction (pycparser_cfg.Instruction): Continue
                statement.
            instructions (list): list of instructions of
                the function which contains the Continue
                statement. The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = cfg.Instruction.get_instructions(instructions)
        index = real_instructions.index(real_instruction)

        # Look for the statement which contains the Break statement
        continue_target_instruction = real_instruction

        while not isinstance(continue_target_instruction,
                             (ast.For, ast.While, ast.DoWhile)):
            try:
                continue_target_instruction =\
                    pycutil.get_parents(real_instructions)[continue_target_instruction]
            except KeyError:
                raise BOAModuleException("the Continue statement is expected to be inside"
                                         " a For, While or DoWhile statement, but"
                                         " has not been found either of those statements", self)

        # The statements For, While and DoWhile has the "cond" property in Pycparser
        next_instruction = continue_target_instruction.cond

        if isinstance(continue_target_instruction, ast.For):
            # The For statement condition may be None

            if next_instruction is None:
                # Look for the next step in the For statement when there is not condition
                # We know that the Continue statement is inside the For, so we are executing
                #  an instruction
                if continue_target_instruction.next is not None:
                    next_instruction = continue_target_instruction.next
                else:
                    # There exist instructions inside the For statement (at least, the
                    #  Continue statement), and the For initialization was performed and
                    #  there is not condition nor next instruction, so we have to go to
                    #  the first instruction of the For statement. In the littlest version,
                    #  the code "for(;;) continue;" would result in a Continue node with a
                    #  dependency to itself
                    next_instruction = continue_target_instruction.stmt
        elif next_instruction is None:
            raise BOAModuleException("unexpected non condition in a While or DoWhile statement",
                                     self)

        next_instruction_index = real_instructions.index(next_instruction)

        # Append the dependency of the Break statement
        instruction.append_succ(instructions[next_instruction_index])

    def resolve_succs_switch(self, instruction, instructions):
        """It resolves the Switch statements dependencies.

        The important statement for the Switch statement
        are Case and Default.

        Arguments:
            instruction (pycparser_cfg.Instruction): Switch
                statement.
            instructions (list): list of instructions of
                the function which contains the Switch
                statement. The type is
                *pycparser_cfg.Instruction*.
        """
        real_instruction = instruction.get_instruction()
        real_instructions = cfg.Instruction.get_instructions(instructions)
        stmt = real_instruction.stmt
        cond = real_instruction.cond
        cond_instructions = [cond] + pycutil.get_instruction_path(cond)
        cond_first_instruction = cond_instructions[0]
        cond_first_instruction_index = real_instructions.index(cond_first_instruction)
        cond_last_instruction = cond_instructions[-1]
        cond_last_instruction_index = real_instructions.index(cond_last_instruction)
        next_instruction = pycutil.get_real_next_instruction(real_instructions[0],
                                                             real_instruction)
        next_instruction_index = real_instructions.index(next_instruction)
        switch_instructions = [stmt] + pycutil.get_instruction_path(stmt)
        parents = pycutil.get_parents(real_instructions)
        case_instructions = pycutil.get_instructions_of_instance(
            ast.Case, switch_instructions)  # Maybe not all the Case are valid
                                            #  (i.e. Switch inside other Switch)
        default_instructions = pycutil.get_instructions_of_instance(
            ast.Default, switch_instructions)   # Maybe not all the Default are valid
                                                #  (e.g. multiple Default)
        inner_compound = 0  # To count the inner Compound (e.g. switch (4){{{{case 4:break;}}}})

        # Append dependency for the Switch statement
        instruction.append_succ(instructions[cond_first_instruction_index])

        while isinstance(real_instructions[cond_last_instruction_index + 1], ast.Compound):
            # We append the dependency of the Compound to the condition
            instructions[cond_last_instruction_index].append_succ(
                instructions[cond_last_instruction_index + 1])

            # The Compound will be the statement who will have the dependencies
            #  to the Case and Default statements
            cond_last_instruction_index += 1
            inner_compound += 1

        real_default_stmt = None

        # Look for Case and Default statements in our Switch target
        for instructions_target in [case_instructions, default_instructions]:
            for switch_instr in instructions_target:
                own_instr = False
                parent = parents[switch_instr]

                # Look for the Switch statement we are targeting
                while not own_instr:
                    if isinstance(parent, ast.Compound):
                        parent = parents[parent]
                    elif parent == real_instruction:
                        own_instr = True
                    else:
                        # No Compound or Switch (our Switch, not other)
                        break

                # Append dependency to the Case or Default statement if is
                #  inside the Switch we are targeting
                if own_instr:
                    if isinstance(switch_instr, ast.Default):
                        # Once we find the first Default statement, we stop
                        real_default_stmt = switch_instr

                        break

                    switch_instr_index = real_instructions.index(switch_instr)
                    instructions[cond_last_instruction_index].append_succ(
                        instructions[switch_instr_index])

        if real_default_stmt is None:
            # There is not Default statement
            # Append to the condition the dependency of the next instruction
            instructions[cond_last_instruction_index - inner_compound].append_succ(
                instructions[next_instruction_index])
        else:
            # Append to the condition the dependency of the next instruction
            default_index = real_instructions.index(real_default_stmt)

            instructions[cond_last_instruction_index - inner_compound].append_succ(
                instructions[default_index])

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
            if isinstance(instruction.get_instruction(), CFGConstants.branching_instr):
                if isinstance(real_instruction, ast.Return):
                    self.resolve_succs_return(function_name, instruction,
                                              instructions, function_invoked_by)
                elif isinstance(real_instruction, ast.Goto):
                    self.resolve_succs_goto(instruction, instructions)
                elif isinstance(real_instruction, ast.For):
                    self.append_end_of_loop_element(function_name,
                                                    instruction.get_instruction())
                    self.resolve_succs_for(instruction, instructions)
                elif isinstance(real_instruction, ast.While):
                    self.append_end_of_loop_element(function_name,
                                                    instruction.get_instruction())
                    self.resolve_succs_while_and_do(instruction, instructions)
                elif isinstance(real_instruction, ast.DoWhile):
                    self.append_end_of_loop_element(function_name,
                                                    instruction.get_instruction())
                    self.resolve_succs_while_and_do(instruction, instructions)
                elif isinstance(real_instruction, ast.FuncCall):
                    self.resolve_succs_func_call(instruction, instructions)
                elif isinstance(real_instruction, ast.If):
                    self.append_end_of_if_else(instruction.get_instruction(),
                                               cfg.Instruction.get_instructions(instructions))
                    self.resolve_succs_if(instruction, instructions)
                elif isinstance(real_instruction, ast.Switch):
                    self.resolve_succs_switch(instruction, instructions)
                elif isinstance(real_instruction, ast.Continue):
                    self.resolve_succs_continue(instruction, instructions)
                elif isinstance(real_instruction, ast.Break):
                    self.resolve_succs_break(instruction, instructions)
                else:
                    raise BOAModuleException("found instruction of type"
                                             f" {get_just_type(real_instruction)}"
                                             " which is defined but not expected (update the"
                                             " module programming in order to fix it)", self)
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
