"""This file has the only purpose of contains a bundle
of functions separately of the main file. It is cleaner
and more readable.
"""

# Std libs
import os
import logging
from collections import OrderedDict

# Own libs
from args_manager import ArgsManager
import exceptions
from exceptions import BOAFlowException
import utils
from constants import Meta, Error, Other
from modules_importer import ModulesImporter
from lifecycles.boalc_manager import BOALifeCycleManager
from rules_manager import RulesManager

def load_modules(user_modules, analysis):
    """It handles the modules loading through ModulesImporter class.

    Arguments:
        user_modules (list): user modules (i.e. non-mandatory modules)
            to be loaded.
        analysis (str): information about which analysis we are running.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        list: list containing:
            * int: status code\n
            * ModulesImporter: ModulesImporter instance
    """

    if not isinstance(user_modules, list):
        user_modules = [user_modules]

    mandatory_modules = [Other.abstract_module_name]
    modules = mandatory_modules + user_modules

    # Through mod_loader we can get modules, but it is not necessary (sys.modules)
    mod_loader = None

    try:
        mod_loader = ModulesImporter(modules)
    except exceptions.BOAModulesImporterException as e:
        raise BOAFlowException("could not instantiate ModulesImporter",
                               Error.error_module_importer_could_not_be_instantiated) from e

    module_subdir = None

    if analysis == "static":
        module_subdir = Other.modules_static_analysis_subdir
    elif analysis == "dynamic":
        module_subdir = Other.modules_dynamic_analysis_subdir
    else:
        logging.warning("unexpected analysis attribute value: '%s'", analysis)

    mod_loader.load(module_subdir=module_subdir)

    # Check if mandatory or user modules failed
    mandatory_module_failed = False
    user_module_failed = False
    rtn_code = Meta.ok_code

    # Checking mandatory modules
    for mandatory_module in mandatory_modules:
        if not mod_loader.is_module_loaded(mandatory_module):
            mandatory_module_failed = True
            break

    # Checking user modules
    for user_module in user_modules:
        if not mod_loader.is_module_loaded(user_module):
            user_module_failed = True
            break

    if (mandatory_module_failed and user_module_failed):
        rtn_code = Error.error_module_some_mandatory_and_user_failed
    elif mandatory_module_failed:
        rtn_code = Error.error_module_some_mandatory_failed
    elif user_module_failed:
        rtn_code = Error.error_module_some_user_failed

    return [rtn_code, mod_loader]

def load_instance(module_loader, module_name, class_name, module_args,
                  module_dependencies):
    """It handles the instances loading throught a ModulesImporter instance.
    It loads one instance from a class.

    Arguments:
        module_loader (ModulesImporter): instance which will load modules.
        module_name (str): module name.
        class_name (str): class name.
        module_args (dict): args to use to initialize the instance.
        module_dependencies (dict): module dependencies.

    Returns:
        list: list containing:
            * int: status code\n
            * loaded instance

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Note:
        All the modules has to inherit from *constants.Meta.
        abstract_module_class_name*.
    """
    instance = module_loader.get_instance(module_name, class_name)
    abstract_instance = module_loader.get_instance(Other.abstract_module_name,
                                                   Other.abstract_module_class_name)

    if instance is None:
        return [Error.error_module_cannot_load_instance, None]
    if abstract_instance is None:
        return [Error.error_module_cannot_load_instance, None]
    if (not issubclass(instance, abstract_instance) or
            instance is abstract_instance):
        logging.error("instance '%s.%s' has not the expected type (does it inherit from "
                      "'%s.%s'?)", module_name, class_name, Other.abstract_module_name,
                      Other.abstract_module_class_name)
        return [Error.error_module_not_expected_type, None]

    if utils.is_key_in_dict(module_args, Other.other_argument_name_for_dependencies_in_modules):
        raise BOAFlowException("argument"
                               f" '{Other.other_argument_name_for_dependencies_in_modules}'"
                               " must not be defined because it is used for intenal purposes"
                               f" ({module_name}.{class_name})",
                               Error.error_other_reserved_keyword_being_used)

    try:
        # Load dependencies
        module_args[Other.other_argument_name_for_dependencies_in_modules] = module_dependencies

        # Initilize instance
        instance = instance(module_args)

        logging.info("instance '%s.%s' initialized", module_name, class_name)
    except Exception as e:
        logging.error("could not load an instance of '%s.%s' (bad implementation of '%s."
                      "%s' in '%s.%s'?): %s", module_name, class_name, Other.abstract_module_name,
                      Other.abstract_module_class_name, module_name, class_name, str(e))

    return [Meta.ok_code, instance]

def get_boapm_instance(module_name, class_name, filename=None):
    """It attempts to load a BOAPM module and get an
    instance of it.

    It checks that the loaded BOAPM class is subclass of
    the BOAPM abstract class.

    Arguments:
        module_name (str): BOAPM module name.
        class_name (str): BOAPM class name.

    Raises:
        BOAFlowException: if could not load the abstract
            instance or the file does not exist.

    Returns:
        loaded instance
    """
    return get_boa_runner_instance(module_name, class_name, "parser", Other.runners_static_analysis_directory,
                                   Other.parser_modules_directory, Other.abstract_parser_module_name,
                                   Other.abstract_parser_module_class_name, Other.abstract_parser_module_filename,
                                   filename=filename)

def get_boaim_instance(module_name, class_name, filename=None):
    """It attempts to load a BOAIM module and get an
    instance of it.

    It checks that the loaded BOAIM class is subclass of
    the BOAIM abstract class.

    Arguments:
        module_name (str): BOAIM module name.
        class_name (str): BOAIM class name.

    Raises:
        BOAFlowException: if could not load the abstract
            instance or the file does not exist.

    Returns:
        loaded instance
    """
    return get_boa_runner_instance(module_name, class_name, "input", Other.runners_dynamic_analysis_directory,
                                   Other.input_modules_directory, Other.abstract_input_module_name,
                                   Other.abstract_input_module_class_name, Other.abstract_input_module_filename,
                                   filename=filename)

def get_boafm_instance(module_name, class_name, filename=None):
    """It attempts to load a BOAFM module and get an
    instance of it.

    It checks that the loaded BOAFM class is subclass of
    the BOAFM abstract class.

    Arguments:
        module_name (str): BOAFM module name.
        class_name (str): BOAFM class name.

    Raises:
        BOAFlowException: if could not load the abstract
            instance or the file does not exist.

    Returns:
        loaded instance
    """
    return get_boa_runner_instance(module_name, class_name, "fail", Other.runners_dynamic_analysis_directory,
                                   Other.fail_modules_directory, Other.abstract_fail_module_name,
                                   Other.abstract_fail_module_class_name, Other.abstract_fail_module_filename,
                                   filename=filename)

def get_boa_runner_instance(module_name, class_name, runner_module, analysis_dir, modules_dir, abstract_mod_name,
                            abstract_class_name, abstract_mod_filename, filename=None):
    """It attempts to load a runner BOA module and get an
    instance of it.

    It checks that the loaded runner BOA class is subclass of
    the BOA abstract class.

    Arguments:
        module_name (str): BOA runner module name.
        class_name (str): BOA runner class name.

    Raises:
        BOAFlowException: if could not load the abstract
            instance or the file does not exist.

    Returns:
        loaded instance
    """
    if filename is None:
        filename = f"{module_name}.py"

    file_path = f'{utils.get_current_path(__file__)}/{analysis_dir}/{modules_dir}'
    abstract_instance = ModulesImporter.load_and_get_instance(abstract_mod_name,
                                                              f'{file_path}/{abstract_mod_filename}',
                                                              abstract_class_name)
    file_path = f'{file_path}/{filename}'

    if not abstract_instance:
        raise BOAFlowException("could not load and get an instance of "
                               f"'{abstract_mod_name}.{abstract_class_name}'",
                               Error.error_runner_module_abstract_not_loaded)
    if not utils.file_exists(file_path):
        raise BOAFlowException(f"file '{file_path}' not found",
                               Error.error_runner_module_not_found)

    instance = ModulesImporter.load_and_get_instance(
        module_name,
        file_path,
        class_name)

    if not instance:
        raise BOAFlowException(f"could not load the {runner_module} module '{module_name}.{class_name}'",
                               Error.error_runner_module_not_loaded)

    if (not issubclass(instance, abstract_instance) or
            instance is abstract_instance):
        raise BOAFlowException(f"instance '{module_name}.{class_name}' has not the expected"
                               f" type (does it inherit from '{abstract_mod_name}."
                               f"{abstract_class_name}'?)",
                               Error.error_runner_module_abstract_not_expected_type)

    return instance

def remove_not_loaded_modules(mod_loader, modules, classes, mods_args,
                              mods_dependencies, reports, lifecycles):
    """It handles the non-loaded modules errors (it is optional to continue if
    some modules did not be loaded properly) through a ModulesImporter instance.

    Arguments:
        mod_loader (ModulesImporter): instance which will be used to get
            the non-loaded modules.
        modules (list): list which contains the module names that were
            attempted to loading (its index is related with *classes*).
        classes (list): list which contains the class names that were
            attempted to loading (its index is related with *modules*).
        mods_args (dict): dict which contains the arguments of all
            the modules.
        mods_dependencies (dict): dict which contains the dependencies
            of all the modules.
        reports (list): list which contains the reports of all the modules.
        lifecycles (list): list which contains the lifecycles of all the
            modules.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.
    """
    not_loaded_modules = mod_loader.get_not_loaded_modules()

    for not_loaded_module in not_loaded_modules:
        try:
            index = modules.index(not_loaded_module)

            removed_module = modules.pop(index)
            removed_class = classes.pop(index)

            mods_args.pop(f"{removed_module}.{removed_class}")

            if utils.is_key_in_dict(mods_dependencies, f"{removed_module}.{removed_class}"):
                mods_dependencies.pop(f"{removed_module}.{removed_class}")

            reports.pop(index)
            lifecycles.pop(index)

            logging.warning("instance '%s.%s' was removed", removed_module, removed_class)
        except Exception as e:
            raise BOAFlowException("could not remove a module/class/arg/dependency while"
                                   f" trying to remove module '{not_loaded_module}'",
                                   Error.error_module_cannot_remove_not_loaded_module) from e

def manage_rules_file():
    """It handles the rules file (parsing, checking and processing)
    through RulesManager class.

    Arguments:
        analysis (str): information about which analysis we are running.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        RulesManager: RulesManager instance
    """

    rules_manager = RulesManager(ArgsManager.args.rules_file)

    # Open file
    rtn_code = rules_manager.open()

    if rtn_code != Meta.ok_code:
        raise BOAFlowException("could not open the rules file", rtn_code)

    # Read and save relevant information
    rtn_code = rules_manager.read()

    if rtn_code != Meta.ok_code:
        raise BOAFlowException("could not read the rules file", rtn_code)

    rtn_code = rules_manager.close()

    if rtn_code != Meta.ok_code:
        raise BOAFlowException("could not close the rules file", rtn_code)

	# Check rules and process arguments from rules file
    if not rules_manager.check_rules(True):
        raise BOAFlowException("the rules did not pass the checking",
                               Error.error_rules_bad_checking)

    return rules_manager

def manage_lifecycles(instances, reports, lifecycle_args, lifecycles, analysis):
    """It handles the lifecycles of the instances.

    Arguments:
        instances (list): module instances to be executed.
        reports (list): reports to be used by the *instances*.
        lifecycle_args (dict): args to be used by the lifecycle.
        lifecycles (list): list of names in format
            "module_name.class_name" to be used.
        analysis (str): information about which analysis we are running.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        BOALifeCycleManager: BOALifeCycleManager instance
    """
    lifecycle_manager = None
    lifecycle_instances = []
    lifecycle_path = f"{utils.get_current_path(__file__)}/"\
                     f"{Other.lifecycle_modules_directory}/"\
                     f"{Other.lifecycle_abstract_module_filename}"
    lifecycle_abstract_instance = ModulesImporter.load_and_get_instance(
        Other.lifecycle_abstract_module_name,
        lifecycle_path,
        Other.lifecycle_abstract_module_class_name)

    if not lifecycle_abstract_instance:
        raise BOAFlowException("could not get the lifecycle abstract instance",
                               Error.error_lifecycle_could_not_load_abstract_instance)

    # Get lifecycle instances
    for lifecycle in lifecycles:
        lifecycle_splitted = lifecycle.split('.')
        lifecycle_module_name = lifecycle_splitted[0]
        lifecycle_class_name = lifecycle_splitted[1]
        lifecycle_path = f"{utils.get_current_path(__file__)}/"\
                         f"{Other.lifecycle_modules_directory}/"\
                         f"{lifecycle_module_name}.py"

        # Check if the lifecycle file exists
        if not utils.file_exists(lifecycle_path):
            raise BOAFlowException("could not found the lifecycle "
                                   f"module '{lifecycle_module_name}'",
                                   Error.error_lifecycle_module_not_found)

        lifecycle_instance = ModulesImporter.load_and_get_instance(lifecycle_module_name,
                                                                   lifecycle_path,
                                                                   lifecycle_class_name)

        # Check if the lifecycle instance could be imported and if it is of the expected type
        if not lifecycle_instance:
            raise BOAFlowException("lifecycle instance has the unexpected"
                                   f" value '{lifecycle_instance}'",
                                   Error.error_lifecycle_could_not_load_instance)
        if (not issubclass(lifecycle_instance, lifecycle_abstract_instance) or
                lifecycle_instance is lifecycle_abstract_instance):
            raise BOAFlowException(f"instance '{lifecycle_module_name}.{lifecycle_class_name}'"
                                   " has not the expected type (does it inherit from "
                                   f"'{Other.lifecycle_abstract_module_name}"
                                   f".{Other.lifecycle_abstract_module_class_name}'?)",
                                   Error.error_lifecycle_not_expected_type)

        lifecycle_instances.append(lifecycle_instance)

    # Manage the lifecycles
    try:
        lifecycle_manager = BOALifeCycleManager(instances, reports, lifecycle_args, lifecycle_instances, analysis)

        rtn_code = lifecycle_manager.handle_lifecycle()
    except exceptions.BOALCAnalysisException as e:
        raise BOAFlowException(f"lifecycle wrong analysis: {str(e)}", Error.error_lifecycle_wrong_analysis) from e
    except exceptions.BOALCException as e:
        raise BOAFlowException("lifecycle exception", Error.error_lifecycle_exception) from e
    except exceptions.BOAReportException as e:
        raise BOAFlowException("report exception", Error.error_report_unknown) from e
    except Exception as e:
        raise BOAFlowException("unknown reason", Error.error_lifecycle_exception) from e

    if rtn_code != Meta.ok_code:
        raise BOAFlowException("lifecycle could finish, but not with a correct status",
                               rtn_code)

    return lifecycle_manager

def handle_boapm(boapm_instance, parser_rules):
    """It handles the BOAParserModule instance.

    It will call the base methods and the callbacks defined in the rules file.

    Arguments:
        boapm_instance (BOAParserModuleAbstract): instance that inherits from
            BOAParserModuleAbstract.
        parser_rules (OrderedDict): rules which contains the necessary information
            for the parser module in order to be initialized.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        dict: callback results (boa_rules.runners.parser.callback.method) of *boapm_instance*.
    """
    # Initialize the instance and other necessary information
    boapm_instance = boapm_instance(ArgsManager.args.target)
    boapm_instance_name = utils.get_name_from_class_instance(boapm_instance)
    parser_name = parser_rules["name"]
    parser_lang = parser_rules["lang_objective"]
    callbacks = parser_rules["callback"]["method"]
    names = []
    methods = []
    boapm_results = {}

    logging.info("parser which is being loaded: %s (language: %s)", parser_name, parser_lang)

    # Call initialization methods defined in
    try:
        boapm_instance.initialize()
        boapm_instance.parse()
    except exceptions.BOAPMInitializationError as e:
        raise BOAFlowException(f"'{boapm_instance_name}.initialize()'",
                               Error.error_runner_module_failed_in_initialization) from e
    except exceptions.BOAPMParseError as e:
        raise BOAFlowException(f"'{boapm_instance_name}.parse()'",
                               Error.error_runner_module_failed_in_parsing) from e
    except Exception as e:
        raise BOAFlowException(f"'{boapm_instance_name}'",
                               Error.error_runner_module_failed_in_execution) from e

    if not isinstance(callbacks, list):
        callbacks = [callbacks]

    for callback in callbacks:
        callback_dict = dict(callback.items())
        name = callback_dict["@name"]
        method = callback_dict["@callback"]

        if (not name or not method):
            logging.warning("attributes 'name' ('%s') and 'callback' ('%s') in"
                            " 'boa_rules.runners.parser.callback.method' cannot be empty: skipping", name, method)
        elif name in names:
            logging.warning("attribute 'name' ('%s') cannot be duplicated in"
                            " 'boa_rules.runners.parser.callback.method': skipping", name)
        else:
            names.append(callback_dict["@name"])
            methods.append(callback_dict["@callback"])

    error = False

    for name, method in zip(names, methods):
        result = utils.invoke_by_name(boapm_instance, method)

        # Checking is made with "is" because we want to check the reference, not the value!
        # Check function "utils.invoke_by_name" in order to understand the following checking
        if result is not Other.other_util_invoke_by_name_error_return:
            boapm_results[name] = result
        else:
            error = True

    if error:
        if len(boapm_results) == 0:
            raise BOAFlowException("parser modules: no callback was executed",
                                   Error.error_runner_module_no_callback_executed)

        raise BOAFlowException("parser modules: some callbacks were not executed",
                               Error.error_runner_module_some_callback_not_executed)

    return boapm_results

def handle_dynamic_analysis_runner(module_instance, module_args):
    """ It handles the runner instances from dynamic analysis.

    Arguments:
        module_instance: runner instance.
        module_args (dict): args to initilize the instance.

    Raises:
        BOAFlowException: the initialization of the runner instance failed.

    Returns:
        dict: runner instance.
    """
    # Initialize the instance and other necessary information
    instance = module_instance(module_args)
    instance_name = utils.get_name_from_class_instance(instance)
    results = {"instance": instance}

    # Call initialization methods defined in
    try:
        instance.initialize()
    except exceptions.BOARunnerModuleError as e:
        raise BOAFlowException(f"runner module '{instance_name}' failed when was"
                               " initialized") from e
    except Exception as e:
        raise BOAFlowException(f"'{instance_name}'",
                               Error.error_runner_module_failed_in_execution) from e

    return results


def get_env_vars(rules):
    """It gets the environment variables from the rules file.

    Arguments:
        rules (OrderedDict): rules

    Returns:
        list: environment variable names
    """
    env_vars = rules["env_vars"]

    if not env_vars:
        # No environment variable was defined
        return []

    env_vars = rules["env_vars"]["env_var"]

    if not env_vars:
        return []
    if isinstance(env_vars, str):
        return [env_vars]
    if not isinstance(env_vars, list):
        logging.error("expected type in environment variables is 'list',"
                      " but actually is '%s'", type(env_vars))

    return env_vars

def handle_env_vars(env_vars_rules):
    """It handles the environment variables from the rules file.
    It checks if the envvars are defined, raise exception if the non-defined
    envvars are mandatory and sets the values if the defined envvars have
    provided one definition.

    Arguments:
        env_vars_rules (OrderedDict): rules

    Raises:
        BOAEnvvarException: unexpected type of envvar from *rules* or mandatory
            envvar not defined and without assigned value.
    """
    if not env_vars_rules:
        # No environment variable was defined
        return

    env_vars = env_vars_rules["env_var"]
    optional_env_vars = []
    mandatory_env_vars = []

    if not isinstance(env_vars, list):
        # Fix if there was only one defined envvar
        env_vars = [env_vars]

    for env_var in env_vars:
        if isinstance(env_var, OrderedDict):
            env_var_name = env_var["#text"]

            if "@mandatory" in env_var:
                value = env_var["@mandatory"].lower()

                if value == "true":
                    mandatory_env_vars.append(env_var_name)
                elif value == "false":
                    optional_env_vars.append(env_var_name)
                else:
                    logging.warning(f"unexpected 'mandatory' value for envvar '{env_var_name}': skipping")
                    continue
            if "@value" in env_var:
                value = env_var["@value"]

                if env_var_name in os.environ:
                    logging.warning("envvar '%s' is already defined in the environment and has been overwritten")

                os.environ[env_var_name] = value
        elif isinstance(env_var, str):
            optional_env_vars.append(env_var)
        else:
            raise exceptions.BOAEnvvarException("unexpected type from rules file of the"
                                                f" environment variables (type: {str(type(env_var))})")

    utils.get_environment_varibles(optional_env_vars, verbose_on_failure=True,
                                   failure_message="optional envvar is not defined")

    not_defined_mandatory_envvars = []

    # Check which mandatory envvars are not defined
    for env_var in mandatory_env_vars:
        if env_var not in os.environ:
            not_defined_mandatory_envvars.append(env_var)

    if len(not_defined_mandatory_envvars) != 0:
        str_env_vars = "', '".join(not_defined_mandatory_envvars)
        raise exceptions.BOAEnvvarException(f"the following mandatory envvars are not defined: '{str_env_vars}'")

def get_boar_instance(module_name, class_name, filename=None):
    """It attempts to load a BOAR module and get an
    instance of it.

    It checks that the loaded BOAR class is subclass of
    the BOAR abstract class.

    Arguments:
        module_name (str): BOAR module name.
        class_name (str): BOAPR class name.

    Raises:
        BOAFlowException: if could not load the abstract
            instance or the file does not exist.

    Returns:
        loaded instance
    """
    if filename is None:
        filename = f"{module_name}.py"

    file_path = f'{utils.get_current_path(__file__)}/{Other.report_modules_directory}'
    abstract_instance = ModulesImporter.load_and_get_instance(Other.report_abstract_module_name,
                                                              f'{file_path}/{Other.report_abstract_module_filename}',
                                                              Other.report_abstract_module_class_name)
    file_path = f'{file_path}/{filename}'

    if not abstract_instance:
        raise BOAFlowException("could not load and get an instance of "
                               f"'{Other.report_abstract_module_name}.{Other.report_abstract_module_class_name}'",
                               Error.error_report_module_abstract_not_loaded)
    if not utils.file_exists(file_path):
        raise BOAFlowException(f"file '{file_path}' not found",
                               Error.error_report_module_not_found)

    instance = ModulesImporter.load_and_get_instance(
        module_name,
        file_path,
        class_name)

    if not instance:
        raise BOAFlowException(f"could not load the report module '{module_name}.{class_name}'",
                               Error.error_report_module_not_found)

    if (not issubclass(instance, abstract_instance) or
            instance is abstract_instance):
        raise BOAFlowException(f"instance '{module_name}.{class_name}' has not the expected"
                               f" type (does it inherit from '{Other.abstract_parser_module_name}."
                               f"{Other.abstract_parser_module_class_name}'?)",
                               Error.error_report_module_abstract_not_expected_type)

    return instance

def handle_boar(rules_manager, severity_enum_instance):
    """It handles the reports instances which will be
    used as parameter for the modules instances.

    Arguments:
        rules_manager (RulesManager): rules manager instance
            which will allow us to get the arguments of the
            report instance.
        severity_enum_instance (SeverityBase): severity enum
            instance which will be used for the report
            instance which will be returned.

    Returns:
        BOAReportAbstract: report instance
    """
    report_instance = None
    report_default_handler = Other.other_report_default_handler.split(".")

    if (not report_default_handler or len(report_default_handler) != 2):
        raise exceptions.BOAUnexpectedException("the default report handler has not the expected value:"
                                                f" '{Other.other_report_default_handler}'")

    report_module_name = report_default_handler[0]
    report_class_name = report_default_handler[1]
    report_args = rules_manager.get_report_args()
    report_rules = rules_manager.get_rules("boa_rules.report")

    if utils.is_key_in_dict(report_rules, "module_name"):
        report_module_name = report_rules["module_name"]
    if utils.is_key_in_dict(report_rules, "class_name"):
        report_class_name = report_rules["class_name"]

    # Get instance
    report_instance = get_boar_instance(report_module_name, report_class_name)

    # Initialize instance
    report_instance = report_instance(severity_enum_instance, report_args)

    return report_instance


def process_security_modules(rules_manager):
    """It process the necessary information to work with the
    security modules.

    Arguments:
        rules_manager (RulesManager): rules manager to get the
            arguments.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        list: list containing:
            * list: modules (str)\n
            * list: classes (str)\n
            * dict: modules arguments\n
            * dict: modules dependencies\n
            * list: reports instances\n
            * list: lifecycles handler (str)
    """
    modules = []
    classes = []
    mods_args = {}	# {"mod.class": {"arg1": "value2", "arg2": ["value2", "value3"]}}
    mods_dependencies = {}  # {"mod.class": {"mod_dep1.class_dep1": {"name1": "value1",
                            #   "name2": "value2"}, "mod_dep2.class_dep2": {"a": "b"}}}
    reports = []
    lifecycles = []

    args = rules_manager.get_args()
    dependencies = rules_manager.get_dependencies()
    rmodules = rules_manager.get_rules("boa_rules.modules.module", True)

    for m in rmodules:
        module_name = m['module_name']
        class_name = m['class_name']
        severity_enum_formatted = m['severity_enum']
        severity_enum_splitted = severity_enum_formatted.split('.')
        severity_enum_module_name = severity_enum_splitted[0]
        severity_enum_class_name = severity_enum_splitted[1]
        severity_enum_name = f"{severity_enum_module_name}.{severity_enum_class_name}"
        lifecycle = m['lifecycle_handler']

        modules.append(module_name)
        classes.append(class_name)
        lifecycles.append(lifecycle)

        if not utils.is_key_in_dict(args, f"{module_name}.{class_name}"):
            raise BOAFlowException(f"args for module '{module_name}.{class_name} not found'",
                                   Error.error_rules_args_not_found)

        severity_enum_path = f"{utils.get_current_path(__file__)}/enumerations/severity/{severity_enum_module_name}.py"

        if not utils.file_exists(severity_enum_path):
            raise BOAFlowException("could not found the severity enumeration"
                                   f" module '{severity_enum_module_name}'",
                                   Error.error_report_severity_enum_module_not_found)

        severity_enum_instance = ModulesImporter.load_and_get_instance(
            severity_enum_module_name,
            severity_enum_path,
            severity_enum_class_name)

        if not severity_enum_instance:
            raise BOAFlowException(f"could not load the severity enumeration '{severity_enum_name}'",
                                   Error.error_report_severity_enum_module_not_loaded)

        report = None

        try:
            #report = Report(severity_enum_instance)
            report = handle_boar(rules_manager, severity_enum_instance)
        except exceptions.BOAReportEnumTypeNotExpected as e:
            raise BOAFlowException(f"severity enum type not expected: '{severity_enum_name}'",
                                   Error.error_report_severity_enum_not_expected) from e
        except exceptions.BOAUnexpectedException as e:
            raise BOAFlowException("unexpected exception", Error.error_report_unknown) from e
        except BOAFlowException as e:
            raise e
        except Exception as e:
            raise BOAFlowException("unknown reason", Error.error_report_unknown) from e

        reports.append(report)

        mods_args[f"{module_name}.{class_name}"] = \
             args[f"{module_name}.{class_name}"]

        # Set dependencies if exist (are optional)
        if utils.is_key_in_dict(dependencies, f"{module_name}.{class_name}"):
            mods_dependencies[f"{module_name}.{class_name}"] = \
                 dependencies[f"{module_name}.{class_name}"]

    if (len(modules) != len(classes) or len(modules) != len(mods_args)):
        raise BOAFlowException(f"modules length ({len(modules)}), classes length ({len(classes)})"
                               f" and arguments length ({len(mods_args)}) are not equal",
                               Error.error_rules_modules_classes_args_neq_length)

    return [modules, classes, mods_args, mods_dependencies, reports, lifecycles]

def load_instances(modules, classes, mods_args, mod_loader, rules_manager):
    """It loads the instances with their arguments.

    Arguments:
        modules (list): list of modules names.
        classes (list): list of classes names.
        mods_args (dict): args to give to the instances. Each one will
            have access only to its arguments.
        mod_loader (ModulesImporter): instance which will load modules.
        rules_manager (RulesManager): rules manager instance which
            will allow us to get information.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        loaded instances
    """
    instances = []
    instances_dict = {}
    index = 0

    while index < len(modules):
        name_formatted = f"{modules[index]}.{classes[index]}"

        try:
            mod_args = mods_args[name_formatted]
        except KeyError as e:
            raise BOAFlowException(f"could not get '{e}' arguments"
                                   " due to a bad naming reference",
                                   Error.error_rules_bad_naming_references) from e

        # Replace string callback with the real callback
        dependencies = rules_manager.get_dependencies(name_formatted)

        replace_dependencies_callbacks(dependencies, instances_dict)

        # Load instance
        rtn = load_instance(mod_loader, modules[index], classes[index], mod_args, dependencies)
        rtn_code = rtn[0]
        instance = rtn[1]

        if rtn_code != Meta.ok_code:
            raise BOAFlowException(None, rtn_code)

        instances.append(instance)
        instances_dict[name_formatted] = instance

        index += 1

    return instances

def replace_dependencies_callbacks(dependencies, instances_dict):
    """It replaces the callback string of the dependencies
    for the actual callback.

    Example:
        dependencies =
            {'boam_function_match.BOAModuleFunctionMatch': {'arg0': 'clean',
                'arg1': 'finish'}}
        instances_dict =
            {'boam_function_match.BOAModuleFunctionMatch':
                <boam_function_match.BOAModuleFunctionMatch object at 0x7f7bb49a7c50>}

        After invoke *replace_dependencies_callbacks(dependencies, instances_dict)*:

        dependencies =
            {'boam_function_match.BOAModuleFunctionMatch':
                {'arg0': <bound method BOAModuleFunctionMatch.clean of
                    <boam_function_match.BOAModuleFunctionMatch object at 0x7f7bb49a7c50>>,
                    'arg1': <bound method BOAModuleFunctionMatch.finish of
                    <boam_function_match.BOAModuleFunctionMatch object at 0x7f7bb49a7c50>>}}

    Arguments:
        dependencies (dict): dependencies of a concrete module.
        instances_dict (dict): dictionary which contains the
            instances as values and the name of the instances
            as key.
    """
    for dependency, args in dependencies.items():
        for arg, callback in args.items():
            try:
                dependencies[dependency][arg] = \
                    getattr(instances_dict[dependency], callback)
            except AttributeError as e:
                raise BOAFlowException(f"callback '{callback}' does not exist"
                                       f" in dependency '{dependency}'",
                                       Error.error_module_dependency_callback_not_found) from e
            except NameError as e:
                raise BOAFlowException("name error", Error.error_unknown) from e
            except Exception as e:
                raise BOAFlowException("unknown reason", Error.error_unknown) from e

def check_dependencies(modules, classes, mods_dependencies):
    """It checks if the dependencies are correct. Concretely,
    it checks if the dependencies exist, if a module is a dependency
    of itself and if the dependencies graph is cyclic, what is not
    allowed.

    Arguments:
        modules (list): list of modules.
        classes (list): list of classes.
        mods_dependencies (dict): dependencies of the modules.

    Raises:
        BOAFlowException: the dependencies are not ok.

    Returns:
        dict: dependencies graph
    """
    if (len(modules) != len(classes) or len(classes) != len(mods_dependencies)):
        raise BOAFlowException(f"length of modules ({len(modules)}), classes"
                               f" ({len(classes)}) and dependencies"
                               f" ({len(mods_dependencies)}) should be equal",
                               Error.error_rules_modules_classes_args_neq_length)

    dependencies_names = []
    dependencies_graph = {}

    for m, c in zip(modules, classes):
        dependencies_names.append(f"{m}.{c}")

    for key_module, value_dependencies in mods_dependencies.items():
        for key_mod_dependecie in value_dependencies:
            # Check if the dependecie exist
            if key_mod_dependecie not in dependencies_names:
                # The dependency does not exist
                raise BOAFlowException(f"module '{key_module}' has the module dependency"
                                       f" '{key_mod_dependecie}', which is not loaded",
                                       Error.error_module_dependency_failed)

            # Check that the module it is not a dependency of itself
            if key_module == key_mod_dependecie:
                # The module has a dependency of itself
                raise BOAFlowException(f"module '{key_module}' has a dependency of itself,"
                                       " which it is not allowed",
                                       Error.error_module_dependency_itself)

            # Fill dependencies graph
            if not utils.is_key_in_dict(dependencies_graph, key_module):
                dependencies_graph[key_module] = []

            dependencies_graph[key_module].append(key_mod_dependecie)

    # If there are not dependencies for a concrete module, is not initialized, so we have to
    for dependency_name in dependencies_names:
        if not utils.is_key_in_dict(dependencies_graph, dependency_name):
            # Initialize modules without dependencies
            dependencies_graph[dependency_name] = []

    # Check if the dependencies are cyclic
    if utils.is_graph_cyclic(dependencies_graph):
        raise BOAFlowException(f"cyclic dependencies detected",
                               Error.error_module_dependencies_cyclic)

    return dependencies_graph

def get_execution_order(dependencies_graph):
    """The objective is return an order of execution
    which avoids dependencies problems

    Arguments:
        dependencies_graph (dict): dependencies of the modules.
            The graph has not to be cyclic and has not to contain
            self references of nodes.

    Returns:
        list: list with an order which avoids dependencies
        problems. The elements that will contain the list
        are the keys of the *dependencies_graph*.

    Note:
        If you use a cyclic graph or a graph which contains
        self references, it might fell in an infinite loop.
        Check *check_dependencies* method if you are in that
        situation.
    """
    result = []

    # Will not finish until we have the order of execution
    while len(result) != len(dependencies_graph):
        for module, dependencies in dependencies_graph.items():
            # Check if the current module has been executed or not
            if module not in result:
                # The current module has not been executed

                # Check if the current module has not dependencies
                if len(dependencies) == 0:
                    result.append(module)
                # The current module has dependencies
                else:
                    found_dependencies = []

                    # Check if all the dependencies of the current module has been executed
                    for dependency in dependencies:
                        if dependency in result:
                            # The current dependency has been executed
                            found_dependencies.append(dependency)

                    if len(dependencies) == len(found_dependencies):
                        # All the dependencies of the current module has been executed
                        result.append(module)

    return result

def apply_execution_order(execution_order, modules, classes, reports, lifecycles):
    """It applies a concrete execution order.

    Arguments:
        execution_order (list): order to be applied. It contains
            values in the format "module_name"."class_name" (without
            the quotes).
        modules (list): list of modules.
        classes (list): list of classes.
        reports (list): list of reports.
        lifecycles (list): list of lifecycles.
    """
    expected_format = []

    for mod_name, class_name in zip(modules, classes):
        expected_format.append(f"{mod_name}.{class_name}")

    index = 0
    found_indexes = []

    while index < len(execution_order):
        if index in found_indexes:
            index += 1
            continue

        # Get the current position of the module to be executed
        current_index = expected_format.index(execution_order[index])

        if current_index <= index:
            # Do not move the modules that are in the correct position
            index += 1
            continue

        # Swap the current position with the order of execution
        modules[current_index], modules[index] = modules[index], modules[current_index]
        classes[current_index], classes[index] = classes[index], classes[current_index]
        reports[current_index], reports[index] = reports[index], reports[current_index]
        lifecycles[current_index], lifecycles[index] = lifecycles[index], lifecycles[current_index]

        #found_indexes.append(index)
        #found_indexes.append(current_index)

        index += 1
