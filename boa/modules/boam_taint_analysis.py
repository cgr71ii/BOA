"""This file contains the class BOAModuleTaintAnalysis.

The goal of this module is achieve a taint analysis execution
with kildall's algorithm.

The CFG is used as dependency because we need it in order to
execute kildall's algorithm.

Things which this implementation DOES NOT do:
1. Does not resolve graph cyclic dependencies within function
   calls of functions defined in the same file.
2. Does not apply a concrete order when executing kildall's
   algorithm.
3. It ignores those function calls which are not defined as
   a Source nor Sink.
"""

# Std libs
from copy import deepcopy
from collections import OrderedDict as odict

# Own libs
from constants import Meta
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

        self.append_tainted_variables_to_report = True

        if is_key_in_dict(self.args, "append_tainted_variables_to_report"):
            if self.args["append_tainted_variables_to_report"].lower() == "false":
                self.append_tainted_variables_to_report = False
            elif self.args["append_tainted_variables_to_report"].lower() != "true":
                raise BOAModuleException("the argument "
                                         "'append_tainted_variables_to_report'"
                                         " only allows the values 'true' or 'false'")

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
        self.results = None

    def process(self, args):
        """It process the given information from the rules
        file and attempts to look for security threats.

        Arguments:
            args: given information.
        """
        self.results = self.taint_analysis.apply_kildall_to_all_functions()

    def clean(self):
        """It does nothing.
        """

    def save(self, report):
        """It saves the security threads found in a report.
        This method will be invoked after all tokens have been processed.

        Arguments:
            report: report which will contain the threats records.
        """
        threats = self.taint_analysis.threats
        results = self.results
        severity_instance = report.get_severity_enum_instance_by_who(self.who_i_am)

        if severity_instance is None:
            eprint(f"Error: could not append threat records in '{self.who_i_am}'."
                   " Wrong severity enum instance.")
            return

        self.save_threats(report, threats, severity_instance)

        if self.append_tainted_variables_to_report:
            self.save_results(report, results, severity_instance)

    def save_threats(self, report, threats, severity_instance):
        """It appends the found threats in Taint Analysis.

        Arguments:
            report: report which will contain the threats records.
            threats (list): list of dicts which contain information
                about the found threats.
            severity_instance: severity instance used to retrieve
                the position of concrete severity from name.
        """
        for threat in threats:
            if threat["threat"] == "sink":
                row = -1
                col = -1
                affected_parameter = int(threat["affected_parameter"])
                func_name = threat["func_name"]
                container_func_name = threat["container_func_name"]
                instruction = threat["instruction"]
                instruction_coord = None

                if instruction is not None:
                    instruction_coord = instruction.coord

                severity = severity_instance[threat["severity"]]

                if instruction_coord is not None:
                    row = int(str(instruction_coord).split(':')[-2])
                    col = int(str(instruction_coord).split(':')[-1])

                description = ""
                description += f"function '{container_func_name}': a sink "
                description += f"(function '{func_name}') with a"
                description += " tainted value has been found, in"
                description += f" the parameter with position '{affected_parameter}'"
                description += " (the first parameter starts with 1)"

                advice = ""
                advice += "try to avoid that the user has access to information"
                advice += " which could reach dangerous functions unless that is"
                advice += " your goal"

                rtn_code = report.add(self.who_i_am,
                                      description,
                                      severity,
                                      advice,
                                      row,
                                      col)

                if rtn_code != Meta.ok_code:
                    eprint("Error: could not append a threat"
                           f" record (status code: {rtn_code})"
                           f" in '{self.who_i_am}'.")

    def save_results(self, report, results, severity_instance,
                     severity_value="INFORMATIONAL"):
        """It appends the results of the Taint Analysis, which means
        to display those variables which were tainted. Just
        informational.

        Arguments:
            report: report which will contain the threats records.
            results (dict): dict with the functions of the file as keys
                and the results as values.
            severity_instance: severity instance used to retrieve
                the position of concrete severity from name.
            severity_value (str): severity to use in the report. The
                default value is "INFORMATIONAL" of
                *severity_syslog.SeveritySyslog*.
        """
        for function, result in results.items():
            for variable in result:
                row = -1
                col = -1
                variable_name = variable[0]
                taint = variable[1]
                taint_status = taint.status
                instruction = taint.instruction
                instruction_coord = None

                if (instruction is not None and len(instruction) != 0):
                    instruction_coord = instruction[0].coord

                severity = severity_instance[severity_value]

                if instruction_coord is not None:
                    row = int(str(instruction_coord).split(':')[-2])
                    col = int(str(instruction_coord).split(':')[-1])

                description = ""
                description += f"function '{function}': variable"
                description += f" '{variable_name}' is tainted with status"
                description += f" '{taint_status}' which means that the variable"

                if taint_status == "T":
                    description += " is, if is not a false positive, tainted"
                else:
                    description += " could be tainted or not, because has"
                    description += " both status (i.e. tainted and not tainted)"

                advice = None

                rtn_code = report.add(self.who_i_am,
                                      description,
                                      severity,
                                      advice,
                                      row,
                                      col)

                if rtn_code != Meta.ok_code:
                    eprint("Error: could not append a threat"
                           f" record (status code: {rtn_code})"
                           f" in '{self.who_i_am}'.")

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

        Raises:
            BOAModuleException: if *dangerous_parameter* is not an integer.
        """
        self.function_name = function_name
        self.dangerous_parameter = int(dangerous_parameter)

        try:
            self.dangerous_parameter = int(self.dangerous_parameter)
        except:
            raise BOAModuleException("'dangerous_parameter' has to be number", self)

    @classmethod
    def get_instance(cls, args):
        """Wrapper method to get an instance initialized with a list.

        Arguments:
            args (list): list of arguments to initialize the *Sink*.

        Returns:
            Sink: sink instance initialized with *args*

        Raises:
            BOAModuleException: check *Sink.__init__* method.
        """
        return Sink(*args)

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

            # Check if any value was not set (i.e. "@@" or "....@")
            for index, value in enumerate(values):
                if len(value) == "":
                    values[index] = None

            #if len(values) == 2:
            #    sink = Sink(values[0], values[1])

            sink = Sink.get_instance(values)

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
    variables (e.g. argc, argv, ...).
    """

    allowed_types = ("function", "variable")
    allowed_how = ("argument", "targ")

    def __init__(self, name, stype, function_name_container=None, how=None,
                 affected_argument_position=None, tainted_argument_position=None):
        """It initializes a Source.

        Arguments:
            name (str): name of the object reference which contains or allows
                the user to insert data.
            stype (str): type of the object which is the Source (e.g. "function",
                "variable", ...). The possible values of *stype* are in the class
                list *allowed_types*.
            function_name_container (str): optional value which indicates that a
                Source can be found inside a concrete function.
            how (str): optional value which indicates how and who affects the Source.
                The possible values of *how* are in the class list *allowed_how*.
            affected_argument_position (str): optional value which indicates which
                argument, or even other variable, is affected.
            tainted_argument_position (str): optional value which indicates that if
                the argument indicated by *tainted_argument_position* is tainted,
                then the argument in *affected_argument_poition* position is affected,
                but if not tainted, then is not affected.

        Raises:
            BOAModuleException: if *stype* is not a value of *Source.allowed_types*.
                If *how* is specified and is not a value of *allowed_how*. If
                *affected_argument_position* or *tainted_argument_position* are
                specified and are not integers.
        """
        self.name = name
        self.type = stype
        self.function_name_container = function_name_container
        self.how = how
        self.affected_argument_position = affected_argument_position
        self.tainted_argument_position = tainted_argument_position

        try:
            if self.affected_argument_position is not None:
                self.affected_argument_position = int(self.affected_argument_position)

                if self.affected_argument_position < 0:
                    raise BOAModuleException("if 'affected_argument_position' is"
                                             " specified, has to be greater or equal"
                                             " to 0", self)
        except ValueError:
            raise BOAModuleException("if 'affected_argument_position' is"
                                     " specified, has to be number", self)

        try:
            if self.tainted_argument_position is not None:
                self.tainted_argument_position = int(self.tainted_argument_position)

                if self.tainted_argument_position <= 0:
                    raise BOAModuleException("if 'tainted_argument_position' is"
                                             " specified, has to be greater to 0",
                                             self)
        except ValueError:
            raise BOAModuleException("if 'tainted_argument_position' is"
                                     " specified, has to be number", self)

        if self.type not in Source.allowed_types:
            raise BOAModuleException("the Source type can only contain a"
                                     " value of the next list: "
                                     f"'{str(Source.allowed_types)[1:-1]}'", self)

        if (self.how is not None and self.how not in Source.allowed_how):
            raise BOAModuleException("the 'how' argument in Source can only"
                                     " contain a value of the next list: "
                                     f"'{str(Source.allowed_how)[1:-1]}'", self)

    @classmethod
    def get_instance(cls, args):
        """Wrapper method to get an instance initialized with a list.

        Arguments:
            args (list): list of arguments to initialize the *Source*.

        Returns:
            Source: source instance initialized with *args*

        Raises:
            BOAModuleException: check *Source.__init__* method.
        """
        return Source(*args)

    @classmethod
    def isinstance(cls, source, stype, function_name_container=None, how=None,
                   affected_argument_position=None, tainted_argument_position=None):
        """It helps us to know if a Source instance is of a concrete instance. This
        function is really useful when used with *list(filter())*.

        Arguments:
            source (Source): *Source* instance.
            stype (str): type of *Source*.
            function_name_container (str): function which contains *Source*.
            how (str): how and who is affected by *Source*.
            affected_argument_position (str): position of the argument or variable
                affected.
            tainted_argument_position (str): if tainted, then
                *affected_argument_position* is affected.

        Returns:
            bool: *True* if *type* matchs with *Source.type* and *function_name_container*
            matchs with *Source.function_name_container*. *False* otherwise
        """
        if (source.type == stype and
                source.function_name_container == function_name_container and
                source.how == how and
                source.affected_argument_position == affected_argument_position and
                source.tainted_argument_position == tainted_argument_position):
            return True

        return False

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

            # Check if any value was not set (i.e. "@@" or "....@")
            for index, value in enumerate(values):
                if len(value) == 0:
                    values[index] = None

            source = Source.get_instance(values)

            if source is None:
                raise BOAModuleException("could not create a Source object. Check your"
                                         " rules file in order to have the correct format"
                                         " in the arguments sections, concretely in the"
                                         " 'sources' list", module_instance)

            result.append(source)

        return result

class Taint:
    """It represents a Taint, which in Taint Analysis terminology is
    a Source (we are talking about a Source like a real Source (variable
    or function which introduces information possibly manipulated by the
    user) or a variable which we could call "fake" Source because is
    derived from a real Source) which has a path in the CFG from a Sink
    until the Source itself. The Taint might contain information
    manipulated, direct or indirectly, by the user.

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

    allowed_status = ("UNK", "T", "NT", "MT")

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
        self.threats = []

    def apply_kildall_to_all_functions(self, main_first_if_defined=True):
        """It applies kildall's algorithm to all the defined functions
        in the file: *self.kildall(function)*.

        Arguments:
            main_first_if_defined (bool): if *True* and *main* function
                is defined, the *main* function will be the first in be
                analyzed with kildall's algorithm. Otherwise, the order
                of the analysis will be decided by
                *self.cfg.get_function_calls().keys()*

        Returns:
            dict: dict with the functions as key and the result of
            kidall's algorithm as value
        """
        functions = list(self.cfg.get_function_calls().keys())
        results = {}

        if (main_first_if_defined and "main" in functions):
            index = functions.index("main")

            if index != 0:
                functions.remove("main")
                functions.insert(0, "main")

        for function in functions:
            result = self.kildall(function)
            results[function] = result

        return results

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
            self.get_sources(["variable", function_name]) +\
                self.get_sources(["variable", None])
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
        whole_instructions = pycutil.get_full_instruction_function(real_instructions)

        worklist = []

        if len(whole_instructions) != 0:
            worklist = [whole_instructions[0]]

        # Initialization of the first instruction
        self.initialize_input_dict(input_dict, variables_decl, function_name,
                                   tainted_variables_names, result, whole_instructions[0],
                                   None)

        visited = []
        # Store the taints of control flow structures to affect the inner statements
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
                continue

            ids = self.get_all_id_names(whole_instruction)

            # Control flow structures (inheritance of taints)
            # Avoid literal Compound elements because does not add any relevant
            #  information
            if (isinstance(whole_instruction[0],
                           pycutil.PycparserUtilConstants.strict_compound_instr) and
                    not isinstance(whole_instruction[0], ast.Compound)):
                compound_element_identifier =\
                    self.get_taint_information_from_compound_element(whole_instruction,
                                                                     whole_instructions,
                                                                     input_dict, ids)

                if compound_element_identifier is not None:
                    already_inserted = len(list(
                        filter(lambda x:
                               x[3] == compound_element_identifier[3],
                               temporal_taints_of_control_structures))) > 0

                    if not already_inserted:
                        temporal_taints_of_control_structures\
                            .append(compound_element_identifier)

            func_calls = pycutil.get_instructions_of_instance(ast.FuncCall, whole_instruction)

            # Func calls (check sources and sinks)
            if len(func_calls) != 0:
                # There are func call elements in the current whole instruction

                for func_call in func_calls:
                    # Check sources
                    self.check_sources(func_call, input_dict,
                                       outputs, function_name)
                    # Check if any taint variable reached a sink
                    self.check_sinks(func_call, result, function_name)

            variable_decls = [whole_instruction]

            # Check if there are variable declarations or assignments inside
            #  a structure (i.e. the main instruction is not a declaration
            #  nor assingment, but that does not mean which could have not
            #  declarations or assignments)
            if (not (pycutil.is_variable_decl(whole_instruction[0]) or
                     isinstance(whole_instruction[0], ast.Assignment))):
                # There are declarations or assignments inside a structure
                #  (e.g. for(int i = 0; ...; ...);)
                variable_decls =\
                    pycutil.get_instructions_of_instance(ast.Decl, whole_instruction)
                aux_result = []

                for index, variable_decl in enumerate(variable_decls):
                    if pycutil.is_variable_decl(variable_decl):
                        variable_decls[index] = pycutil.get_full_instruction(
                            variable_decl,
                            real_instructions)

                        for aux in variable_decls[index]:
                            aux_result.append(aux)

                variable_decls = aux_result

            # Check if there are variable declarations or assignments
            for variable_decl in variable_decls:
                if (pycutil.is_variable_decl(variable_decl[0]) or
                        isinstance(variable_decl[0], ast.Assignment)):
                    current_ids = self.get_all_id_names(variable_decl)

                    # Initialize those variables which have "UNK" status
                    self.process_output_from_decl_or_asign(outputs, variable_decl,
                                                           input_dict,
                                                           tainted_variables_names,
                                                           current_ids, result)
                    # Once initialized, check the Sources knowing that are initialized!
                    self.check_sources(variable_decl[0], input_dict,
                                       outputs, function_name)

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
                        # Check if "var" is defined in the function
                        if self.get_result_index_by_var_name(result, var) is None:
                            # Using variable not defined in the function
                            continue

                        if output == "NT":
                            # The variable was not tainted, and now it is
                            outputs[output_index][1] = control_structure_status
                            result[self.get_result_index_by_var_name(result, var)][1]\
                                .instruction = control_structure[0]
                        elif (output == "T" and control_structure_status == "MT"):
                            # The variable was tainted, but now also contains the value "NT"
                            #  "T" + "NT" -> "MT"
                            outputs[output_index][1] = control_structure_status
                            result[self.get_result_index_by_var_name(result, var)][1]\
                                .instruction = control_structure[0]

                        output_index += 1

            last_input_dict = None

            if len(input_dict) != 0:
                last_input_dict = input_dict[list(input_dict)[-1]]

            # [instruction index, current result, new output values, current result, succ]
            # If we visit the same values again, it means we have reached a loop
            visiting = [whole_instructions.index(whole_instruction),
                        last_input_dict, outputs,
                        list(map(lambda x: x[0], result)), None]

            # Get succ whole instructions from current whole instruction
            succs = self.get_succs_from_whole_instruction(whole_instruction, whole_instructions,
                                                          instructions, real_instructions)

            # Sort reversely because the instructions are appended in the front of the worklist
            succs.sort(reverse=True, key=whole_instructions.index)

            for succ_instruction in succs:
                visiting[-1] = id(succ_instruction)
                abort = False

                if succ_instruction[0] not in real_instructions:
                    eprint("Warning: the CFG has taken to a instruction of other"
                           " function and 'kildall' function has been designed to"
                           " have all the instructions in the same function.")
                    continue

                if not is_key_in_dict(input_dict, id(succ_instruction)):
                    last_input_dict_id = None

                    if len(input_dict) != 0:
                        # If there is next instruction but we are in a function
                        #  without parameters nor varaibles declaration, we cannot
                        #  initialize input_dict because we do not have any
                        #  instruction as reference
                        last_input_dict_id = list(input_dict)[-1]

                        instruction_reference =\
                            pycutil.get_full_instruction_from_id(whole_instructions,
                                                                 last_input_dict_id)

                        self.initialize_input_dict(input_dict, variables_decl,
                                                   function_name,
                                                   tainted_variables_names, result,
                                                   succ_instruction,
                                                   instruction_reference)
                    else:
                        # Cannot continue, so avoid next iterations
                        abort = True

                if abort:
                    continue

                input_value = input_dict[id(succ_instruction)]
                append_succ = False

                for var, output in outputs:
                    if not is_key_in_dict(input_value, var):
                        # global variable -> initialize
                        input_dict[id(succ_instruction)][var] = "UNK"

                        # Initialize global variable in result
                        if self.get_result_index_by_var_name(result, var) is None:
                            # var is not in result, so append it
                            gv_source = Source(var, "variable", function_name)
                            gv_taint = Taint(gv_source, None, None, "UNK")

                            result.append((var, gv_taint))

                    taint_status = input_value[var]

                    if output != taint_status:
                        if taint_status == "UNK":
                            # New taint status will be output, which is "T" or "NT"
                            input_dict[id(succ_instruction)][var] = output
                            append_succ = True
                        #elif taint_status != "MT":
                        else:
                            # New taint status will be "MT" because output is "T" or "NT" and
                            #  taint_status the other, so we have the set {"T", "NT"} = "MT"
                            #input_dict[id(succ_instruction)][var] = "MT"
                            input_dict[id(succ_instruction)][var] = output
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
                        succ_control_structure = None

                        # Look for the If structure which contains the EndOfIfElse element
                        for control_structure in temporal_taints_of_control_structures:
                            if isinstance(control_structure[0][0], ast.If):
                                if_instructions = pycutil.get_instruction_path(control_structure[0][0])

                                if succ_instruction[0] in if_instructions:
                                    # Found
                                    succ_control_structure = control_structure
                                    break

                        # Check if the control flow structure has been found
                        if succ_control_structure is None:
                            # It has not been found, so the default behaviour is
                            #  append at end
                            worklist.append(succ_instruction)
                        else:
                            # It has been found
                            inserted = False

                            # Look for the first element of the worklist which does
                            #  not belong to the If statement
                            for wl_index_enum, wl in enumerate(worklist):
                                wl_index = whole_instructions.index(wl)

                                # Check if the current element of the worklist does not
                                #  belong to the control flow structure
                                if not succ_control_structure[3] <= wl_index <\
                                    succ_control_structure[4]:
                                    # It does not belong, so we append the element of
                                    #  the control flow statement in that position
                                    worklist.insert(wl_index_enum, succ_instruction)
                                    inserted = True
                                    break

                            if not inserted:
                                # Default behaviour: append at end
                                worklist.append(succ_instruction)
                    else:
                        worklist.insert(0, succ_instruction)

                    # Append this current and concrete result as visited
                    visited.append(deepcopy(visiting))

        # Get only those Taint instantes which are tainted (T and MT status)
        result = list(filter(lambda x: x[1].status in ["T", "MT"], result))

        function_parameters_name = list(map(lambda x: x.name, function_parameters))

        # Check if there are results without instruction
        for var, taint in result:
            if taint.instruction is None:
                # There are results without instruction
                if ((taint.decl is not None and taint.decl in function_parameters) or
                        (var in function_parameters_name)):
                    # The result is a variable from the function arguments
                    parameter_index = None

                    # Get the index of the parameter
                    if taint.decl is not None:
                        parameter_index = function_parameters.index(taint.decl)
                    else:
                        parameter_index = function_parameters_name.index(var)

                    # Get the parameter and the whole instruction of it
                    parameter = function_parameters[parameter_index]
                    parameter_whole_instruction =\
                        pycutil.get_full_instruction(parameter, real_instructions)

                    # Set, if possible, the declaration as the instruction
                    if len(parameter_whole_instruction) != 0:
                        taint.instruction = parameter_whole_instruction[0]
                else:
                    # Set the tainted instruction to pointing the declaration
                    taint.instruction = taint.decl

        return result

    def check_sources(self, instruction, input_dict, outputs, function_name):
        """It checks if the current instruction is a *Source* and if is
        dangerous.

        The expected type of instructions are function calls, variable
        assignments and variable declarations.

        Arguments:
            instruction (pycparser.c_ast.Node): instruction which is going
                to be analyzed if is or is not a *Source*.
            input_dict (dict): dict of dicts of *str* which represents the tainted
                variables of the current analysis.
            outputs (list): list of tuple of format (str, str) which contains
                the output values for the found variables for all the processed
                whole instructions. This argument will mutate.
            function_name (str): name of the current function being analyzed.

        Raises:
            BOAModuleException: if *instruction* is not an instance of the expected
                ones. If any value of *Source* has not an expected value.
        """
        if not isinstance(instruction, (ast.FuncCall, ast.Assignment, ast.Decl)):
            raise BOAModuleException("'instruction' was expected to be "
                                     "'pycparser.c_ast.FuncCall', "
                                     "'pycparser.c_ast.Assignment'"
                                     " or 'pycparser.c_ast.Decl', "
                                     f"but actual is '{get_just_type(instruction)}'",
                                     self)

        sources = self.get_sources(None)
        last_input_dict = None

        if len(input_dict) != 0:
            last_input_dict = input_dict[list(input_dict)[-1]]

        if isinstance(instruction, ast.FuncCall):
            # Function information
            name = pycutil.get_name(instruction)
            arguments = pycutil.get_func_call_parameters_name(instruction, False)

            # Filter sources
            sources = list(filter(lambda x: x.type == "function" and x.name == name and
                                  x.function_name_container in [function_name, None] and
                                  x.affected_argument_position != 0,
                                  sources))

            for source in sources:
                how = source.how
                affected = source.affected_argument_position
                if_tainted = source.tainted_argument_position

                arg_tainted = "NT"

                if how in Source.allowed_how:
                    if how == "argument":
                        if affected is None:
                            raise BOAModuleException("'Source' defined with 'how="
                                                     "argument', but 'affected' attr"
                                                     " is not defined. Fix your rules"
                                                     " file in order to continue", self)

                        # Check if "affected" is a position of an argument
                        if not 0 <= affected - 1 < len(arguments):
                            continue

                        arg_tainted = "T"
                    elif how == "targ":
                        if affected is None:
                            raise BOAModuleException("'Source' defined with 'how="
                                                     "targ', but 'affected' attr"
                                                     " is not defined. Fix your rules"
                                                     " file in order to continue", self)
                        if if_tainted is None:
                            raise BOAModuleException("'Source' defined with 'how="
                                                     "targ', but 'if_tainted' attr"
                                                     " is not defined. Fix your rules"
                                                     " file in order to continue", self)
                        if last_input_dict is None:
                            # There is not input_dict (i.e. function without arguments
                            #  nor defined sources in rules nor variables declarations)
                            continue

                        # Check if "affected" and "if_tainted" are positions
                        #  of arguments
                        if (not 0 <= affected - 1 < len(arguments) or
                                not 0 <= if_tainted - 1 < len(arguments)):
                            continue

                        target_args = arguments[if_tainted - 1]
                        arg_tainted = "NT"

                        for target_arg in target_args:
                            if (is_key_in_dict(last_input_dict, target_arg) and
                                    last_input_dict[target_arg] in ["T", "MT"]):
                                # The argument which affects "affected" is tainted

                                if arg_tainted == "NT":
                                    arg_tainted = last_input_dict[target_arg]
                                elif (arg_tainted == "MT" and
                                      last_input_dict[target_arg] == "T"):
                                    # "T" has more priority than "MT" in this case
                                    arg_tainted = "T"

                        # Check if "if_tainted" is tainted in order to taint
                        #  "affected" as well
                        if arg_tainted == "NT":
                            # "if_tainted" is not tainted, so "affected" will not
                            #  be tainted
                            continue
                    else:
                        raise BOAModuleException("'source.how' has one of the"
                                                 " defined in 'Source.allowed_how',"
                                                 " but is not specified in this"
                                                 " method (fix the module in order"
                                                 " to continue)", self)

                    # Check if there is only 1 variable as argument, because
                    #  it will only affect the variable if is a reference, and
                    #  only can be 1 variable as reference
                    if (len(arguments[affected - 1]) != 1 or
                            not isinstance(arguments[affected - 1][0], str)):
                        continue

                    name = arguments[affected - 1][0]
                    found = False
                    index = 0

                    for var, output in outputs:
                        if var == name:
                            found = True
                            break
                        index += 1

                    # Check if the variable has been defined right now
                    #  (usual case when declaring and initializating)
                    if found:
                        # The variable has been declarated right now
                        taint_value = outputs[index][1]

                        # Only if the variable is not tainted, we taint the
                        #  variable
                        if taint_value == "NT":
                            outputs[index][1] = arg_tainted
                    else:
                        # Not found, so append the taint
                        outputs.append([name, arg_tainted])
        else:
            # Assignment or declaration

            # Filter sources
            sources = list(filter(lambda x: x.type == "function" and
                                  x.function_name_container in [function_name, None] and
                                  x.affected_argument_position == 0,
                                  sources))

            if len(sources) == 0:
                return

            name = None

            if isinstance(instruction, ast.Assignment):
                # Try to find the root of the name
                try:
                    name = whole_instruction[0].lvalue.name
                except:
                    try:
                        name = whole_instruction[0].lvalue.exprs[0]
                    except:
                        try:
                            name = whole_instruction[0].lvalue.expr
                        except:
                            return
            else:
                # Try to find the root of the name
                try:
                    name = whole_instruction[0].name
                except:
                    try:
                        name = whole_instruction[0].exprs[0]
                    except:
                        try:
                            name = whole_instruction[0].expr
                        except:
                            return

            while not isinstance(name, str):
                name = name.name

            init = None

            if isinstance(instruction, ast.Assignment):
                init = instruction.rvalue
            else:
                init = instruction.init    # Initialization of the declaration

            if init is not None:
                # There are instructions to analyze. If there are not, we are done

                instructions = pycutil.get_instruction_path(init)
                func_calls = pycutil.get_instructions_of_instance(ast.FuncCall,
                                                                  instructions)
                func_call_names = list(map(pycutil.get_name, func_calls))
                func_call_arguments = list(map(lambda x: pycutil\
                                               .get_func_call_parameters_name(x, False),
                                               func_calls))

                # Get only those Sources which are being used in the declaration
                #  or assignment
                sources = list(filter(lambda x: x.name in func_call_names, sources))

                for source in sources:
                    how = source.how
                    affected = source.affected_argument_position    # 0
                    if_tainted = source.tainted_argument_position

                    if how in Source.allowed_how:
                        if how == "argument":
                            pass
                        elif how == "targ":
                            # Check if "affected" and "if_tainted" are positions
                            #  of arguments
                            if if_tainted is None:
                                raise BOAModuleException("'Source' defined with 'how="
                                                         "targ', but 'if_tainted' attr"
                                                         " is not defined. Fix your rules"
                                                         " file in order to continue", self)
                            if not 0 <= if_tainted - 1 < len(arguments):
                                continue
                            if last_input_dict is None:
                                # There is not input_dict (i.e. function without arguments
                                #  nor defined sources in rules nor variables declarations)
                                continue

                            index = func_call_names.index(source.name)

                            target_args = func_call_arguments[index][if_tainted - 1]
                            arg_tainted = "NT"

                            for target_arg in target_args:
                                if (is_key_in_dict(last_input_dict, target_arg) and
                                        last_input_dict[target_arg] in ["T", "MT"]):
                                    # The argument which affects "affected" is tainted

                                    if arg_tainted == "NT":
                                        arg_tainted = last_input_dict[target_arg]
                                    elif (arg_tainted == "MT" and
                                          last_input_dict[target_arg] == "T"):
                                        # "T" has more priority than "MT" in this case
                                        arg_tainted = "T"

                            # Check if "if_tainted" is tainted in order to taint
                            #  "affected" as well
                            if arg_tainted == "NT":
                                # "if_tainted" is not tainted, so "affected" will not
                                #  be tainted
                                continue
                        else:
                            raise BOAModuleException("'source.how' has one of the"
                                                     " defined in 'Source.allowed_how',"
                                                     " but is not specified in this"
                                                     " method (fix the module in order"
                                                     " to continue)", self)

                        # Check if the value has been appended to outputs right now
                        found = False
                        index = 0

                        for var, output in outputs:
                            if var == name:
                                found = True
                                break
                            index += 1

                        # Check if the variable has been defined right now
                        #  (usual case when declaring and initializating)
                        if found:
                            # The variable has been declarated right now
                            taint_value = outputs[index][1]

                            # Only if the variable is not tainted, we taint the
                            #  variable
                            if taint_value == "NT":
                                outputs[index][1] = "T"
                        else:
                            # Not found, so append the taint
                            outputs.append([name, "T"])

    def check_sinks(self, func_call, result, function_name):
        """It checks if the known sinks have been reached by a tainted variable
        and, if so, a found threat will be created.

        Only direct arguments are checked, so those arguments in a function call
        which are other function calls are not processed. The reason is to avoid
        complexity because we do not know if those functions with concrete
        information about tainting is dangerous or not, and if we analyze that
        function recursively, it might be recursively to the same function which
        we are analyzing -> is difficult.

        Arguments:
            func_call (pycparser.c_ast.FuncCall): FuncCall element which will be
                analyzed if is a sink.
            result (dict): dict of dicts which contains information about all the
                variables of the function and their taint information.
            function_name (str): function which we are analyzing.
        """
        name = pycutil.get_name(func_call)
        arguments = pycutil.get_func_call_parameters_name(func_call, False)
        arguments_index = []

        for sink in self.sinks:
            if sink.function_name == name:
                # A taint has been found -> check if dangerous

                # Get the arguments which will be checked
                if sink.dangerous_parameter == 0:
                    # Check all arguments if contain any tainted variable
                    arguments_index = list(range(0, len(arguments)))
                else:
                    # Check dangerous_parameter if contain any tainted
                    #  variable if defined (if the parameter is not found,
                    #  will not raise any exception)
                    # 0 < sink.dangerous_parameter <= len(arguments)
                    if 0 <= sink.dangerous_parameter - 1 < len(arguments):
                        arguments_index = [sink.dangerous_parameter - 1]

                # Check every parameter of the function call
                for arg_index in arguments_index:
                    arg = arguments[arg_index]

                    # Check every variable found in the argument
                    for arg_name in arg:
                        if isinstance(arg_name, str):
                            # Variable found in argument
                            result_index =\
                                self.get_result_index_by_var_name(\
                                    result, arg_name)

                            # Check if the variable exists
                            if result is None:
                                continue

                            taint_status = result[result_index][1].status

                            if taint_status in ["T", "MT"]:
                                # Tainted variable in sink!
                                severity = None

                                if taint_status == "T":
                                    severity = "ALERT"
                                else:
                                    severity = "CRITICAL"

                                current_threat = {
                                    "threat": "sink",
                                    "func_name": name,
                                    "container_func_name": function_name,
                                    "affected_parameter": str(arg_index + 1),
                                    "instruction": func_call,
                                    "severity": severity
                                    }

                                if current_threat not in self.threats:
                                    self.threats.append(current_threat)
                        else:
                            # Function calls as arguments found.
                            # Will not be processed!
                            pass

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
            1. pycparser.c_ast.Node: *whole_instruction* reference.
            2. bool: *True* if the statement is tainted.
            3. str: taint status
            4. int: index where the statement starts (from all the whole instructions)
            5. int: index where the statement finishes (from all the whole instructions).
               It does not include the instruction which targets!
            If there are not elements, *None* will be returned
        """
        # The instruction might have a Compound element strictly
        compound_element_identifier = []

        last_input_dict = None

        if len(input_dict) != 0:
            last_input_dict = input_dict[list(input_dict)[-1]]
        else:
            return None

        # Append which type of compound instruction is (debbug purposes)
        compound_element_identifier.append(whole_instruction)
        # Append if the statement is tainted (T or MT in any of the variables used
        #  in the statement (e.g. if (tainted){indirectly tainted}))
        # Retrieve the tainted variables from the last result
        not_tainted_vars_last_result = list(filter(lambda item: item[1] == "NT",
                                                   last_input_dict.items()))
        tainted_vars_last_result = list(filter(lambda item: item[1] in ["T", "MT"],
                                               last_input_dict.items()))

        not_tainted_vars_last_result = list(filter(lambda x: x[0] in ids,
                                                   not_tainted_vars_last_result))
        tainted_vars_last_result = list(filter(lambda x: x[0] in ids,
                                               tainted_vars_last_result))

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
            # Try to find the root of the name
            try:
                name = whole_instruction[0].lvalue.name
            except:
                try:
                    name = whole_instruction[0].lvalue.exprs[0]
                except:
                    try:
                        name = whole_instruction[0].lvalue.expr
                    except:
                        return
        else:
            # Try to find the root of the name
            try:
                name = whole_instruction[0].name
            except:
                try:
                    name = whole_instruction[0].exprs[0]
                except:
                    try:
                        name = whole_instruction[0].expr
                    except:
                        return

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
                    lambda y: input_dict[last_key][y] in ["T", "MT"],
                    input_dict[last_key]))
                current_not_tainted_variables = list(filter(
                    lambda y: input_dict[last_key][y] == "NT",
                    input_dict[last_key]))

                # Append the known tainted variables
                current_tainted_variables += tainted_variables_names

                # Get the tainted variables from the variables of the
                #  initialization
                tainted = list(filter(lambda x: x in ids[ids_valid_index:],
                                      current_tainted_variables))

                # Get the not tainted variables from the variables of the
                #  initialization
                not_tainted = list(filter(lambda x: x in ids[ids_valid_index:],
                                          current_not_tainted_variables))

                tainted_index = 0

                # Only distinct values
                while tainted_index < len(tainted):
                    if tainted.count(tainted[tainted_index]) != 1:
                        tainted.remove(tainted[tainted_index])
                        continue
                    tainted_index += 1

                tainted_index = 0

                # Only distinct values
                while tainted_index < len(not_tainted):
                    if not_tainted.count(not_tainted[tainted_index]) != 1:
                        not_tainted.remove(not_tainted[tainted_index])
                        continue
                    tainted_index += 1


                # Check if there are any tainted variables in the
                #  initialization
                if len(tainted) != 0:
                    taint_value = "NT"

                    for taint in tainted:
                        if taint_value == "NT":
                            # The taint might not be defined in the function (Source
                            #  defined in the rules file), but we know is tainted
                            taint_value = "T"
                        elif (taint_value == "T" and
                              input_dict[last_key][taint] == "MT"):
                            taint_value = "MT"

                    # Check if there are "NT" tainted variables
                    if (taint_value != "MT" and
                            len(not_tainted) != 0):
                        # There are variables that are not tainted and variables
                        #  that are tainted, but not both (i.e. "MT"), so the
                        #  result is both, which is "MT"
                        taint_value = "MT"

                    outputs.append([name, taint_value])

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
            of *name*. If *name* is not in *result*, *None* will be returned
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

                    if name is None:
                        index += 1
                        continue

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

    def get_sources(self, args):
        """It returns the sources.

        Arguments:
            args (list): list of arguments to pass to *Source.isinstance*.

        Returns:
            list: Sources.
        """
        if (args is None or len(args) == 0):
            return self.sources

        return\
        list(filter(lambda source: Source.isinstance(
            source,
            *args),
                    self.sources))
