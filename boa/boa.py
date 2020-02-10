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

    # Parse and check args
    rtn_code = manage_args()

    if rtn_code != Meta.ok_code:
        return rtn_code

    # Check if lang. file exists
    if not file_exists(ArgsManager.args.file):
        eprint(f"Error: file '{ArgsManager.args.file}' not found.")

        return Error.error_file_not_found

    # Manage rules file
    rtn = boa_internals.manage_rules_file()
    rtn_code = rtn[0]
    rules_manager = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    rtn = boa_internals.process_security_modules(rules_manager)
    rtn_code = rtn[0]
    processed_info_sec_mods = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    modules = processed_info_sec_mods[0]
    classes = processed_info_sec_mods[1]
    mods_args = processed_info_sec_mods[2]
    reports = processed_info_sec_mods[3]
    lifecycles = processed_info_sec_mods[4]

    # Parse lang. file

    parser_rules = rules_manager.get_rules("boa_rules.parser")

    rtn = boa_internals.get_boapm_instance(parser_rules['module_name'], parser_rules['class_name'])
    rtn_code = rtn[0]
    boapm_instance = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    parser_env_vars = boa_internals.get_parser_env_vars(parser_rules)

    rtn = boa_internals.handle_boapm(boapm_instance, parser_rules, parser_env_vars)
    rtn_code = rtn[0]
    lifecycle_args = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    # Load modules
    rtn = boa_internals.load_modules(modules)
    rtn_code = rtn[0]
    mod_loader = rtn[1]
    fail_if_some_user_module_failed = False

    if ArgsManager.args.no_fail is not None:
        fail_if_some_user_module_failed = True

    if (rtn_code == Error.error_module_some_user_failed and fail_if_some_user_module_failed):
        return rtn_code
    if rtn_code not in (Meta.ok_code, Error.error_module_some_user_failed):
        return rtn_code

    # Remove not loaded modules
    rtn_code = boa_internals.remove_not_loaded_modules(mod_loader, modules, classes, mods_args)

    if rtn_code != Meta.ok_code:
        return rtn_code

    # Load rules and instances with that rules as args
    rtn = boa_internals.load_instances(modules, classes, mods_args, mod_loader)
    rtn_code = rtn[0]
    instances = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    # It handles the lifecycles
    rtn = boa_internals.manage_lifecycles(instances, reports, lifecycle_args, lifecycles)
    rtn_code = rtn[0]
    lifecycle_handler = rtn[1]

    if rtn_code != Meta.ok_code:
        return rtn_code

    # Display all the found threats
    report = lifecycle_handler.get_final_report()

    if report:
        print()
        report.display_all()

    return Meta.ok_code

if __name__ == "__main__":
    __rtn_code__ = main()

    print(f"\nExit status: {__rtn_code__}")

    sys.exit(__rtn_code__)
