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
from own_exceptions import ParseError
from constants import Meta, Error
from args_manager import ArgsManager
from util import eprint, is_key_in_dict, file_exists
from modules_importer import ModulesImporter
from main_loop import MainLoop
from rules_manager import RulesManager

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
    """

    instance = module_loader.get_instance(module_name, class_name)

    if instance is None:
        return [Error.error_module_cannot_load_instance, instance]

    try:
        instance = instance(module_args)
        print(f"Info: {module_name}.{class_name} initialized.")
    except Exception as e:
        eprint(f"Error: could not load an instance of {module_name}.{class_name} "
               f"(bad implementation of {Meta.abstract_module_name}."
               f"{Meta.abstract_module_class_name} in {module_name}.{class_name}?). {e}.")

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

def manage_main_loop(instances, ast):
    """It handles the main loop through MainLoop class.

    Arguments:
        instances: module instances which will be looped.
        ast: processed AST.

    Returns:
        int: status code
    """

    main_loop = MainLoop(instances, ast)

    # It handles the loop work
    rtn_code = main_loop.handle_loop()

    return rtn_code

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

    rtn = manage_rules_file()
    rtn_code = rtn[0]
    rules_manager = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    modules = []
    classes = []
    mods_args = {}	# {"class": {"arg1": "value2", "arg2": ["value2", "value3"]}}

    args = rules_manager.get_args()
    rmodules = rules_manager.get_rules("boa_rules.modules.module", True)

    for m in rmodules:
        module_name = m['module_name']
        class_name = m['class_name']

        modules.append(module_name)
        classes.append(class_name)

        if not is_key_in_dict(args, f"{module_name}.{class_name}"):
            eprint(f"Error: args for module {module_name}.{class_name} not found.")
            return Error.error_rules_args_not_found

        mods_args[f"{module_name}.{class_name}"] = args[f"{module_name}.{class_name}"]

    if (len(modules) != len(classes) or len(modules) != len(mods_args)):
        eprint(f"Error: modules length ({len(modules)}), classes length ({len(classes)})"
               f" and arguments length ({len(mods_args)}) are not equal.")
        return Error.error_rules_modules_classes_args_neq_length

    # Parse C file
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
    rtn_code = manage_main_loop(instances, ast)

    if rtn_code != Meta.ok_code:
        return rtn_code

    return Meta.ok_code

if __name__ == "__main__":
    __rtn_code__ = main()

    print(f"\nExit status: {__rtn_code__}")

    sys.exit(__rtn_code__)
