"""This file contains the class BOAModuleTaintAnalysis.

The goal of this module is achieve a taint analysis execution
with kildall's algorithm.

The CFG is used as dependency because we need it in order to
execute kildall's algorithm.
"""

# Std libs
from copy import deepcopy

# Own libs
from boam_abstract import BOAModuleAbstract
from util import is_key_in_dict, eprint
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
            decl (auxiliary_modules.pycparser_cfg.Instruction): declaration
                of the instruction.
            instruction (auxiliary_modules.pycparser_cfg.Instruction):
                instruction which tainted the *source*.
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
        """
        result = []
        instructions = self.cfg.get_cfg(function_name)

        if instructions is None:
            eprint(f"Warning: function '{function_name}' was not found in the CFG.")
            return result

        real_instructions = pycfg.Instruction.get_instructions(instructions)
        func_param_list = real_instructions[0].decl.type.args
        func_body = real_instructions[0].body
        func_body_instructions = pycutil.get_instruction_path(func_body)

        # Get all the known Sources (initialization), which can be or not declared in the function
        known_tainted =\
            self.get_sources("variable", function_name) + self.get_sources("variable", None)
        variables_decl = []                 # All the found variables in the current function

        # Check if there are function parameters
        if func_param_list is not None:
            # Thare are function parameters
            param_list_instructions = pycutil.get_instruction_path(func_param_list)
            function_parameters =\
                pycutil.get_instructions_of_instance(ast.Decl, param_list_instructions)

            # Store the fuction parameters
            variables_decl.extend(function_parameters)

        function_variables =\
            pycutil.get_instructions_of_instance(ast.Decl, func_body_instructions)

        for function_variable in function_variables:
            function_variable_instructions = pycutil.get_instruction_path(function_variable)
            function_type_decl = pycutil.get_instructions_of_instance(
                ast.TypeDecl,
                function_variable_instructions)
            function_id_type = pycutil.get_instructions_of_instance(
                ast.IdentifierType,
                function_variable_instructions)

            if (len(function_type_decl) == 1 and len(function_id_type) == 1):
                variables_decl.append(function_variable)

        # Initialize all the Taint instances with the variables of the function
        #  (initializes the algorithm)
        tainted_variables_names = list(map(lambda x: x.name, known_tainted))
        input_dict = {}
        worklist = [func_body]

        for variable_decl in variables_decl:
            variable_decl_name = variable_decl.name
            taint_status = "UNK"
            taint_instruction = None

            # Initialize the inputs
            for func_body_instruction in func_body_instructions:
                if not is_key_in_dict(input_dict, func_body_instruction):
                    input_dict[func_body_instruction] = {}

                input_dict[func_body_instruction][variable_decl_name] = taint_status

            if variable_decl_name in tainted_variables_names:
                # The variable is tainted
                taint_status = "T"
                taint_instruction = variable_decl

                # Initial information
                input_dict[func_body_instructions[0]][variable_decl_name] = taint_status

            source = Source(variable_decl_name, "variable", function_name)
            taint = Taint(source, variable_decl, taint_instruction, taint_status)

            result.append(taint)

        # Work with the worklist and the CFG
        while len(worklist) != 0:
            # Take the first instruction
            first_instruction = worklist[0]
            # Take off the first instruction of the worklist
            worklist.remove(worklist[0])

            output = "NT"

            # TODO get the real value of output

            index = real_instructions.index(first_instruction)
            instruction = instructions[index]
            succs = instruction.get_succs()
            succ_real_instructions = pycfg.Instruction.get_instructions(succs)

            for succ_instruction in succ_real_instructions:
                if not is_key_in_dict(input_dict, succ_instruction):
                    eprint("Warning: the CFG has taken to a instruction of other function"
                           " and 'kildall' function has been designed to have all the"
                           " instructions in the same function.")
                    continue

                input_value = input_dict[succ_instruction]
                append_succ = False

                for var in input_value:
                    taint_status = input_value[var]

                    if output != taint_status:
                        if taint_status == "UNK":
                            # New taint status will be output, which is "T" or "NT"
                            input_dict[succ_instruction][var] = output
                            append_succ = True
                        elif taint_status != "MT":
                            # New taint status will be "MT" because output is "T" or "NT" and
                            #  taint_status the other, so we have the set {"T", "NT"} = "MT"
                            input_dict[succ_instruction][var] = "MT"
                            append_succ = True

                if append_succ:
                    # A variable was affected, so we process the dependency
                    worklist.append(succ_instruction)

        # TODO process input_dict in order to obtain the Taint instances for append it
        #  in "result"

        # Get only those Taint instantes which are tainted (T and MT status)
        result = list(filter(lambda x: x.status == "T" or x.status != "MT", result))

        return result

    def get_sources(self, stype=None, function_name_container=None):
        if (stype is None and function_name_container is None):
            return self.sources

        return\
        list(filter(lambda source: Source.isinstance(
            source,
            stype,
            function_name_container),
                    self.sources))
