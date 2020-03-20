"""This file contains the class BOAModuleTaintAnalysis.

The goal of this module is achieve a taint analysis execution
with kildall's algorithm.

The CFG is used as dependency because we need it in order to
execute kildall's algorithm.
"""

# Own libs
from boam_abstract import BOAModuleAbstract
from util import is_key_in_dict
from own_exceptions import BOAModuleException

class TAConstants:
    cfg_dependency = "boam_cfg.BOAModuleControlFlowGraph"
    cfg_dependency_key = "cfg"

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
        # TODO load sources and sinks from rules file
        self.sources = []
        self.sinks = []
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

class Source:
    """It represents a Source, which in the Taint Analysis terminology
    means something that allows the user to have control over the information
    which is inserted in the program. A Source may be a function, a variable,
    a network package or anything else which the user might alter. Usually,
    the Sources are function calls (e.g. gets()) and a few set of dangerous
    variables (i.e. argc, argv).
    """

    allowed_types = ["function", "variable"]

    def __init__(self, name, stype):
        """It initializes a Source.

        Arguments:
            name (str): name of the object reference which contains or allows
                the user to insert data.
            stype (str): type of the object which is the Source (e.g. "function",
                "variable", ...). The possible values of *stype* are in the class
                list *allowed_types*.

        Raises:
            BOAModuleException: if *stype* is not a value of *Source.allowed_types*.
        """
        self.name = name
        self.type = stype

        if self.type not in Source.allowed_types:
            raise BOAModuleException("the Source type can only contain a value of the"
                                     f" next: '{str(Source.allowed_types)[1:-1]}'", self)

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
