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
import logging
import traceback

# Own libs
from constants import Meta, Error
from args_manager import ArgsManager
from util import file_exists, set_up_logging
from exceptions import BOAFlowException
import boa_utilities

def manage_args():
    """It handles BOA's general args through ArgsManager class.

    Returns:
        int: status code
    """

    if len(sys.argv) == 1:
        sys.argv.append("-h")

    args_manager = ArgsManager()

    args_manager.load_args()
    rtn_code = args_manager.parse()

    if rtn_code != Meta.ok_code:
        return rtn_code

    rtn_code = args_manager.check()

    if rtn_code != Meta.ok_code:
        return rtn_code

    return Meta.ok_code

def main():
    """It handles the main BOA's flow at a high level.

    Returns:
        int: status code
    """
    # Check if user asked about the version
    #  (check with sys.args in order to avoid the mandatory parameters)
    if ("-v" in sys.argv or "--version" in sys.argv):
        print(f"Welcome to {Meta.name} - Version {Meta.version}")

        return Meta.ok_code

    try:
        # Parse and check args
        rtn_code = manage_args()

        if rtn_code != Meta.ok_code:
            # Set up the logging library with the default values
            set_up_logging()

            message = "args management failed"

            if rtn_code == Error.error_args_incorrect:
                # argparse displays its own message, so it is not necessary do it twice
                message = ""

            raise BOAFlowException(message, rtn_code)

        # Set up the logging library
        set_up_logging(filename=ArgsManager.args.log_file, level=ArgsManager.args.logging_level,
                       display_when_file=ArgsManager.args.log_display)

        # Check if lang. file exists
        if not file_exists(ArgsManager.args.code_file):
            raise BOAFlowException(f"file '{ArgsManager.args.code_file}' not found",
                                   Error.error_file_not_found)

        # Manage rules file
        rules_manager = boa_utilities.manage_rules_file()

        # Process all security modules and get the necessary information
        processed_info_sec_mods = boa_utilities.process_security_modules(rules_manager)

        modules = processed_info_sec_mods[0]
        classes = processed_info_sec_mods[1]
        mods_args = processed_info_sec_mods[2]
        mods_dependencies = processed_info_sec_mods[3]
        reports = processed_info_sec_mods[4]
        lifecycles = processed_info_sec_mods[5]

        # Check if the dependencies are ok (detect cyclic dependencies and dependencies to itself)
        dependencies_graph = boa_utilities.check_dependencies(modules, classes, mods_dependencies)

        # Analysis
        analysis = rules_manager.get_rules("boa_rules.@analysis")

        # Get the correct execution order to avoid dependencies problems
        execution_order = boa_utilities.get_execution_order(dependencies_graph)

        # Apply execution order
        boa_utilities.apply_execution_order(execution_order, modules, classes, reports, lifecycles)

        # Parser module
        parser_rules = rules_manager.get_rules("boa_rules.parser")

        # Get parser module instance
        boapm_instance = boa_utilities.get_boapm_instance(parser_rules['module_name'], parser_rules['class_name'])

        # Get environment variables for the parser module
        parser_env_vars = boa_utilities.get_parser_env_vars(parser_rules)

        # Handle parser module and get the result for the lifecycle
        lifecycle_args = boa_utilities.handle_boapm(boapm_instance, parser_rules, parser_env_vars)

        # Load modules
        rtn = boa_utilities.load_modules(modules, analysis)
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
        boa_utilities.remove_not_loaded_modules(mod_loader, modules, classes, mods_args,
                                                mods_dependencies, reports, lifecycles)

        # Load rules and instances with that rules as args
        instances = boa_utilities.load_instances(modules, classes, mods_args,
                                                 mod_loader, rules_manager)

        # It handles the lifecycles
        lifecycle_handler = boa_utilities.manage_lifecycles(instances, reports,
                                                            lifecycle_args, lifecycles,
                                                            analysis)

        # Display all the found threats
        report = lifecycle_handler.get_final_report()

        if report:
            # Blank line and display
            #print()
            report.display_all()
    except BOAFlowException as e:
        # Error in some internal function.

        if e.message:
            logging.error("BOA: %s", e.message)

        if e.error_code:
            return e.error_code

        logging.error("'BOAFlowException' does not have 'error_code' as expected")

        return Error.error_unknown
    except Exception as e:
        # Unexpected and unknown error.

        logging.error("BOA: %s", str(e))

        traceback.print_exc()

        return Error.error_unknown

    return Meta.ok_code

def tear_down():
    logging.info("exit status: %d", __rtn_code__)

if __name__ == "__main__":
    __rtn_code__ = main()

    tear_down()

    sys.exit(__rtn_code__)
