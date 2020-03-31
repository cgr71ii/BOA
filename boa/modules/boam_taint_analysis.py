"""This file contains the class BOAModuleTaintAnalysis.

The goal of this module is achieve a taint analysis execution
with kildall's algorithm.

The CFG is used as dependency because we need it in order to
execute kildall's algorithm.
"""

# Std libs
from copy import deepcopy
from collections import OrderedDict as odict

# Own libs
from boam_abstract import BOAModuleAbstract
from util import is_key_in_dict, eprint, get_just_type
from own_exceptions import BOAModuleException
import auxiliary_modules.pycparser_util as pycutil
import auxiliary_modules.pycparser_cfg as pycfg

# Pycparser libs
import pycparser.c_ast as ast

class TAConstants:
    cfg_dependency = "boam_cfg.BOAModuleControlFlowGraph"
    cfg_dependency_key = "cfg"
    split_char = "@"    # Character that will be used in order to split the values
                        #  of the rules file for the Sources and Sinks

    id_instr = (#ast.Goto, ast.Label,
                ast.ArrayRef, ast.Decl, ast.Enum, ast.Enumerator,
                ast.FuncCall, ast.ID, ast.NamedInitializer, ast.Struct,
                ast.StructRef, ast.Typedef, ast.Typename, ast.Union)

class BOAModuleTaintAnalysis(BOAModuleAbstract):
    """BOAModuleTaintAnalysis class.

    It implements the necessary methods in order to perform
    the taint analysis technique.
    """

    def initialize(self):
        """It loads the args an initializes the module.

        Raises:
            BOAModuleException: if the CFG is not found in the
                expected format as dependency.
        """
        self.cfg = None

        if (not is_key_in_dict(self.dependencies, TAConstants.cfg_dependency) or
                not is_key_in_dict(self.dependencies[TAConstants.cfg_dependency],
                                   TAConstants.cfg_dependency_key)):
            raise BOAModuleException("it is necessary to have as dependency the module"
                                     f" '{TAConstants.cfg_dependency}' and is expected"
                                     f" to be found with key '{TAConstants.cfg_dependency_key}'"
                                     " in the dependencies", self)

        self.cfg = self.dependencies["boam_cfg.BOAModuleControlFlowGraph"]["cfg"]()
        self.sources = []
        self.sinks = []

        # Load Sources from rules file
        if (is_key_in_dict(self.args, "sources") and
                isinstance(self.args["sources"], list)):
            self.sources = Source.process_sources(self.args["sources"], self)
        else:
            eprint("Warning: no Sources were found in the rules file.")

        # Load Sinks from rules file
        if (is_key_in_dict(self.args, "sinks") and
                isinstance(self.args["sinks"], list)):
            self.sinks = Sink.process_sinks(self.args["sinks"], self)
        else:
            eprint("Warning: no Sinks were found in the rules file.")

        self.taint_analysis = TaintAnalysis(self.cfg, self.sources, self.sinks)

    def process(self, args):
        """It process the given information from the rules
        file and attempts to look for security threats.

        Arguments:
            args: given information.
        """

    def clean(self):
        """It does nothing.
        """

    def save(self, report):
        """It saves the security threads found in a report.
        This method will be invoked after all tokens have been processed.

        Arguments:
            report: report which will contain the threats records.
        """

    def finish(self):
        """It does nothing.
        """

class Sink:
    """It represents a Sink, which in the Taint Analysis terminology
    means a function which should be protected because a bad use of it,
    could lead to a security threat (e.g. system, strcpy, ...).
    However, there are functions which might fell in a security threat
    depending on the affected parameter, so it is important to know
    that information.
    """

    def __init__(self, function_name, dangerous_parameter):
        """It initializes a Sink.

        Arguments:
            function_name (str): function name of the dangerous function.
            dangerous_parameter (list): list which contains the postion of
                the dangerous parameter. If the value is 0, it means that
                all the parameters are dangerous (or none if there is no
                parameters).
        """
        self.function_name = function_name
        self.dangerous_parameter = dangerous_parameter

    @classmethod
    def process_sinks(cls, sinks, module_instance):
        """It process the Sinks from the rules files in order to create
        the Sink instances for the TaintAnalysis class.

        The expected format of the values of *sinks* are elements of
        "function_name@dangerous_parameter".

        Arguments:
            sinks (list): list of *str* which are expected to have the
                explained format.
            module_instance (BOAModuleAbstract): module instance in order
                to have the necessary information for the exceptions.

        Returns:
            list: list of *Sink* instances. Empty list if *sinks*
            is empty

        Raises:
            BOAModuleException: if the format of *sinks* elements are
                not the expected.
        """
        result = []

        for sink in sinks:
            values = sink.split(TAConstants.split_char)
            sink = None

            if len(values) == 2:
                sink = Sink(values[0], values[1])

            if sink is None:
                raise BOAModuleException("could not create a Sink object. Check your"
                                         " rules file in order to have the correct format"
                                         " in the arguments sections, concretely in the"
                                         " 'sinks' list", module_instance)

            result.append(sink)

        return result

class Source:
    """It represents a Source, which in the Taint Analysis terminology
    means something that allows the user to have control over the information
    which is inserted in the program. A Source may be a function, a variable,
    a network package or anything else which the user might alter. Usually,
    the Sources are function calls (e.g. gets()) and a few set of dangerous
    variables (i.e. argc, argv).
    """

    allowed_types = ["function", "variable"]

    def __init__(self, name, stype, function_name_container=None):
        """It initializes a Source.

        Arguments:
            name (str): name of the object reference which contains or allows
                the user to insert data.
            stype (str): type of the object which is the Source (e.g. "function",
                "variable", ...). The possible values of *stype* are in the class
                list *allowed_types*.
            function_name_container (str): optional value which indicates that a
                Source can be found inside a concrete function.

        Raises:
            BOAModuleException: if *stype* is not a value of *Source.allowed_types*.
        """
        self.name = name
        self.type = stype
        self.function_name_container = function_name_container

        if self.type not in Source.allowed_types:
            raise BOAModuleException("the Source type can only contain a value of the"
                                     f" next: '{str(Source.allowed_types)[1:-1]}'", self)

    @classmethod
    def isinstance(cls, source, stype, function_name_container):
        """It helps us to know if a Source instance is of a concrete instance. This
        function is really useful when used with *list(filter())*.

        Arguments:
            source (Source): *Source* instance.
            stype (str): type of *Source*.
            function_name_container (str): function which contains *Source*.

        Returns:
            bool: *True* if *type* matchs with *Source.type* and *function_name_container*
            matchs with *Source.function_name_container*. *False* otherwise
        """
        return source.type == stype and source.function_name_container == function_name_container

    @classmethod
    def process_sources(cls, sources, module_instance):
        """It process the Sources from the rules files in order to create
        the Source instances for the TaintAnalysis class.

        The expected format of the values of *sources* are elements of
        "name@type@function".

        Arguments:
            sources (list): list of *str* which are expected to have the
                explained format.
            module_instance (BOAModuleAbstract): module instance in order
                to have the necessary information for the exceptions.

        Returns:
            list: list of *Source* instances. Empty list if *sources*
            is empty

        Raises:
            BOAModuleException: if the format of *sources* elements are
                not the expected.
        """
        result = []

        for source in sources:
            values = source.split(TAConstants.split_char)
            source = None

            if len(values) == 2:
                source = Source(values[0], values[1])
            elif len(values) == 3:
                source = Source(values[0], values[1], values[2])

            if source is None:
                raise BOAModuleException("could not create a Source object. Check your"
                                         " rules file in order to have the correct format"
                                         " in the arguments sections, concretely in the"
                                         " 'sources' list", module_instance)

            result.append(source)

        return result

class Taint:
    """It represents a Taint, which in Taint Analysis terminology is
    a Source which has a path in the CFG from a Sink until the Source
    itself. The Taint might contain information manipulated, direct
    or indirect, by the user.

    Possible taint status (static analysis):
              MT
              /\\
             /  \\
            /    \\
           T      NT
            \\    /
             \\  /
              \\/
              UNK

    1. UNK: Unknown
    2. T: Tainted
    3. NT: Not Tainted
    4. MT: T + NT
    """

    allowed_status = ["UNK", "T", "NT", "MT"]

    def __init__(self, source, decl, instruction, status):
        """It initializes a Taint.

        Arguments:
            source (Source): *Source* instance which represents the Taint.
            decl (list): list of *pycparser.c_ast.Node* which represents a
                whole instruction declaration of the instruction.
            instruction (list): list of *pycparser.c_ast.Node* which represents
                a whole instruction which tainted the *source*.
            status (str): status of the Taint instance. The allowed values
                are in *Taint.allowed_status* class variable.
        """
        self.source = source
        self.decl = decl
        self.instruction = instruction
        self.status = status

        if self.status not in Taint.allowed_status:
            raise BOAModuleException("the Taint status can only contain a value of the"
                                     f" next: '{str(Taint.allowed_status)[1:-1]}'", self)

    def get_declaration_coord(self):
        """It attempts to return the coord variable of *self.decl*.

        Returns:
            pycparser.plyparser.Coord: if could not retrieve the coord element,
            *None* will be returned
        """
        if (self.decl is not None and len(self.decl) != 0):
            return self.decl[0].coord

        return None

    def get_instruction_coord(self):
        """It attempts to return the last instruction which tainted the declaration
        (*self.instruction*).

        Returns:
            pycparser.plyparser.Coord: if could not retrieve the coord element,
            *None* will be returned
        """
        if (self.instruction is not None and len(self.instruction) != 0):
            return self.instruction[0].coord

        return None

    def is_tainted(self):
        """It checks if the current instance is tainted.

        Returns:
            bool: *True* if tainted. Otherwise, *False*
        """
        if self.status in ["T", "MT"]:
            return True

        return False

class TaintAnalysis:
    """TaintAnalysis class.

    It performs the Taint Analysis.
    """

    def __init__(self, cfg, sources, sinks):
        """It initializes the class.

        Arguments:
            cfg (auxiliary_modules.pycparser_cfg.CFG): Control Flow Graph.
            sources (list): list of *Source* which will contain the sources
                in the following taint analysis.
            sinks (list): list of *Sink* which will contain the sinks in the
                following taint analysis.
        """
        self.cfg = cfg
        self.sources = sources
        self.sinks = sinks
        self.taints = []

        # TODO temporal (it will be removed)
        self.kildall("main")

    def kildall(self, function_name):
        """It executes Kildall's algorithm in order to perform the Taint
        Analysis.

        Arguments:
            function_name (str): name of the function which will be looked
                for in the CFG.

        Returns:
            list: list of *Taint* which will have information about the
            variables of the function

        Raises:
            BOAModuleException: when something unexpected happens.
        """
        result = []
        instructions = self.cfg.get_cfg(function_name)

        if instructions is None:
            eprint(f"Warning: function '{function_name}' was not found in the CFG.")
            return result

        real_instructions = pycfg.Instruction.get_instructions(instructions)
        func_body = real_instructions[0].body

        if not isinstance(func_body, ast.Compound):
            raise BOAModuleException("the first instruction of the function was expected"
                                     " to be 'pycparser.c_ast.Compound', but is"
                                     f" '{get_just_type(func_body)}'", self)

        func_body_instructions = pycutil.get_instruction_path(func_body)
        func_body = func_body_instructions[0]   # First instruction will be the next of Compound

        # Get all the known Sources (initialization), which can be or not declared in the function
        known_tainted =\
            self.get_sources("variable", function_name) + self.get_sources("variable", None)
        variables_decl = []                 # All the found variables in the current function

        # Get the function parameters (if any)
        function_parameters = pycutil.get_function_decl_parameters(real_instructions[0])
        # Get the function variables (if any)
        function_variables = pycutil.get_function_decl_variables(real_instructions[0])

        # Store the fuction parameters and variables
        variables_decl.extend(function_parameters)
        variables_decl.extend(function_variables)

        # Initialize all the Taint instances with the variables of the function
        #  (initializes the algorithm)
        tainted_variables_names = list(map(lambda x: x.name, known_tainted))
        input_dict = odict()
        # TODO remove last parameter or set to False
        whole_instructions = pycutil.get_full_instruction_function(real_instructions, True)

        worklist = []

        if len(whole_instructions) != 0:
            worklist = [whole_instructions[0]]

        # Initialization of the first instruction
        self.initialize_input_dict(input_dict, variables_decl, function_name,
                                   tainted_variables_names, result, whole_instructions[0],
                                   None)

        visited = []
        # Store the temporal taints of control structures
        # It will be removed when the end of the control structure is reached
        # TODO
        temporal_taints_of_control_structures = []

        # Work with the worklist and the CFG
        while len(worklist) != 0:
            # Take the first instruction of the worklist
            first_instruction = worklist[0]
            # Take off the first instruction of the worklist
            worklist.remove(worklist[0])

            outputs = []

            whole_instruction = first_instruction
            whole_instruction_index = whole_instructions.index(whole_instruction)

            if len(whole_instruction) == 0:
                # TODO check if this is correct or append the next whole instruction to
                #  worklist before continue
                continue

            # TODO get the real value of output

            ids = self.get_all_id_names(whole_instruction)

            if isinstance(whole_instruction[0],
                          pycutil.PycparserUtilConstants.strict_compound_instr):
                compound_element_identifier =\
                    self.get_taint_information_from_compound_element(whole_instruction,
                                                                     whole_instructions,
                                                                     input_dict, ids)

                already_inserted = len(list(filter(lambda x:
                                                   x[3] == compound_element_identifier[3],
                                                   temporal_taints_of_control_structures))) > 0

                if not already_inserted:
                    temporal_taints_of_control_structures.append(compound_element_identifier)



            if len(pycutil.get_instructions_of_instance(ast.FuncCall, whole_instruction)) != 0:
                # There are func call elements in the current whole instruction
                # TODO Check if assignment
                # TODO Store which arguments passed to the func call are T or NT
                #  and from which function is being called from which other
                pass

            # Check if is a variable declaration or assignment
            if (pycutil.is_variable_decl(whole_instruction[0]) or
                    isinstance(whole_instruction[0], ast.Assignment)):
                self.process_output_from_decl_or_asign(outputs, whole_instruction,
                                                       input_dict,
                                                       tainted_variables_names,
                                                       ids, result)

            # Once reached this point, outputs is already calculated

            # Check if the current whole instruction is inside a control flow structure
            #  and if the control structure is tainted
            for control_structure in temporal_taints_of_control_structures:
                if (control_structure[3] <= whole_instruction_index < control_structure[4] and
                        control_structure[1]):
                    # The current whole instruction is inside a control flow structure tainted
                    control_structure_status = control_structure[2]
                    output_index = 0

                    # Update the tainted values of all the variables because are inside
                    #  a control flow structure tainted
                    for var, output in outputs:
                        if output == "NT":
                            # The variable was not tainted, and now it is
                            outputs[output_index][1] = control_structure_status
                        elif (output == "T" and control_structure_status == "MT"):
                            # The variable was tainted, but now also contains the value "NT"
                            #  "T" + "NT" -> "MT"
                            outputs[output_index][1] = control_structure_status

                        output_index += 1

            # [instruction index, current result, new output values, current result, succ]
            # If we visit the same values again, it means we have reached a loop
            visiting = [whole_instructions.index(whole_instruction),
                        input_dict[list(input_dict)[-1]], outputs,
                        list(map(lambda x: x[0], result)), None]

            # TODO remove the following debug print
            print("-----------------------------------------")
            print(f"index: {visiting[0]}")
            print(visiting[1])

            # Get succ whole instructions from current whole instruction
            succs = self.get_succs_from_whole_instruction(whole_instruction, whole_instructions,
                                                          instructions, real_instructions)

            # Sort reversely because the instructions are appended in the front of the worklist
            succs.sort(reverse=True, key=whole_instructions.index)

            for succ_instruction in succs:
                visiting[-1] = id(succ_instruction)

                if succ_instruction[0] not in real_instructions:
                    eprint("Warning: the CFG has taken to a instruction of other"
                           " function and 'kildall' function has been designed to"
                           " have all the instructions in the same function.")
                    continue

                if not is_key_in_dict(input_dict, id(succ_instruction)):
                    self.initialize_input_dict(input_dict, variables_decl,
                                               function_name,
                                               tainted_variables_names, result,
                                               succ_instruction, whole_instruction)

                input_value = input_dict[id(succ_instruction)]
                append_succ = False

                for var, output in outputs:
                    taint_status = input_value[var]

                    if output != taint_status:
                        if taint_status == "UNK":
                            # New taint status will be output, which is "T" or "NT"
                            input_dict[id(succ_instruction)][var] = output
                            append_succ = True
                        elif taint_status != "MT":
                            # New taint status will be "MT" because output is "T" or "NT" and
                            #  taint_status the other, so we have the set {"T", "NT"} = "MT"
                            input_dict[id(succ_instruction)][var] = "MT"
                            append_succ = True

                abort = False

                # Check if we are in a loop
                if visiting in visited:
                    # We have visited this concrete result before, so we are in a loop -> abort
                    abort = True

                if (append_succ or not abort):
                    # A variable was affected, so we process the dependency

                    if (len(succ_instruction) != 0 and
                            isinstance(succ_instruction[0], pycfg.EndOfIfElse)):
                        # The succ instruction is the end of if-else, which means that
                        #  we might have not finished the whole if-else statement, so
                        #  we append instead of insert
                        worklist.append(succ_instruction)
                    else:
                        worklist.insert(0, succ_instruction)

                    # Append this current and concrete result as visited
                    visited.append(deepcopy(visiting))

            # TODO remove next line used for debugging
            print(f"worklist: {list(map(whole_instructions.index, worklist))}")

        # Get only those Taint instantes which are tainted (T and MT status)
        result = list(filter(lambda x: x[1].status == "T" or x[1].status == "MT", result))

        return result

    def get_taint_information_from_compound_element(self, whole_instruction, whole_instructions,
                                                    input_dict, ids):
        """It analyzes a compound element and gets taint information and
        useful information for the taint analysis.

        Arguments:
            whole_instruction (list): list of *pycparser.c_ast.Node* instructions
                which represents a whole instruction.
            whole_instructions (list): list of lists of *pycparser.c_ast.Node* which
                represents all the full instructions of the current function, like
                *whole_instruction*.
            input_dict (dict): dict of dicts of *str* which represents the tainted
                variables of the current analysis.
            ids (list): list of *str* which contains all the ID's of the current
                statement.

        Returns:
            list: list which contains the following information:\n
            1. pycparser.c_ast.Node: *whole_instruction[0]* (for debugging purposes).
            2. bool: *True* if the statement is tainted.
            3. str: taint status
            4. int: index where the statement starts (from all the whole instructions)
            5. int: index where the statement finishes (from all the whole instructions).
               It does not include the instruction which targets!
        """
        # The instruction might have a Compound element strictly
        compound_element_identifier = []

        # Append which type of compound instruction is (debbug purposes)
        compound_element_identifier.append(whole_instruction[0])
        # Append if the statement is tainted (T or MT in any of the variables used
        #  in the statement (e.g. if (tainted){indirectly tainted}))
        # Retrieve the tainted variables from the last result
        not_tainted_vars_last_result = list(filter(lambda item: item[1] == "NT",
                                                   input_dict[list(input_dict)[-1]]\
                                                       .items()))
        tainted_vars_last_result = list(filter(lambda item: item[1] in ["T", "MT"],
                                               input_dict[list(input_dict)[-1]].items()))
        tainted_vars_last_result_names = list(map(lambda var_taint: var_taint[0],
                                                  tainted_vars_last_result))
        # Check if the tainted variables from the last result match with the
        #  found ID's in the current whole instruction
        compound_element_identifier.append(len(list(filter(
            lambda x: x in tainted_vars_last_result_names,
            ids))) != 0)

        # Append output value according to the tainted value of last result
        if not compound_element_identifier[-1]:
            # There are not tainted variables
            compound_element_identifier.append("NT")
        elif (len(not_tainted_vars_last_result) != 0 and
                len(tainted_vars_last_result) != 0):
            # There are tainted and not tainted variables
            compound_element_identifier.append("MT")
        else:
            # There are tainted variables
            compound_element_identifier.append("T")

        # Append the index in which this compound element starts
        compound_element_identifier.append(whole_instructions.index(whole_instruction))

        # Append the index in which this compound element finishes
        compound_instructions = [whole_instruction[0]] +\
            pycutil.get_instruction_path(whole_instruction[0])
        index = compound_element_identifier[-1]

        while index < len(whole_instructions):
            if (len(whole_instructions[index]) != 0 and
                    whole_instructions[index][0] not in compound_instructions):
                # We have found the first instruction which does not belongs to
                #  the compound element. Now, index contain the position where
                #  the compound element finishes (not including that element!)
                break

            index += 1

        # Append index because contains the position where the compund elmenet finishes
        # The instruction which has the position targetted by index does not belong to
        #  the compound element!
        compound_element_identifier.append(index)

        return compound_element_identifier

    def process_output_from_decl_or_asign(self, outputs, whole_instruction,
                                          input_dict, tainted_variables_names,
                                          ids, result):
        """It process the output from a variable declaration or assignment.

        Arguments:
            outputs (list): list of tuple of format (str, str) which contains
                the output values for the found variables for all the processed
                whole instructions. In this function will be appended the values
                for *whole_instruction*. This argument will mutate.
            whole_instruction (list): list of *pycparser.c_ast.Node* wich contains
                the instructions of the current whole instruction which is going
                to be analyzed in case that is a variable declaration.
            input_dict (dict): dict of dicts which contains the tainted
                information.
            tainted_variables_names (list): list of str which contains the known
                tainted variables which might be or might not in the current
                function and are known since the begin of the process of the
                current function.
            ids (list): list of str which contains the found ID's in
                *whole_instruction*.
            result (list): list of tuples of format (str, *Taint*) which contains
                taint information about all the variables in the function.
        """
        name = None

        if isinstance(whole_instruction[0], ast.Assignment):
            name = whole_instruction[0].lvalue.name
        else:
            name = whole_instruction[0].name

        ids_valid_index = 1

        while not isinstance(name, str):
            name = name.name
            ids_valid_index += 1

        init = None

        if isinstance(whole_instruction[0], ast.Assignment):
            init = whole_instruction[0].rvalue
        else:
            init = whole_instruction[0].init    # Initialization of the declaration

        index = self.get_result_index_by_var_name(result, name)

        if init is None:
            # The variable is not initialized, so is not tainted
            outputs.append([name, "NT"])
        else:
            # The variable is initialized, so we have to check if is tainted

            if len(input_dict) != 0:
                # Get the taint status of the last analyzed instruction
                last_key = list(input_dict)[-1]
                current_tainted_variables = list(filter(
                    lambda y: input_dict[last_key][y] == "T",
                    input_dict[last_key]))

                # Append the known tainted variables
                current_tainted_variables += tainted_variables_names

                # Get the tainted variables from the variables of the
                #  initialization
                tainted = list(filter(lambda x: x in ids[ids_valid_index:],
                                      current_tainted_variables))

                # Check if there are any tainted variables in the
                #  initialization
                if len(tainted) != 0:
                    outputs.append([name, "T"])

                    if index is not None:
                        result[index][1].instruction = whole_instruction
                else:
                    # There are not tainted variables (or unknown),
                    #  so, by the moment, NT
                    outputs.append([name, "NT"])

        # Set the declaration if not set
        if (index is not None and result[index][1].decl is None):
            result[index][1].decl = whole_instruction

    def get_result_index_by_var_name(self, result, name):
        """It looks for the index in *result* variable with the name
        of a variable.

        Arguments:
            result (list): list of tuples of format (str, *Taint*) which
                contains taint information about all the variables of the
                function.
            name (str): name of the variable which we want the index of
                *result*.

        Returns:
            int: index of the place of the tuple which contains the name
                of *name*.
        """
        for index, _result in enumerate(result, 0):
            if _result[0] == name:
                return index

        return None

    def get_all_id_names(self, whole_instruction, struct_only_first_id=True):
        """It looks for the ID which are being used in a whole instruction.

        Arguments:
            whole_instruction (list): list of *pycparser.c_ast.Node* which represents
                a whole instruction.
            struct_only_first_id (bool): if *True*, when an instruction is instance of
                StructRef, only the first ID will be retrieved and the rest will be ignored.
                If *False*, the format will be "id1.id2.id3 ...". The default value is
                *True*.

        Returns:
            list: list of *str* which are the names of the found ID (e.g. variable names,
            function calls, ...)
        """
        result = []
        index = 0

        while index < len(whole_instruction):
            instruction = whole_instruction[index]

            if isinstance(instruction, TAConstants.id_instr):
                if isinstance(instruction, ast.StructRef):
                    struct_instructions = pycutil.get_instruction_path(instruction)
                    ids = pycutil.get_instructions_of_instance(ast.ID, struct_instructions)

                    if len(ids) == 0:
                        continue

                    # Get the names
                    for _index, _ids in enumerate(ids, 0):
                        while not isinstance(_ids, str):
                            _ids = _ids.name

                        ids[_index] = _ids

                    count = 0
                    _index = index

                    while (_index + 1 < len(whole_instruction) and
                           isinstance(whole_instruction[_index + 1], ast.ID)):
                        _index += 1
                        count += 1

                    if struct_only_first_id:
                        result.append(ids[0])

                        # Avoid to get all the accesses to the struct
                        #  (e.g. myStruct.a.b = c will skip "a" and "b" but not "c",
                        #   myStruct.a.d(z.q, g.s) will skip "a", "d", "q" and "s") 
                        #index += count

                    else:
                        result += ids[0:count]

                    index += count
                elif isinstance(instruction, (ast.ArrayRef, ast.Decl, ast.Enum, ast.Enumerator,
                                              ast.FuncCall, ast.ID, ast.NamedInitializer,
                                              ast.Struct, ast.Typedef, ast.Typename, ast.Union)):
                    name = instruction.name

                    if (isinstance(instruction, ast.FuncCall) and
                            isinstance(name, ast.StructRef)):
                        struct_instructions = pycutil.get_instruction_path(instruction)
                        _index = 0

                        for _index, struct_instruction in enumerate(struct_instructions[1:], 0):
                            if not isinstance(struct_instruction, ast.ID):
                                break

                        while len(struct_instructions) != _index + 1:
                            struct_instructions.remove(struct_instructions[-1])

                        # Function being called from a struct
                        func_call_name = ""
                        aux = self.get_all_id_names(struct_instructions, False)

                        for func_call in aux:
                            func_call_name += f"{func_call}."

                        if len(func_call_name) != 0:
                            func_call_name = func_call_name[0:-1]

                        result.append(func_call_name)

                        index += len(aux) + 1
                    else:
                        while not isinstance(name, str):
                            name = name.name
                            index += 1

                        result.append(name)
                else:
                    raise BOAModuleException("found instruction of type"
                                             f" '{get_just_type(instruction)}'"
                                             " which is defined but not expected (update the"
                                             " function in order to fix it)", self)

            index += 1

        return result

    def get_succs_from_whole_instruction(self, whole_instruction, whole_instructions,
                                         instructions, real_instructions):
        """It returns the whole instructions which are succs of a concrete whole instruction.

        Arguments:
            whole_instruction (list): list of *pycparser.c_ast.Node* which represents a whole
                instruction and is the whole instruction from where we want to know its succs.
            whole_instructions (list): list of lists of *pycparser.c_ast.Node* which represents
                the whole instructions of a function.
            instructions (list): list of *pycparser_cfg.Instruction* which are all the
                instructions of the function.
            real_instructions (list): list of *pycparser.c_ast.Node* which are all the real
                instructions of the function.

        Returns:
            list: list of lists of *pycparser.c_ast.Node* which represents the succs whole
            instructions of *whole_instruction*
        """
        succs = []

        # Look for the succesive whole instructions. The first instruction with
        #  succesive instruction out of the current whole instruction will be
        #  the one used to get all the succesive whole instructions (it makes
        #  easier the searching)
        for instruction in whole_instruction:
            # Check if instruction is real or fake
            if isinstance(instruction, pycutil.PycparserUtilConstants.fake_instr):
                # The instruction is fake and will not be found in real_instructions
                continue
            instruction_index = real_instructions.index(instruction)
            instr = instructions[instruction_index]
            instr_succs = instr.get_succs()
            found = False

            # Check if the succ instructions are from other whole instruction
            for instr_succ in instr_succs:
                real_instr_succ = instr_succ.get_instruction()

                if real_instr_succ not in whole_instruction:
                    # The current instruction's sucessive instructions does not
                    #  belong to the current whole instruction, so look for the
                    #  whole instruction where belongs
                    found = True

                    for whole in whole_instructions:
                        # Look for the whole instruction which contains the succesive
                        #  instruction which is not the current whole instruction
                        if real_instr_succ in whole:
                            # Whole instruction which contains the succesive instruction
                            #  found. Append the whole current instruction as succesive
                            succs.append(whole)
                            break

            # When any succesive instructions of the current whole instruction contain
            #  a succesive instruction out of the current whole instruction, the searching
            #  will stop in order to optimize the difficulty of look for the succesive
            #  instruction with the "whole instruction" context
            # TODO check if is better idea to get all the succ of the whole instruction
            #  which means to remove the 2 following lines
            if found:
                break

        return succs

    def initialize_input_dict(self, input_dict, variables_decl, function_name,
                              tainted_variables_names, result, instruction,
                              instruction_reference):
        """It initializes an entry in the input dictionary for a concrete variable
        for all the variables.

        Arguments:
            input_dict (dict): where the initialization is done.
            variables_decl (list): list of *pycparser.c_ast.Decl* which contains
                all the variables of the function *function_name*.
            function_name (str): function name of the function.
            tainted_variables_names (list): list of *str* which contains all the
                known taints.
            result (list) list of tuples of format (str, *Taint*) which contains
                all the taint information about all the variables of the function.
            instruction (list): list of instructions of *pycparser.c_ast.Node*
                which is going to be initialized in *input_dict*. It represents
                a whole instruction.
            instruction_reference (list): list of instructions of
                *pycparser.c_ast.Node* which, if different of *None*, will
                have the initial values for the initialization. If *None*,
                initialization will be done with *tainted_variables_names*.
                It represents a whole instruction.

        Raises:
            BOAModuleException: if *instruction_reference* is not *None* and is not
                in *input_dict*.
        """
        for index, variable_decl in enumerate(variables_decl, 0):
            variable_decl_name = variable_decl.name
            # Initially, all variables will be "UNK", but when declaration is found, it will change
            taint_status = "UNK"

            # Initialize the inputs with a dictionary
            if not is_key_in_dict(input_dict, id(instruction)):
                input_dict[id(instruction)] = {}

            if instruction_reference is not None:
                if not is_key_in_dict(input_dict, id(instruction_reference)):
                    raise BOAModuleException("was expected to find an instruction reference"
                                             " in input dictionary, but was not found", self)
                # The taint value will be taken from the instruction reference
                taint_status = input_dict[id(instruction_reference)][variable_decl_name]
            elif variable_decl_name in tainted_variables_names:
                # The variable is tainted due to the known taints
                taint_status = "T"

            # Initial information
            input_dict[id(instruction)][variable_decl_name] = taint_status

            if instruction_reference is not None:
                # Update the taint status
                result[index][1].status = taint_status
            else:
                # Create a new entry

                source = Source(variable_decl_name, "variable", function_name)
                # The variable declaration and instruction will be set later while the analysis
                #  is being performed
                taint = Taint(source, None, None, taint_status)

                # We append all the taint information of the variables and later it will be cleaned
                result.append((variable_decl_name, taint))

    def get_sources(self, stype=None, function_name_container=None):
        if (stype is None and function_name_container is None):
            return self.sources

        return\
        list(filter(lambda source: Source.isinstance(
            source,
            stype,
            function_name_container),
                    self.sources))
