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

# Own libs
from constants import Meta, Error
from args_manager import ArgsManager
from util import file_exists, eprint
from own_exceptions import BOAFlowException
import boa_internals

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

def main():
    """It handles the main BOA's flow at a high level.

    Returns:
        int: status code
    """

    print(f"Welcome to {Meta.name} - Version {Meta.version}\n")

    try:
        # Parse and check args
        rtn_code = manage_args()

        if rtn_code != Meta.ok_code:
            raise BOAFlowException("args management failed", rtn_code)

        # Check if lang. file exists
        if not file_exists(ArgsManager.args.file):
            raise BOAFlowException(f"file '{ArgsManager.args.file}' not found",
                                   Error.error_file_not_found)

        # Manage rules file
        rules_manager = boa_internals.manage_rules_file()

        # Process all security modules and get the necessary information
        processed_info_sec_mods = boa_internals.process_security_modules(rules_manager)

        modules = processed_info_sec_mods[0]
        classes = processed_info_sec_mods[1]
        mods_args = processed_info_sec_mods[2]
        reports = processed_info_sec_mods[3]
        lifecycles = processed_info_sec_mods[4]

        # Parser module
        parser_rules = rules_manager.get_rules("boa_rules.parser")

        # Get parser module instance
        boapm_instance = boa_internals.get_boapm_instance(parser_rules['module_name'], parser_rules['class_name'])

        # Get environment variables for the parser module
        parser_env_vars = boa_internals.get_parser_env_vars(parser_rules)

        # Handle parser module and get the result for the lifecycle
        lifecycle_args = boa_internals.handle_boapm(boapm_instance, parser_rules, parser_env_vars)

        # Load modules
        rtn = boa_internals.load_modules(modules)
        rtn_code = rtn[0]
        mod_loader = rtn[1]
        fail_if_some_user_module_failed = False

        if ArgsManager.args.no_fail is not None:
            fail_if_some_user_module_failed = True

        if (rtn_code == Error.error_module_some_user_failed and fail_if_some_user_module_failed):
            raise BOAFlowException("a security module failed", rtn_code)
        if rtn_code not in (Meta.ok_code, Error.error_module_some_user_failed):
            raise BOAFlowException("a security module failed", rtn_code)

        # Remove not loaded modules
        boa_internals.remove_not_loaded_modules(mod_loader, modules, classes, mods_args)

        # Load rules and instances with that rules as args
        instances = boa_internals.load_instances(modules, classes, mods_args, mod_loader)

        # It handles the lifecycles
        lifecycle_handler = boa_internals.manage_lifecycles(instances, reports, lifecycle_args, lifecycles)

        # Display all the found threats
        report = lifecycle_handler.get_final_report()

        if report:
            print()
            report.display_all()
    except BOAFlowException as e:
        # Error in some internal function.

        if e.message:
            eprint(f"Error: {e.message}.")
        if e.error_code:
            return e.error_code

        eprint(f"Error: 'BOAFlowException' does not have 'error_code' as expected.")
        return Error.error_unknown
    except Exception as e:
        # Unexpected and unknown error.

        eprint(f"Error: {e}.")
        return Error.error_unknown

    return Meta.ok_code

if __name__ == "__main__":
    __rtn_code__ = main()

    print(f"\nExit status: {__rtn_code__}")

    sys.exit(__rtn_code__)
