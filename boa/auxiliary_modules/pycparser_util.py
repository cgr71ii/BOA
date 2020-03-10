"""File which contains utilities to work with
Pycparser.
"""

# Own imports
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor

VISITOR_NC = PreorderVisitor()

def get_instruction_path(instruction):
    """It returns the path of a instruction.

    This function is intented to give a basic instructions
    and get all its instructions, but if you use as instruction
    a function definition, you will get all the instructions
    of the function.

    Arguments:
        instrution (pycparser.c_ast.Node): instruction.

    Returns:
        list: list of instructions starting in *instruction*
    """
    return VISITOR_NC.visit_and_return_path(instruction)

def get_instructions_of_instance(instance, instructions):
    """It returns all the instructions of a concrete instance.

    Arguments:
        instance (type): wanted instance of
            *pycparser.c_ast.Node*.
        instructions (list): list of instructions of type
            *pycparser.c_ast.Node*.

    Returns:
        list: list of instructions which are instances of
        *pycparser.c_ast.Node* and *instance*.
    """
    result = []

    for instruction in instructions:
        if isinstance(instruction, instance):
            result.append(instruction)

    return result

def get_real_next_instruction(root, instruction, debug=False):
    """It returns the real next instruction, not just the
    next Pycparser instruction which could be an inner definition
    of an instruction.

    Parameters:
        root (pycparser.c_ast.Node): starting point to look for
            *instruction* and try to get the next. Usually will
            be a function.
        instruction (pycparser.c_ast.Node): instruction or
            inner instruction from which we want the next instruction.
        debug (bool): it displays debug messages if *True*.

    Returns:
        pycparser.c_ast.Node: next real instruction or *None* if
        was the last instruction or could not find *instruction*
        in *root*
    """
    result = None
    instructions = get_instruction_path(root)
    index = 0

    if debug:
        print(f"get_real_next_instruction: instruction: {type(instruction)}")
        print("get_real_next_instruction: root:"
              f" {list(map(lambda x: type(x), root))}")

    while index < len(instructions):
        if instruction == instructions[index]:
            next_instrs = get_instruction_path(instructions[index])

            if debug:
                print("get_real_next_instruction: next_instrs: "
                      f"{list(map(lambda x: type(x), next_instrs))}")
                print("get_real_next_instruction: index: "
                      f"{index} of {len(instructions)}")

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

    Returns:
        list: list with the type of the instructions
    """
    result = list(map(lambda instr: type(instr), instructions))

    if second_function_to_apply is not None:
        result = list(map(second_function_to_apply, result))

    return result
