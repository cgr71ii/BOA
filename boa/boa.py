#!/usr/bin/env python3

"""BOA main file.

This file handles the higher level interaction with BOA.

Main tasks:\n
* It handles args.\n
* It handles parser modules.\n
* It handles code modules (BOA's goal).\n
* It handles the general flow.\n
"""

# Std libs
import sys
import os

# Pycparser libs
from pycparser import parse_file

# Own libs
from own_exceptions import ParseError, BOAPMInitializationError, BOAPMParseError
from constants import Meta, Error, Other
from args_manager import ArgsManager
from util import eprint, is_key_in_dict, file_exists, get_current_path
from util import invoke_by_name, get_name_from_class_instance
from modules_importer import ModulesImporter
from main_loop import MainLoop
from rules_manager import RulesManager
from report import Report

def manage_args():
    """It handles BOA's general args through ArgsManager class.

    Returns:
        int: status code
    """

    if len(sys.argv) == 1:
        sys.argv.append("-h")

    args_manager = ArgsManager()

    args_manager.load_args()
    args_manager.parse()

    rtn_code = args_manager.check()

    if rtn_code != Meta.ok_code:
        return rtn_code

    return Meta.ok_code

def parse_c_file():
    """It parses the code file which is passed through the args.

    Raises:
        FileNotFoundError: if a path which is provided in the
            rules file does not exist or is not valid.

    Returns:
        list: list containing:
            * int: status code\n
            * AST (Abstract Syntax Tree)
    """

    file_path = ArgsManager.args.file
    ast = None
    rtn_code = Meta.ok_code
    pycparser_fake_libc_include_ev = os.environ.get("PYCPARSER_FAKE_LIBC_INCLUDE_PATH")

    # parse_file (__init__.py) returns an AST or ParseError if doesn't parse successfully
    try:
        if not file_exists(file_path):
            raise FileNotFoundError()

        if pycparser_fake_libc_include_ev is not None:
            # use_cpp = Use CPreProcessor
            ast = parse_file(file_path, use_cpp=True, cpp_path="gcc",
                             cpp_args=["-E", f"-I{pycparser_fake_libc_include_ev}"])
        else:
            ast = parse_file(file_path, use_cpp=False)
    except ParseError:
        eprint(f"Error: could not parse file '{file_path}'.")
        rtn_code = Error.error_parse_parse
    except FileNotFoundError:
        eprint(f"Error: file '{file_path}' not found.")
        rtn_code = Error.error_file_not_found
    except Exception as e:
        eprint(f"Error: {e} (if using pycparser for a C file and using preprocess directives,"
               " try defining PYCPARSER_FAKE_LIBC_INCLUDE_PATH environmental variable"
               " to solve the problem).")
        rtn_code = Error.error_unknown

    return [rtn_code, ast]

def load_modules(user_modules):
    """It handles the modules loading through ModulesImporter class.

    Arguments:
        user_modules (list): user modules (i.e. non-mandatory modules)
            to be loaded.

    Returns:
        list: list contining:
            * int: status code\n
            * ModulesImporter: ModulesImporter instance
    """

    if not isinstance(user_modules, list):
        user_modules = [user_modules]

    mandatory_modules = [Meta.abstract_module_name]
    modules = mandatory_modules + user_modules

    # Through mod_loader we can get modules, but it is not necessary (sys.modules)
    mod_loader = ModulesImporter(modules)
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

def load_instance(module_loader, module_name, class_name, module_args):
    """It handles the instances loading throught a ModulesImporter instance.
    It loads one instance from a class.

    Arguments:
        module_loader (ModulesImporter): instance which will load modules.
        module_name (str): module name.
        class_name (str): class name.
        module_args: args to use to initialize the instance.

    Returns:
        list: list containing:
            * int: status code\n
            * loaded instance

    Note:
        All the modules has to inherit from *constants.Meta.
        abstract_parser_module_class_name*.
    """
    instance = module_loader.get_instance(module_name, class_name)
    abstract_instance = module_loader.get_instance(Meta.abstract_module_name,
                                                   Meta.abstract_module_class_name)

    if instance is None:
        return [Error.error_module_cannot_load_instance, None]
    if abstract_instance is None:
        return [Error.error_module_cannot_load_instance, None]
    if (not issubclass(instance, abstract_instance) or
            instance is abstract_instance):
        eprint(f"Error: instance '{module_name}.{class_name}'"
               " has not the expected type (does it inherit from "
               f"'{Meta.abstract_module_name}.{Meta.abstract_module_class_name}'?).")
        return [Error.error_module_not_expected_type, None]

    try:
        instance = instance(module_args)

        print(f"Info: '{module_name}.{class_name}' initialized.")
    except Exception as e:
        eprint(f"Error: could not load an instance of '{module_name}.{class_name}' "
               f"(bad implementation of '{Meta.abstract_module_name}."
               f"{Meta.abstract_module_class_name}' in '{module_name}.{class_name}'?). {e}.")

    return [Meta.ok_code, instance]

def get_boapm_instance(module_name, class_name):
    """It attempts to load a BOAPM module and get an
    instance of it.

    Arguments:
        module_name (str): BOAPM module name.
        class_name (str): BOAPM class name.

    Returns:
        list: list containing:
            * int: status code\n
            * loaded instance
    """
    file_path = f'{get_current_path(__file__)}/{Meta.parser_modules_directory}'
    abstract_instance = ModulesImporter.load_and_get_instance(Meta.abstract_parser_module_name,
                                                              f'{file_path}/{Meta.abstract_parser_module_name}.py',
                                                              Meta.abstract_parser_module_class_name)
    file_path = f'{file_path}/{module_name}.py'

    if not abstract_instance:
        eprint("Error: could not load and get an instance of "
               f"'{Meta.abstract_parser_module_name}.{Meta.abstract_parser_module_class_name}'.")
        return [Error.error_parser_module_abstract_not_loaded, None]
    if not file_exists(file_path):
        eprint(f"Error: file '{file_path}' not found.")
        return [Error.error_parser_module_not_found, None]

    instance = ModulesImporter.load_and_get_instance(
        module_name,
        file_path,
        class_name)

    if not instance:
        eprint(f"Error: could not load the parser module '{module_name}.{class_name}'.")
        return [Error.error_parser_module_not_loaded, instance]

    if (not issubclass(instance, abstract_instance) or
            instance is abstract_instance):
        eprint(f"Error: instance '{module_name}.{class_name}' has not the expected"
               f" type (does it inherit from '{Meta.abstract_parser_module_name}."
               f"{Meta.abstract_parser_module_class_name}'?).")
        return [Error.error_parser_module_abstract_not_expected_type, instance]

    return [Meta.ok_code, instance]

def remove_not_loaded_modules(mod_loader, modules, classes, mods_args):
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

    Returns:
        int: status code
    """

    not_loaded_modules = mod_loader.get_not_loaded_modules()
    rtn_code = Meta.ok_code

    for not_loaded_module in not_loaded_modules:
        try:
            index = modules.index(not_loaded_module)

            removed_module = modules.pop(index)
            removed_class = classes.pop(index)
            removed_mod_args = mods_args.pop(removed_class)

            print(f"Info: {removed_module}.{removed_class}({removed_mod_args}) was removed.")
        except Exception as e:
            eprint(f"Error: could not remove a module/class/arg while trying"
                   f" to remove module {not_loaded_module}. {e}.")
            rtn_code = Error.error_module_cannot_remove_not_loaded_module

    return rtn_code

def manage_rules_file():
    """It handles the rules file (parsing, checking and processing)
    through RulesManager class.

    Returns:
        list: list contining:
            * int: status code\n
            * RulesManager: RulesManager instance
    """

    rules_manager = RulesManager(ArgsManager.args.rules_file)

    # Open file
    rtn_code = rules_manager.open()

    if rtn_code != Meta.ok_code:
        return [rtn_code, rules_manager]

    # Read and save relevant information
    rtn_code = rules_manager.read()

    if rtn_code != Meta.ok_code:
        return [rtn_code, rules_manager]

    rtn_code = rules_manager.close()

    if rtn_code != Meta.ok_code:
        return [rtn_code, rules_manager]

	# Check rules and process arguments from rules file
    if not rules_manager.check_rules(True):
        return [Error.error_rules_bad_checking, rules_manager]

    return [Meta.ok_code, rules_manager]

def manage_main_loop(instances, reports, ast):
    """It handles the main loop through MainLoop class.

    Arguments:
        instances: module instances which will be looped.
        ast: processed AST.

    Returns:
        list: list contining:
            * int: status code\n
            * MainLoop: MainLoop instance
    """

    main_loop = MainLoop(instances, reports, ast)

    # It handles the loop work
    rtn_code = main_loop.handle_loop()

    return [rtn_code, main_loop]

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

    Returns:
        list: list contining:
            * int: status code\n
            * dict: callback results (boa_rules.parser.callback.method) of *boapm_instance*.
    """
    # Initialize the instance and other necessary information
    boapm_instance = boapm_instance(ArgsManager.args.file, environment_variable_names)
    boapm_instance_name = get_name_from_class_instance(boapm_instance)
    callbacks = parser_rules["callback"]["method"]
    names = []
    methods = []
    boapm_results = {}
    rtn_code = Meta.ok_code

    # Call initialization methods defined in
    try:
        boapm_instance.initialize()
        boapm_instance.parse()
    except BOAPMInitializationError as e:
        eprint(f"Error: '{boapm_instance_name}.initialize()': {e}.")
        return [Error.error_parser_module_failed_in_initialization, boapm_results]
    except BOAPMParseError as e:
        eprint(f"Error: '{boapm_instance_name}.parse()': {e}.")
        return [Error.error_parser_module_failed_in_parsing, boapm_results]
    except Exception as e:
        eprint(f"Error: '{boapm_instance_name}': {e}.")
        return [Error.error_parser_module_failed_in_execution, boapm_results]

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

        if result is not Other.util_invoke_by_name_error_return:
            boapm_results[name] = result
        else:
            error = True

    if error:
        if len(boapm_results) == 0:
            rtn_code = Error.error_parser_module_no_callback_executed
        else:
            rtn_code = Error.error_parser_module_some_callback_not_executed

    return [rtn_code, boapm_results]

def get_parser_env_vars(parser_rules):
    """It gets the environment variables from the rules file.

    Arguments:
        parser_rules (OrderedDict): rules which contains the necessary information
            for the parser module in order to be initialized.

    Returns:
        list: environment variable names
    """
    env_vars = parser_rules["env_vars"]["env_var"]

    if not env_vars:
        return []
    elif isinstance(env_vars, str):
        return [env_vars]
    elif not isinstance(env_vars, list):
        eprint("Error: expected type in environment variables is 'list',"
               f" but actually is '{type(env_vars)}'.")

    return env_vars

def main():
    """It handles the main BOA's flow at a high level.

    Returns:
        int: status code
    """

    print(f"Welcome to {Meta.name} - Version {Meta.version}\n")

    # Parse and check args
    rtn_code = manage_args()

    if rtn_code != Meta.ok_code:
        return rtn_code

    # Check if lang. file exists
    if not file_exists(ArgsManager.args.file):
        eprint(f"Error: file '{ArgsManager.args.file}' not found.")

        return Error.error_file_not_found

    # Manage rules file
    rtn = manage_rules_file()
    rtn_code = rtn[0]
    rules_manager = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    modules = []
    classes = []
    mods_args = {}	# {"class": {"arg1": "value2", "arg2": ["value2", "value3"]}}
    severity_enums = []
    reports = []

    args = rules_manager.get_args()
    rmodules = rules_manager.get_rules("boa_rules.modules.module", True)

    for m in rmodules:
        module_name = m['module_name']
        class_name = m['class_name']
        severity_enum_formatted = m['severity_enum']
        severity_enum_module_name = severity_enum_formatted.split('.')[0]
        severity_enum_class_name = severity_enum_formatted.split('.')[1]

        modules.append(module_name)
        classes.append(class_name)

        if not is_key_in_dict(args, f"{module_name}.{class_name}"):
            eprint(f"Error: args for module {module_name}.{class_name} not found.")
            return Error.error_rules_args_not_found

        severity_enum_path = f"{get_current_path()}/enumerations/severity/{severity_enum_module_name}.py"

        if not file_exists(severity_enum_path):
            eprint(f"Error: could not found the severity enumeration module '{severity_enum_module_name}.py'.")
            return Error.error_other_severity_enumeration_module_not_found

        severity_enum_instance = ModulesImporter.load_and_get_instance(
            severity_enum_module_name,
            severity_enum_path,
            severity_enum_class_name)

        if not severity_enum_instance:
            eprint(f"Error: could not load the severity enumeration '{severity_enum_module_name}.{severity_enum_class_name}'.")
            return Error.error_other_severity_enumeration_module_not_loaded

        severity_enums.append(severity_enum_instance)
        reports.append(Report(severity_enum_instance))

        mods_args[f"{module_name}.{class_name}"] = args[f"{module_name}.{class_name}"]

    if (len(modules) != len(classes) or len(modules) != len(mods_args)):
        eprint(f"Error: modules length ({len(modules)}), classes length ({len(classes)})"
               f" and arguments length ({len(mods_args)}) are not equal.")
        return Error.error_rules_modules_classes_args_neq_length

    # Parse lang. file

    parser_rules = rules_manager.get_rules("boa_rules.parser")

    rtn = get_boapm_instance(parser_rules['module_name'], parser_rules['class_name'])
    rtn_code = rtn[0]
    boapm_instance = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    parser_env_vars = get_parser_env_vars(parser_rules)

    rtn = handle_boapm(boapm_instance, parser_rules, parser_env_vars)
    rtn_code = rtn[0]
    # TODO use lifecycle_args in MainLoop
    # TODO use MainLoop as base for lifecycles
    lifecycle_args = rtn[1]

    # TODO use an argument to know if execution should be stopped
    #  when some parser module didn't succeed with a callback.
    if rtn_code != Meta.ok_code:
        return rtn_code

    rtn = parse_c_file()
    rtn_code = rtn[0]
    ast = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    # Load modules
    rtn = load_modules(modules)
    rtn_code = rtn[0]
    mod_loader = rtn[1]
    fail_if_some_user_module_failed = False

    if ArgsManager.args.no_fail is not None:
        fail_if_some_user_module_failed = True

    if (rtn_code == Error.error_module_some_user_failed and fail_if_some_user_module_failed):
        return rtn_code
    if rtn_code not in (Meta.ok_code, Error.error_module_some_user_failed):
        return rtn_code

    # Load rules and instances with that rules as args
    instances = []
    index = 0

    # Remove not loaded modules
    rtn_code = remove_not_loaded_modules(mod_loader, modules, classes, mods_args)

    if rtn_code != Meta.ok_code:
        return rtn_code

    while index < len(modules):
        try:
            mod_args = mods_args[f"{modules[index]}.{classes[index]}"]
        except KeyError as e:
            eprint(f"Error: could not get {e} arguments due to a bad naming reference.")
            return Error.error_rules_bad_naming_references

        rtn = load_instance(mod_loader, modules[index], classes[index], mod_args)
        rtn_code = rtn[0]
        instance = rtn[1]

        if rtn_code != Meta.ok_code:
            return rtn_code

        instances.append(instance)

        index += 1

    # It handles the loop work
    rtn = manage_main_loop(instances, reports, ast)
    rtn_code = rtn[0]
    main_loop = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    # Display all the found threats
    report = main_loop.get_final_report()

    if report:
        print()
        report.display_all()

    return Meta.ok_code

if __name__ == "__main__":
    __rtn_code__ = main()

    print(f"\nExit status: {__rtn_code__}")

    sys.exit(__rtn_code__)
