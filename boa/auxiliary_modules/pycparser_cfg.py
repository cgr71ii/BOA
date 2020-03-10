"""File which contains the CFG (i.e. Control Flow Graph)
data structure.
"""

# Pycparser libs
import pycparser.c_ast as ast

# Own libs
from util import is_key_in_dict

class FinalNode(ast.Node):
    """Empty pycparser class which is a reference
    to set a final node and to know that if we reach
    this node, the execution would finish (e.g. end
    of main function, exit(), ...)
    """

class Instruction():

    def __init__(self, instruction):
        """It initializes a concrete instruction.

        Arguments:
            instruction (pycparser.c_ast.Node): instruction.
        """
        self.instruction = instruction
        self.type = type(instruction)
        self.succs = []

    def append_succ(self, succ_instr):
        """It appends a successive instruction for
        the current instruction.

        If a successive instruction is already in, it
        will be ignored.

        Arguments:
            succ_instr (Instruction): successive instruction
                which could be executed after the current
                instruction.
        """
        if not succ_instr in self.succs:
            self.succs.append(succ_instr)

    def get_instruction(self):
        """It returns the pycparser instruction.

        Returns:
            pycparser.c_ast.Node: instruction
        """
        return self.instruction

    def get_type(self):
        """It returns the type of the instruction.

        Returns:
            type: type of the instruction
        """
        return self.type

    def get_succs(self):
        """It returns the successive instructions
        which are going to be executed after itself.

        Returns:
            list: successive instructions
        """
        return self.succs

class CFG():

    def __init__(self):
        self.function_calls = {}
        self.function_invoked_by = {}
        self.instructions = {}

    def append_instruction(self, function, instruction):
        """It appends an instruction from a function.

        Arguments:
            function (str): function from where the instruction
                is going to be executed.
            instruction (pycparser.c_ast.Node): instruction.
        """
        instr = Instruction(instruction)

        if not is_key_in_dict(self.instructions, function):
            self.instructions[function] = [instr]
        else:
            self.instructions[function].append(instr)

    def append_function_call(self, origin, destiny):
        """It appends a function call from other function
        (or itself if recursive). Moreover, it appends
        the functions which are being invoked from.

        Arguments:
            origin (str): function call from where the function
                call is being invoked.
            destiny (str): function call which is being invoked.
        """
        if not is_key_in_dict(self.function_calls, origin):
            if destiny is None:
                self.function_calls[origin] = []
            else:
                self.function_calls[origin] = [destiny]
        else:
            self.function_calls[origin].append(destiny)

        if destiny is None:
            if is_key_in_dict(self.function_invoked_by, origin):
                return

            self.function_invoked_by[origin] = []
            return

        if not is_key_in_dict(self.function_invoked_by, destiny):
            self.function_invoked_by[destiny] = [origin]
        else:
            self.function_invoked_by[destiny].append(origin)

    def get_cfg(self, function_name):
        """It returns the CFG starting in a concrete function.
        If *function* is *None*, the whole CFG will be returned.

        Arguments:
            function_name (str): function.

        Returns:
            list: CFG of a function. If *function_name* is *None*,
            the whole CFG will be returned. If *function_name* is
            not defined, *None* will be returned. The type of the
            elements is *Instruction*
        """
        if function_name is None:
            return self.instructions
        if not is_key_in_dict(self.instructions, function_name):
            return None

        return self.instructions[function_name]

    def get_function_calls(self):
        """It returns the function calls.

        Returns:
            dict: function calls
        """
        return self.function_calls

    def get_function_invoked_by(self):
        """It returns the information about which functions invoked
        a concrete function.

        Returns:
            dict: functions which invokes a concrete function
        """
        return self.function_invoked_by
