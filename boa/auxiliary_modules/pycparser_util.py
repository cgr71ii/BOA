"""File which contains utilities to work with
Pycparser.
"""

# Pycparser imports
import pycparser.c_ast as ast

# Own imports
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
from util import get_just_type

VISITOR_NC = PreorderVisitor()

class PycparserException(Exception):
    """PycparserException exception.

    This exception is raised in methods which are intended
    to be using the Pycparser parser. It is a general exception
    used to explain a error when handling pycparser jobs.
    """

    def __init__(self, message):
        """It redefined self.message with the goal of be more
        verbose.

        Arguments:
            message (str): custom message to be displayed when
                the exception is raised.
        """
        super(PycparserException, self).__init__(f"pycparser: {message}")

def get_instruction_path(instruction):
    """It returns the path of a instruction.

    This function is intented to give a basic instructions
    and get all its instructions, but if you use as instruction
    a function definition, you will get all the instructions
    of the function.

    Arguments:
        instrution (pycparser.c_ast.Node): instruction.

    Raises:
        PycparserException: when *instruction* is not the expected
            type.

    Returns:
        list: list of instructions starting in *instruction*
    """
    if not isinstance(instruction, ast.Node):
        raise PycparserException("'instruction' was expected to be"
                                 " 'pycparser.c_ast.Node', but is"
                                 f" {get_just_type(instruction)}")

    return VISITOR_NC.visit_and_return_path(instruction)

def get_instructions_of_instance(instance, instructions):
    """It returns all the instructions of a concrete instance.

    Arguments:
        instance (type): wanted instance of
            *pycparser.c_ast.Node*.
        instructions (list): list of instructions of type
            *pycparser.c_ast.Node*.

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.

    Returns:
        list: list of instructions which are instances of
        *pycparser.c_ast.Node* and *instance*.
    """
    result = []

    if not isinstance(instance, type):
        raise PycparserException("'instance' was expected to be 'type',"
                                 f" but is '{get_just_type(instance)}'")
    if not isinstance(instructions, list):
        raise PycparserException("'instructions' was expected to be 'list',"
                                 f" but is '{get_just_type(instructions)}'")

    for instruction in instructions:
        if not isinstance(instruction, ast.Node):
            raise PycparserException("'instructions' elements were expected"
                                     " to be 'pycparser.c_ast.Node', but are"
                                     " (some or all) "
                                     f"'{get_just_type(instruction)}'")

        if isinstance(instruction, instance):
            result.append(instruction)

    return result

def get_real_next_instruction(root, instruction):
    """It returns the real next instruction, not just the
    next Pycparser instruction which could be an inner definition
    of an instruction.

    Parameters:
        root (pycparser.c_ast.Node): starting point to look for
            *instruction* and try to get the next. Usually will
            be a function.
        instruction (pycparser.c_ast.Node): instruction or
            inner instruction from which we want the next instruction.

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.

    Returns:
        pycparser.c_ast.Node: next real instruction or *None* if
        was the last instruction or could not find *instruction*
        in *root*
    """
    if (not isinstance(root, ast.Node) or
            not isinstance(instruction, ast.Node)):
        raise PycparserException("'root' and 'instruction' have to be "
                                 f"'pycparser.c_ast.Node', but they are"
                                 f" '{get_just_type(root)}' and"
                                 f" '{get_just_type(instruction)}' respectively")

    result = None
    instructions = get_instruction_path(root)
    index = 0

    while index < len(instructions):
        if instruction == instructions[index]:
            next_instrs = get_instruction_path(instructions[index])

            if index + len(next_instrs) + 1 < len(instructions):
                result = instructions[index + len(next_instrs) + 1]

            return result

        index += 1

    return result

def get_instructions_type(instructions, second_function_to_apply=None):
    """It maps the instructions to their types.

    Parameters:
        instructions (list): list of instructions.
        second_function_to_apply (lambda): optional second
            function to apply. Default value is *None*.

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.
        Exception: if *second_function_to_apply* is not
            wisely applied.

    Returns:
        list: list with the type of the instructions
    """
    if (not isinstance(instructions, list) or
            not isinstance(second_function_to_apply, [type(None),
                                                      type(lambda x: x)])):
        raise PycparserException("'instructions' and 'second_function_to_apply'"
                                 " were expected to be 'list' and 'function' but"
                                 f" they are '{get_just_type(instructions)}' and"
                                 f" '{get_just_type(second_function_to_apply)}'"
                                 " respectively")

    result = list(map(lambda instr: type(instr), instructions))

    if second_function_to_apply is not None:
        result = list(map(second_function_to_apply, result))

    return result

def append_element_to_function(element, compound=None, func_def=None):
    """It attempts to append an element to a function.

    Arguments:
        element (pycparser.c_ast.Node): element to be appended.
        compound (pycparser.c_ast.Compound): 'compound' element of
            the function. If is *None*, *func_def* can not be *None*.
        func_def (pycparser.c_ast.FuncDef): 'func_def' element of
            the function. If is *None*, *compound* can not be *None*.

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.

    Returns:
        bool: *True* if *element* could be appended. *False* otherwise
    """
    if (compound is None and
            func_def is None):
        return False
    if not isinstance(element, ast.Node):
        raise PycparserException("'element' was expected to be"
                                 " 'pycparser.c_ast.Node' but"
                                 f" is '{get_just_type(element)}'")

    if compound is None:
        compound =\
        get_instructions_of_instance(ast.Compound,
                                     get_instruction_path(func_def))

        if len(compound) == 0:
            return False

        compound = compound[0]

    if compound.block_items is None:
        compound.block_items = [element]
    else:
        compound.block_items.append(element)

    return True

def append_element_to_loop_stmt(element, loop_element):
    """It attempts to append an element to a For, While or
    DoWhile statement.

    Arguments:
        element (pycparser.c_ast.Node): element to be appended.
        loop_element (pycparser.c_ast.Node): 'for', 'while'
            of 'do_while' element.
    """
    if not isinstance(element, ast.Node):
        raise PycparserException("'element' was expected to be"
                                 " 'pycparser.c_ast.Node' but"
                                 f" is '{get_just_type(element)}'")
    if not isinstance(loop_element, (ast.For, ast.While, ast.DoWhile)):
        raise PycparserException("'loop_element' was expected to"
                                 " be 'pycparser.c_ast.For', "
                                 "'pycparser.c_ast.While' or "
                                 "'pycparser.c_ast.DoWhile' but"
                                 f" is '{get_just_type(loop_element)}'")

    if loop_element.stmt is None:
        loop_element.stmt = [element]
    else:
        if isinstance(loop_element.stmt, ast.Compound):
            # Append element to Compound like if was a function
            append_element_to_function(element, loop_element.stmt)
        else:
            # There is just an element (i.e. for (?;?;?)single_statement;), so
            #  we create a Compound element and append the existant elements and
            #  the new one
            compound = ast.Compound([loop_element.stmt, element], loop_element.stmt.coord)
            loop_element.stmt = compound
