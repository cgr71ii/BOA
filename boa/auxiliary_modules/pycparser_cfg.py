"""File which contains the CFG (i.e. Control Flow Graph)
data structure.
"""

# Pycparser libs
import pycparser.c_ast as ast

# Own libs
from util import is_key_in_dict, get_just_type
import auxiliary_modules.pycparser_util as pycutil

class FinalNode(ast.EmptyStatement):
    """Empty pycparser statement which is a reference
    to set a final node and to know that if we reach
    this node, the execution would finish (e.g. end
    of main function, exit(), ...)
    """

class NotInvoked(ast.EmptyStatement):
    """Empty pycparser statement which is a reference
    to use when a function is not invoked by any
    other function. This is useful to avoid other
    reference problems (e.g. expecting a reference
    when doing tail recursion optimization)
    """

class CFGException(pycutil.PycparserException):
    """CFGException exception.

    This exception should be raised when something wrong
    happens while processing or using CFG. This exception
    is intended to be used when using a CFG implemented
    for Pycparser parser because of the structure of the
    message (inheritance from PycparserException).
    """

    def __init__(self, message):
        """It redefined self.message with the goal of be more
        verbose.

        Arguments:
            message (str): custom message to be displayed when
                the exception is raised.
        """
        super(CFGException, self).__init__(f"CFG: {message}")

class Instruction():

    def __init__(self, instruction):
        """It initializes a concrete instruction.

        Arguments:
            instruction (pycparser.c_ast.Node): instruction.

        Raises:
            CFGException: if the type of the arguments
                are not the expected.
        """
        if not isinstance(instruction, ast.Node):
            raise CFGException("'instruction' was expected to be"
                               " 'pycparser.c_ast.Node', but is"
                               f" '{get_just_type(instruction)}'")

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

        Raises:
            CFGException: if the type of the arguments
                are not the expected.
        """
        if not isinstance(succ_instr, Instruction):
            raise CFGException("'succ_instr' was expected to be"
                               " 'Instruction', but is "
                               f"{get_just_type(succ_instr)}")

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

    def append_instruction(self, function_name, instruction):
        """It appends an instruction from a function.

        Arguments:
            function_name (str): function from where the
                instruction is going to be executed.
            instruction (pycparser.c_ast.Node): instruction.

        Raises:
            CFGException: if the type of the arguments
                are not the expected.
        """
        instr = Instruction(instruction)

        if not isinstance(function_name, str):
            raise CFGException("'function_name' was expected to be 'str'"
                               f", but is {get_just_type(function_name)}")

        if not is_key_in_dict(self.instructions, function_name):
            self.instructions[function_name] = [instr]
        else:
            self.instructions[function_name].append(instr)

    def append_function_call(self, origin, destiny):
        """It appends a function call from other function
        (or itself if recursive). Moreover, it appends
        the functions which are being invoked from.

        Arguments:
            origin (str): function call from where the function
                call is being invoked.
            destiny (str): function call which is being invoked.

        Raises:
            CFGException: if the type of the arguments
                are not the expected.
        """
        if (not isinstance(origin, str) or
                (destiny is not None and
                 not isinstance(destiny, str))):
            raise CFGException("'origin' and 'destiny' were expected to be 'str'"
                               f" and 'str', but are '{get_just_type(origin)}'"
                               f" and '{get_just_type(destiny)}' respectively")

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

        Raises:
            CFGException: if the type of the arguments
                are not the expected.
        """
        if function_name is None:
            return self.instructions

        if not isinstance(function_name, str):
            raise CFGException("'function_name' was expected to be 'str'"
                               f", but is '{get_just_type(function_name)}'")

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
