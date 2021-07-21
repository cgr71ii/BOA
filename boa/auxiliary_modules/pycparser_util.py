"""File which contains utilities to work with
Pycparser.
"""

# Std libs
import logging

# Pycparser imports
import pycparser.c_ast as ast

# Own imports
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
from util import get_just_type, is_key_in_dict

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

class Separator(ast.EmptyStatement):
    """This element is intented to separate statements when
    creating whole instructions in a list. For example, it
    might be used to separate the differents statements used
    in a For statement.

    Warning: this instruction is fake, so you will not be able
    to find it in the original instructions.
    """

class PycparserUtilConstants:
    """Useful constants to use by the methods in this file.
    """
    visitor_nc = PreorderVisitor()
    strict_compound_instr = (ast.Compound, ast.DoWhile, ast.For,
                             ast.If, ast.Switch, ast.While)
    compound_instr = strict_compound_instr + (ast.Case, ast.Default)
    fake_instr = (Separator,)

def get_instruction_path(instruction, include_instruction=False):
    """It returns the path of a instruction.

    This function is intented to give a basic instructions
    and get all its instructions, but if you use as instruction
    a function definition, you will get all the instructions
    of the function.

    Arguments:
        instrution (pycparser.c_ast.Node): instruction.
        include_instruction (bool): if *True*, *instruction* will be
            the first instruction in the result.

    Raises:
        PycparserException: when *instruction* is not the expected
            type.

    Returns:
        list: list of instructions starting in *instruction* if, at
        least, contains other instruction besides of *instruction*.
        If there is not instructions besides of *instructions*, an
        empty list will be returned
    """
    if not isinstance(instruction, ast.Node):
        raise PycparserException("'instruction' was expected to be"
                                 " 'pycparser.c_ast.Node', but is"
                                 f" {get_just_type(instruction)}")

    result = PycparserUtilConstants.visitor_nc.visit_and_return_path(instruction)

    if include_instruction:
        result = [instruction] + result

    return result

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
        *pycparser.c_ast.Node* and *instance*. If no instruction
        is instance of *instance*, an empty list will be
        returned
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

    Arguments:
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

    Arguments:
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

    result = list(map(type, instructions))

    if second_function_to_apply is not None:
        result = list(map(second_function_to_apply, result))

    return result

def append_element_to_function(element, compound=None, func_def=None,
                               after_element=None):
    """It attempts to append an element to a function.

    Arguments:
        element (pycparser.c_ast.Node): element to be appended.
        compound (pycparser.c_ast.Compound): 'compound' element of
            the function. If is *None*, *func_def* can not be *None*.
        func_def (pycparser.c_ast.FuncDef): 'func_def' element of
            the function. If is *None*, *compound* can not be *None*.
        after_element (pycparser.c_ast.Node): element which will be
            before of *element*. The default value is *None*. If is
            different of *None* and the element is not found, the
            position will be the last.

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
        found = False

        if after_element is not None:

            if after_element in compound.block_items:
                index = compound.block_items.index(after_element)

                compound.block_items.insert(index + 1, element)
                found = True
            else:
                instructions = get_instruction_path(compound)
                compound_elements = get_instructions_of_instance(ast.Compound,
                                                                 instructions)

                for comp in compound_elements:
                    if after_element in comp.block_items:
                        index = comp.block_items.index(after_element)

                        comp.block_items.insert(index + 1, element)
                        found = True
                        break

                if not found:
                    index = instructions.index(after_element)

                    instructions.insert(index + 1, element)
                    found = True

        if not found:
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

def append_element_to_if_else_stmt(element_if, element_else, if_element):
    """It attempts to append an element to a If statement.

    Arguments:
        element_if (pycparser.c_ast.Node): element to be appended.
            in the else statement. If *None*, no element will be
            appended.
        element_else (pycparser.c_ast.Node): element to be appended
            in the else statement. If *None*, no element will be
            appended.
        if_element (pycparser.c_ast.If): If node.
    """
    if (not isinstance(element_if, (ast.Node, type(None))) or
            not isinstance(element_else, (ast.Node, type(None)))):
        raise PycparserException("'element_if' and 'element_else'"
                                 " were expected to be"
                                 " 'pycparser.c_ast.Node' but"
                                 f" are '{get_just_type(element_if)}'"
                                 f" and '{get_just_type(element_else)}'"
                                 " respectively")
    if not isinstance(if_element, ast.If):
        raise PycparserException("'if_element' was expected to"
                                 " be 'pycparser.c_ast.If' but"
                                 f" is '{get_just_type(if_element)}'")

    cond = if_element.cond
    if_true = if_element.iftrue
    if_false = if_element.iffalse
    if_true_compound = if_true
    if_false_compound = if_false

    # Handle if statement
    if element_if is not None:
        if not isinstance(if_true, ast.Compound):
            # Create a virtual compound and insert the elements
            compound = ast.Compound([if_true, element_if], if_true.coord)  # if_true cannot be None
            if_element.iftrue = compound
        else:
            # Append the element to the existing Compound

            block = if_true.block_items

            if isinstance(block, list):
                # Append the element to the bunch of existing elements
                block.append(element_if)
            else:
                # The Compound contains only one or none elements.
                if if_true.block_items is None:
                    if_true.block_items = [element_if]
                else:
                    if_true.block_items = [block, element_if]

    # Handle else statement
    if element_else is not None:
        if if_false is None:
            # Just set the element
            if_element.iffalse = element_else
        else:
            if not isinstance(if_false, ast.Compound):
                # Create a virtual compound and insert the elements
                compound = ast.Compound([if_false, element_else], if_false.coord)  # if_false is not None
                if_element.iffalse = compound
            else:
                # Append the element to the existing Compound

                block = if_false.block_items

                if isinstance(block, list):
                    # Append the element to the bunch of existing elements
                    block.append(element_else)
                else:
                    # The Compound contains only one or none elements.
                    if if_false.block_items is None:
                        if_false.block_items = [element_else]
                    else:
                        if_false.block_items = [block, element_else]

def is_primitive_instruction(instruction):
    """It checks if *instruction* is primitive, which means
    that is a leaf of the AST.

    Arguments:
        instruction (pycparser.c_ast.Node): instruction to check
            if it is a leaf of the AST.

    Raises:
        PycparserException: if the type of the arguments are not
            the expected.

    Returns:
        bool: *True* if *instruction* is a leaf of the AST. *False*
        otherwise
    """
    if not isinstance(instruction, ast.Node):
        raise PycparserException("'instruction' was expected to be"
                                 " 'pycparser.c_ast.Node' but is"
                                 f" '{get_just_type(instruction)}'")

    return len(get_instruction_path(instruction)) == 0

def get_parents(instructions):
    """It gets the parents of *instructions*.

    Arguments:
        instructions (list): list of instructions of type
            *pycparser.c_ast.Node*.

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.

    Returns:
        dict: contains each instruction and its found parent
        (if could be found)
    """
    result = {}

    for instr in instructions:
        if not isinstance(instr, ast.Node):
            raise PycparserException("'instructions' elements were expected"
                                     " to be 'pycparser.c_ast.Node', but are"
                                     " (some or all) "
                                     f"'{get_just_type(instr)}'")

        direct_children = PycparserUtilConstants.visitor_nc.visit_and_return_first_path(instr)

        for child in direct_children:
            if not is_key_in_dict(result, child):
                result[child] = instr

    return result

def get_direct_children(instruction):
    """It gets the direct children of *instruction*.

    Arguments:
        instruction (pycparser.c_ast.Node): instruction of type
            *pycparser.c_ast.Node*.

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.

    Returns:
        list: contains the direct children of *instruction*.
        If none child was found, an empty list will be returned
    """
    if not isinstance(instruction, ast.Node):
        raise PycparserException("'instruction' was expected to be"
                                 " 'pycparser.c_ast.Node', but is"
                                 f" '{get_just_type(instruction)}'")

    return PycparserUtilConstants.visitor_nc.visit_and_return_first_path(instruction)

def get_deepness_level(initial_instr, parents, rec_instr, top_reference):
    """It returns the deepness level.

    Arguments:
        initial_instr (pycparser.c_ast.Node): instruction which we are
            looking for its deepness level with *top_reference* as reference.
        parents (dict): necessary parents of a list of instruction which are
            needed for calculate the depness level (you can use
            *get_parents(initial_instr)* for providing the parents).
        rec_instr (pycparser.c_ast.Node): recursive instruction, which
            initialy should be equal to *initial_instr*.
        top_reference (pycparser.c_ast.Node): reference which will be looking
            for in order to know when to stop the looking. Usually it is a node
            of type *pycparser.c_ast.FuncDef* or *pycparser.c_ast.Compound*.

    Returns:
        int: deepness level
    """
    if rec_instr == top_reference:
        return 0

    return 1 + get_deepness_level(initial_instr, parents, parents[rec_instr], top_reference)

def get_function_decl_parameters(func_def):
    """It returns the Decl statements of the parameters of a function.

    Parameters:
        func_def (pycparser.c_ast.FuncDef): definition of the function.

    Returns:
        list: list of Decl statements of the function parameters. If there
        are not parameters, an empty list will be returned.

    Raises:
        PycparserException: if the type of the arguments are not the
            expected.
    """
    if not isinstance(func_def, ast.FuncDef):
        raise PycparserException("'func_def' was expected to be"
                                 " 'pycparser.c_ast.FuncDef' but is"
                                 f" '{get_just_type(func_def)}'")

    func_param_list = func_def.decl.type.args

    # Check if there are parameters
    if func_param_list is None:
        # There are not parameters
        return []

    # Thare are function parameters
    param_list_instructions = get_instruction_path(func_param_list)
    function_parameters =\
        get_instructions_of_instance(ast.Decl, param_list_instructions)

    return function_parameters

def is_variable_decl(instruction):
    """It checks if an instruction is a declaration of a variable.
    It checks the normal declarations, enums and structs. Only
    checks for the declaration, not assignments.

    Arguments:
        instruction (pycparser.c_ast.Node): instruction to check if
            is a variable declaration.

    Returns:
        bool: *True* if *instruction* is a variable declaration. Otherwise,
        *False*

    Raises:
        PycparserException: if the type of the arguments are not the
            expected.
    """
    if not isinstance(instruction, ast.Node):
        raise PycparserException("'instruction' was expected to be"
                                 " 'pycparser.c_ast.Node' but is"
                                 f" '{get_just_type(instruction)}'")

    # The first instruction of a declaration is of type Decl
    if not isinstance(instruction, ast.Decl):
        return False

    instructions = [instruction] + get_instruction_path(instruction)

    # Used in variables declarations (checked empirically)
    function_type_decl = get_instructions_of_instance(
        ast.TypeDecl,
        instructions)

    # Check if is a normal declaration
    function_id_type = get_instructions_of_instance(
        ast.IdentifierType,
        instructions)
    # Check if is a Struct declaration
    function_struct_type = get_instructions_of_instance(
        ast.Struct,
        instructions)
    # Check if is an Enum declaration
    function_enum_type = get_instructions_of_instance(
        ast.Enum,
        instructions)
    # Check if is an Union declaration
    function_union_type = get_instructions_of_instance(
        ast.Union,
        instructions)

    if (len(function_type_decl) >= 1 and
           isinstance(function_type_decl[0].declname, str) and
           (len(function_id_type) +\
            len(function_struct_type) +\
            len(function_enum_type) +\
            len(function_union_type) >= 1)):
        return True

    return False

def get_function_decl_variables(func_def):
    """It returns the Decl statements of the variables of a function.

    Parameters:
        func_def (pycparser.c_ast.FuncDef): definition of the function.

    Returns:
        list: list of Decl statements of the function variables. If there
        are not variables, an empty list will be returned.

    Raises:
        PycparserException: if the type of the arguments are not the
            expected.
    """
    if not isinstance(func_def, ast.FuncDef):
        raise PycparserException("'func_def' was expected to be"
                                 " 'pycparser.c_ast.FuncDef' but is"
                                 f" '{get_just_type(func_def)}'")
    result = []
    func_body = func_def.body
    func_body_instructions = get_instruction_path(func_body)

    function_variables =\
            get_instructions_of_instance(ast.Decl, func_body_instructions)

    for function_variable in function_variables:
        if is_variable_decl(function_variable):
            result.append(function_variable)

    return result

def get_full_instruction(instruction, instructions, display_coord=False):
    """It returns all the instructions which are part of
    a concrete statement. In case of elements which may
    have a Compound element, literal or semanticaly, will
    only return the necessary part of the element according
    to its semantics.

    It might be returned elements with empty lists because
    there are elements that, in order to avoid semantics leakage,
    it will be explicitly set. An example of it is the For
    statemenet, which might has empty statements, but they will
    be defined: for(;;); -> [[For], [] (init), [] (cond),
    [] (next), [Compound], [EmptyStatement], [EndOfLoop]]. If you
    wonder why there is a Compound element, check the CFG
    implementation. Short answer: CFG uses auxiliary nodes in order
    to know semantic information which helps to build the CFG.
    The long answer has relation with recursion, dependencies, etz.

    Arguments:
        instruction (pycparser.c_ast.Node): first instruction
            from where it will start the searching. It will be
            the root of the result.
        instructions (list): list of instructions of the whole
            function. The type of the elemens have to be
            *pycparser.c_ast.Node*.
        display_coord (bool): If *True*, the *coord* attribute
            of the whole found instructions will be displayed
            in order to debug. The default value is *False*.

    Returns:
        list: elements of type list of type *pycparser.c_ast.Node* wich are
        part of the statement considered as a whole. The instructions
        considered as a whole will be that list inside the main list

    Raises:
        PycparserException: if the first instruction of *instructions*
            is not an instance of *pycparser.c_ast.FuncDef*.
    """
    index = instructions.index(instruction)
    next_instruction = get_real_next_instruction(instructions[0], instruction)

    if next_instruction is None:
        return [[instruction]]

    next_instruction_index = instructions.index(next_instruction)
    result = []

    # ast.Compound, ast.DoWhile, ast.For,
    # ast.If, ast.Switch, ast.While

    if isinstance(instruction, PycparserUtilConstants.compound_instr):
        if isinstance(instruction, ast.Compound):
            result = [[instruction]]  # Compound as an instruction itself
        elif isinstance(instruction, ast.Default):
            result = [[instruction]]  # Default as an instruction itself
        elif isinstance(instruction, ast.Case):
            expr = instruction.expr
            expr_instrs = []

            if expr is not None:
                expr_instrs = get_instruction_path(expr)

            if expr is None:
                expr = []
            elif not isinstance(expr, list):
                expr = [expr]

            expr = expr + expr_instrs

            # The statement is an instruction itself and the expr another
            #result = [[instruction], expr]
            result = [[instruction] + expr]
        elif isinstance(instruction, (ast.While, ast.DoWhile, ast.If, ast.Switch)):
            cond = instruction.cond
            cond_instrs = []

            if cond is not None:
                cond_instrs = get_instruction_path(cond)

            if cond is None:
                cond = []
            elif not isinstance(cond, list):
                cond = [cond]

            cond = cond + cond_instrs

            # The statement is an instruction itself and the condition another
            #result = [[instruction], cond]
            result = [[instruction] + cond]
        elif isinstance(instruction, ast.For):
            init = instruction.init
            init_instrs = []
            cond = instruction.cond
            cond_instrs = []
            for_next = instruction.next
            for_next_instrs = []

            if init is not None:
                init_instrs = get_instruction_path(init)
            if cond is not None:
                cond_instrs = get_instruction_path(cond)
            if for_next is not None:
                for_next_instrs = get_instruction_path(for_next)

            if init is None:
                init = []
            elif not isinstance(init, list):
                init = [init]
            if cond is None:
                cond = []
            elif not isinstance(cond, list):
                cond = [cond]
            if for_next is None:
                for_next = []
            elif not isinstance(for_next, list):
                for_next = [for_next]

            init = init + init_instrs
            cond = cond + cond_instrs
            for_next = for_next + for_next_instrs

            first_separator = Separator()
            second_separator = Separator()

            # Every part is an instruction itself
            #result = [[instruction], cond, init, for_next]
            result = [[instruction] + init + [first_separator] + cond +\
                      [second_separator] + for_next]
        else:
            raise PycparserException("found instruction of type"
                                     f" '{get_just_type(instruction)}'"
                                     " which is defined but not expected (update the"
                                     " function in order to fix it)")
    else:
        while index < next_instruction_index:
            # Append all the instructions which are considered to be part of the same statement
            result.append(instructions[index])
            index += 1

        result = [result]

    if display_coord:
        if (len(result) == 0 or len(result[0]) == 0):
            logging.debug("'Whole' instruction: there is NO instruction")
        else:
            coord = result[0][0].coord
            instr_type = get_just_type(result[0][0])
            name = None

            if is_variable_decl(result[0][0]):
                name = result[0][0].name

            instr_type = instr_type.split(".")[2]

            if coord is None:
                coord = "-1:-1"
            else:
                coord = str(coord)
                coord = coord.split(":")
                coord = f"{coord[1]}:{coord[2]}"

            if name:
                logging.debug("'Whole' instruction: %s - %s - %s", coord, instr_type, name)
            else:
                logging.debug("'Whole' instruction: %s - %s", coord, instr_type)

    return result

def get_full_instruction_function(instructions, display_coord=False):
    """It returns the whole statements of a function. This function
    is a wrapper of *get_full_instruction* which applies it but for
    a whole function.

    Arguments:
        instructions (list): list of instructions of the whole
            function. The type of the elemens have to be
            *pycparser.c_ast.Node*.
        display_coord (bool): If *True*, the *coord* attribute
            of the whole found instructions will be displayed
            in order to debug. The default value is *False*.

    Returns:
        list: list of list of *pycparser.c_ast.Node*. It will contain
        all the instructions considered as atomic. Check
        *get_full_instruction* in order to have a more detailed
        explanation

    Raises:
        PycparserException: if the first instruction of *instructions*
            is not an instance of *pycparser.c_ast.FuncDef*.
    """
    if not isinstance(instructions[0], ast.FuncDef):
        raise PycparserException("first instruction was expected to be"
                                 " 'pycparser.c_ast.FuncDef' but is"
                                 f" '{get_just_type(instructions[0])}'")

    instruction = instructions[0].body
    all_instructions = get_instruction_path(instruction)
    instruction = all_instructions[0]   # Avoid the Compound element
    result = []

    # Get all the full instructions
    while instruction is not None:
        full_instructions = get_full_instruction(instruction, instructions, display_coord)

        # It might not be next instruction
        if len(full_instructions) == 0:
            instruction = None
        else:
            index = instructions.index(instruction)

            for full_instruction in full_instructions:
                result.append(full_instruction)
                index += len(full_instruction)

                # Subtract those fake instructions used for whatever reason
                for fake in PycparserUtilConstants.fake_instr:
                    fake_instrs = get_instructions_of_instance(fake, full_instruction)
                    index -= len(fake_instrs)

            # Is there next instruction?
            if index < len(instructions):
                # Yes
                instruction = instructions[index]
            else:
                # No
                instruction = None

    return result

def get_name(instruction):
    """It returns the full name of a element.

    The name could be a usual name (e.g. foo, bar) or could be a
    function callback stored in a structure (e.g. a.b.foo).

    Arguments:
        instruction (pycparser.c_ast.Node): element which is
            going to be analyzed for retrieve the name.

    Returns:
        str: name of the element

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.
        KeyError: if "name" is not found in *instruction*.
    """
    if not isinstance(instruction, ast.Node):
        raise PycparserException("'instruction' was expected to be"
                                 " 'pycparser.c_ast.Node' but is"
                                 f" '{get_just_type(instruction)}'")

    name = instruction.name
    instructions = None

    if not isinstance(name, str):
        instructions = [name] + get_instruction_path(name)

        name = ""

        for instr in instructions:
            if isinstance(instr, ast.ID):
                name += f".{instr.name}"

        if name[0] == ".":
            name = name[1:]

    return name

def get_func_call_parameters_name(instruction, recursive_struct=True):
    """It returns the name of the found elements in the parameters
    of a FuncCall element.

    If other function call are found, it will be resolved recursively
    and instead of returning the name of the function call, other result
    will be returned in form of list where the first result will be the
    name of the function call and the second a list, result of call this
    function recursively (e.g. foo(a, bar(), a + bar(a)) -> [["a"],
    [["bar", []], ["a", ["bar", [["a"]]]]], foo(foo(foo(a))) ->
    [["foo", [["foo", ["a"]]]]])

    Arguments:
        instruction (pycparser.c_ast.FuncCall): function call which
            is going to be analyzed in order to get the variables or
            other function calls that are being used in its parameters.
        recursive_struct (bool): if *True*, the name of the struct
            references will be resolved recursively. Otherwise, it will
            not. The default value is *True*.

    Returns:
        list: list of lists where every list will represent a parameter
        of the function call, and every inner list will contain the found
        ID's being used (e.g. foo(1, a, b + bar(c)) -> [[], ["a"],
        ["b", ["bar", [[c]]]]]). If there are not parameters, an empty
        list will be returned

    Raises:
        PycparserException: if the type of the arguments
            are not the expected.
    """
    if not isinstance(instruction, ast.FuncCall):
        raise PycparserException("'instruction' was expected to be"
                                 " 'pycparser.c_ast.FuncCall' but is"
                                 f" '{get_just_type(instruction)}'")
    result = []
    args = instruction.args

    if args is None:
        return result

    args = args.exprs

    for arg in args:
        result.append([])

        arg_instrs = [arg] + get_instruction_path(arg)
        index = 0

        while index < len(arg_instrs):
            arg_instr = arg_instrs[index]

            if isinstance(arg_instr, ast.StructRef):
                aux = ast.StructRef(arg_instr, ".", ast.ID("temporal-var"))
                struct_instrs = get_instruction_path(arg_instr)
                removed_elements = 0

                if recursive_struct:
                    result[-1].append(get_name(aux))
                else:
                    for struct_instr in struct_instrs:
                        if isinstance(struct_instr, ast.ID):
                            result[-1].append(struct_instr.name)
                            break

                while removed_elements <= len(struct_instrs):
                    arg_instrs.remove(arg_instrs[index])
                    removed_elements += 1

                # It is not necessary to make index += 1
                break
            if isinstance(arg_instr, ast.FuncCall):
                result[-1].append([get_name(arg_instr),
                                   get_func_call_parameters_name(arg_instr)])

                func_instrs = get_instruction_path(arg_instr)
                removed_elements = 0

                while removed_elements <= len(func_instrs):
                    arg_instrs.remove(arg_instrs[index])
                    removed_elements += 1

                # It is not necessary to make index += 1
                break
            if isinstance(arg_instr, ast.ID):
                name = arg_instr.name

                while not isinstance(name, str):
                    name = name.name

                result[-1].append(name)

            index += 1

    return result

def get_full_instruction_from_id(all_instructions, reference_id):
    """It looks for an instruction with the ID (i.g. id() method).

    Arguments:
        all_instructions (list): list of elements where should
            be an element with id *reference_id*.
        reference_id (int): ID of the element which we are looking
            for.

    Returns:
        object: element of *all_instructions* if *reference_id*
        matchs with any element. Otherwise, an exception will be raised

    Raises:
        PycparserException: if *reference_id* does not match with any
            element of *all_instructions*. The reason why an exception
            is raised instead of return a value is because any returned
            value could match with id() method, even the *None* value.
    """
    for instruction in all_instructions:
        if id(instruction) == reference_id:
            return instruction

    raise PycparserException(f"element with reference '{reference_id}'"
                             " was not found")
