"""This file has the only purpose of contains a bundle
of functions separately of the main file. It is cleaner
and more readable.
"""

# Own libs
from args_manager import ArgsManager
from own_exceptions import BOAPMInitializationError, BOAPMParseError,\
                           BOALCException, BOAReportEnumTypeNotExpected,\
                           BOAModulesImporterException, BOAFlowException,\
                           BOAUnexpectedException, BOAReportException
from util import eprint, is_key_in_dict, file_exists, get_current_path,\
                 invoke_by_name, get_name_from_class_instance, is_graph_cyclic
from constants import Meta, Error, Other
from modules_importer import ModulesImporter
from lifecycles.boalc_manager import BOALifeCycleManager
from rules_manager import RulesManager

def load_modules(user_modules):
    """It handles the modules loading through ModulesImporter class.

    Arguments:
        user_modules (list): user modules (i.e. non-mandatory modules)
            to be loaded.

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
    except BOAModulesImporterException as e:
        raise BOAFlowException(f"could not instantiate ModulesImporter: {e}",
                               Error.error_module_importer_could_not_be_instantiated)

    mod_loader.load()

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
        abstract_parser_module_class_name*.
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
        eprint(f"Error: instance '{module_name}.{class_name}'"
               " has not the expected type (does it inherit from "
               f"'{Other.abstract_module_name}.{Other.abstract_module_class_name}'?).")
        return [Error.error_module_not_expected_type, None]

    if is_key_in_dict(module_args, Other.other_argument_name_for_dependencies_in_modules):
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

        print(f"Info: Instance '{module_name}.{class_name}' initialized.")
    except Exception as e:
        eprint(f"Error: could not load an instance of '{module_name}.{class_name}' "
               f"(bad implementation of '{Other.abstract_module_name}."
               f"{Other.abstract_module_class_name}' in '{module_name}.{class_name}'?). {e}.")

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
    if filename is None:
        filename = f"{module_name}.py"

    file_path = f'{get_current_path(__file__)}/{Other.parser_modules_directory}'
    abstract_instance = ModulesImporter.load_and_get_instance(Other.abstract_parser_module_name,
                                                              f'{file_path}/{Other.abstract_parser_module_filename}',
                                                              Other.abstract_parser_module_class_name)
    file_path = f'{file_path}/{filename}'

    if not abstract_instance:
        raise BOAFlowException("could not load and get an instance of "
                               f"'{Other.abstract_parser_module_name}.{Other.abstract_parser_module_class_name}'",
                               Error.error_parser_module_abstract_not_loaded)
    if not file_exists(file_path):
        raise BOAFlowException(f"file '{file_path}' not found",
                               Error.error_parser_module_not_found)

    instance = ModulesImporter.load_and_get_instance(
        module_name,
        file_path,
        class_name)

    if not instance:
        raise BOAFlowException(f"could not load the parser module '{module_name}.{class_name}'",
                               Error.error_parser_module_not_loaded)

    if (not issubclass(instance, abstract_instance) or
            instance is abstract_instance):
        raise BOAFlowException(f"instance '{module_name}.{class_name}' has not the expected"
                               f" type (does it inherit from '{Other.abstract_parser_module_name}."
                               f"{Other.abstract_parser_module_class_name}'?)",
                               Error.error_parser_module_abstract_not_expected_type)

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

            if is_key_in_dict(mods_dependencies, f"{removed_module}.{removed_class}"):
                mods_dependencies.pop(f"{removed_module}.{removed_class}")

            reports.pop(index)
            lifecycles.pop(index)

            print(f"Warning: Instance '{removed_module}.{removed_class}' was removed.")
        except Exception as e:
            raise BOAFlowException("could not remove a module/class/arg/dependency while"
                                   f" trying to remove module '{not_loaded_module}': {e}",
                                   Error.error_module_cannot_remove_not_loaded_module)

def manage_rules_file():
    """It handles the rules file (parsing, checking and processing)
    through RulesManager class.

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

def manage_lifecycles(instances, reports, lifecycle_args, lifecycles):
    """It handles the lifecycles of the instances.

    Arguments:
        instances (list): module instances to be executed.
        reports (list): reports to be used by the *instances*.
        lifecycle_args (dict): args to be used by the lifecycle.
        lifecycles (list): list of names in format
            "module_name.class_name" to be used.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        BOALifeCycleManager: BOALifeCycleManager instance
    """
    lifecycle_manager = None
    lifecycle_instances = []
    lifecycle_path = f"{get_current_path()}/"\
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
        lifecycle_path = f"{get_current_path()}/"\
                         f"{Other.lifecycle_modules_directory}/"\
                         f"{lifecycle_module_name}.py"

        # Check if the lifecycle file exists
        if not file_exists(lifecycle_path):
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
        lifecycle_manager = BOALifeCycleManager(instances, reports, lifecycle_args, lifecycle_instances)

        rtn_code = lifecycle_manager.handle_lifecycle()
    except BOALCException as e:
        raise BOAFlowException(f"lifecycle exception: {e}", Error.error_lifecycle_exception)
    except BOAReportException as e:
        raise BOAFlowException(f"report exception: {e}", Error.error_report_unknown)
    except Exception as e:
        raise BOAFlowException(e, Error.error_lifecycle_exception)

    if rtn_code != Meta.ok_code:
        raise BOAFlowException("lifecycle could finish, but not with a correct status",
                               rtn_code)

    return lifecycle_manager

def handle_boapm(boapm_instance, parser_rules, environment_variable_names=None):
    """It handles the BOAParserModule instance.

    It will call the base methods and the callbacks defined in the rules file.

    Arguments:
        boapm_instance (BOAParserModuleAbstract): instance that inherits from
            BOAParserModuleAbstract.
        parser_rules (OrderedDict): rules which contains the necessary information
            for the parser module in order to be initialized.
        environment_variable_names (list): environment variables which will be
            loaded and used in the parser modules. It is the only way to give
            information from outside to the parser module. The default value
            is *None*, which means nothing of information to be given.

    Raises:
        BOAFlowException: could not finish the expected behaviour of
            the function.

    Returns:
        callback results (boa_rules.parser.callback.method) of *boapm_instance*.
    """
    # Initialize the instance and other necessary information
    boapm_instance = boapm_instance(ArgsManager.args.file, environment_variable_names)
    boapm_instance_name = get_name_from_class_instance(boapm_instance)
    callbacks = parser_rules["callback"]["method"]
    names = []
    methods = []
    boapm_results = {}

    # Call initialization methods defined in
    try:
        boapm_instance.initialize()
        boapm_instance.parse()
    except BOAPMInitializationError as e:
        raise BOAFlowException(f"'{boapm_instance_name}.initialize()': {e}",
                               Error.error_parser_module_failed_in_initialization)
    except BOAPMParseError as e:
        raise BOAFlowException(f"'{boapm_instance_name}.parse()': {e}",
                               Error.error_parser_module_failed_in_parsing)
    except Exception as e:
        raise BOAFlowException(f"'{boapm_instance_name}': {e}",
                               Error.error_parser_module_failed_in_execution)

    if not isinstance(callbacks, list):
        callbacks = [callbacks]

    for callback in callbacks:
        callback_dict = dict(callback.items())
        name = callback_dict["@name"]
        method = callback_dict["@callback"]

        if (not name or not method):
            eprint(f"Warning: attributes 'name' ('{name}') and 'callback' ('{method}')"
                   " in 'boa_rules.parser.callback.method' cannot be empty. Skipping.")
        elif name in names:
            eprint(f"Warning: attribute 'name' ('{name}') cannot be duplicated in"
                   " 'boa_rules.parser.callback.method'. Skipping.")
        else:
            names.append(callback_dict["@name"])
            methods.append(callback_dict["@callback"])

    error = False

    for name, method in zip(names, methods):
        result = invoke_by_name(boapm_instance, method)

        # Checking is made with "is" becase we want to check the reference, not the value!
        # Check function "util.invoke_by_name" in order to understand the following checking
        if result is not Other.other_util_invoke_by_name_error_return:
            boapm_results[name] = result
        else:
            error = True

    if error:
        if len(boapm_results) == 0:
            raise BOAFlowException("parser modules: no callback was executed",
                                   Error.error_parser_module_no_callback_executed)

        raise BOAFlowException("parser modules: some callbacks were not executed",
                               Error.error_parser_module_some_callback_not_executed)

    return boapm_results

def get_parser_env_vars(parser_rules):
    """It gets the environment variables from the rules file.

    Arguments:
        parser_rules (OrderedDict): rules which contains the necessary information
            for the parser module in order to be initialized.

    Returns:
        list: environment variable names
    """
    env_vars = parser_rules["env_vars"]

    if not env_vars:
        # No environment variable was defined
        return []

    env_vars = parser_rules["env_vars"]["env_var"]

    if not env_vars:
        return []
    elif isinstance(env_vars, str):
        return [env_vars]
    elif not isinstance(env_vars, list):
        eprint("Error: expected type in environment variables is 'list',"
               f" but actually is '{type(env_vars)}'.")

    return env_vars

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

    file_path = f'{get_current_path(__file__)}/{Other.report_modules_directory}'
    abstract_instance = ModulesImporter.load_and_get_instance(Other.report_abstract_module_name,
                                                              f'{file_path}/{Other.report_abstract_module_filename}',
                                                              Other.report_abstract_module_class_name)
    file_path = f'{file_path}/{filename}'

    if not abstract_instance:
        raise BOAFlowException("could not load and get an instance of "
                               f"'{Other.report_abstract_module_name}.{Other.report_abstract_module_class_name}'",
                               Error.error_report_module_abstract_not_loaded)
    if not file_exists(file_path):
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
        raise BOAUnexpectedException("the default report handler has not the expected value:"
                                     f" '{Other.other_report_default_handler}'")

    report_module_name = report_default_handler[0]
    report_class_name = report_default_handler[1]
    report_args = rules_manager.get_report_args()
    report_rules = rules_manager.get_rules("boa_rules.report")

    if is_key_in_dict(report_rules, "module_name"):
        report_module_name = report_rules["module_name"]
    if is_key_in_dict(report_rules, "class_name"):
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

        if not is_key_in_dict(args, f"{module_name}.{class_name}"):
            raise BOAFlowException(f"args for module '{module_name}.{class_name} not found'",
                                   Error.error_rules_args_not_found)

        severity_enum_path = f"{get_current_path()}/enumerations/severity/{severity_enum_module_name}.py"

        if not file_exists(severity_enum_path):
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
        except BOAReportEnumTypeNotExpected:
            raise BOAFlowException(f"severity enum type not expected: '{severity_enum_name}'",
                                   Error.error_report_severity_enum_not_expected)
        except BOAUnexpectedException as e:
            raise BOAFlowException(f"unexpected exception: {e}", Error.error_report_unknown)
        except BOAFlowException as e:
            raise e
        except Exception as e:
            raise BOAFlowException(e, Error.error_report_unknown)

        reports.append(report)

        mods_args[f"{module_name}.{class_name}"] = \
             args[f"{module_name}.{class_name}"]

        # Set dependencies if exist (are optional)
        if is_key_in_dict(dependencies, f"{module_name}.{class_name}"):
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
                                   Error.error_rules_bad_naming_references)

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
            except AttributeError:
                raise BOAFlowException(f"callback '{callback}' does not exist"
                                       f" in dependency '{dependency}'",
                                       Error.error_module_dependency_callback_not_found)
            except NameError as e:
                raise BOAFlowException(e, Error.error_unknown)
            except Exception as e:
                raise BOAFlowException(e, Error.error_unknown)

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
            if not is_key_in_dict(dependencies_graph, key_module):
                dependencies_graph[key_module] = []

            dependencies_graph[key_module].append(key_mod_dependecie)

    # If there are not dependencies for a concrete module, is not initialized, so we have to
    for dependency_name in dependencies_names:
        if not is_key_in_dict(dependencies_graph, dependency_name):
            # Initialize modules without dependencies
            dependencies_graph[dependency_name] = []

    # Check if the dependencies are cyclic
    if is_graph_cyclic(dependencies_graph):
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
