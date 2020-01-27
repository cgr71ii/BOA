
"""File with constant values.

This file contains constant information about BOA.

It contains multiple classes:\n
1. Meta class: it contains information about BOA.
2. Args class: it contains the mandatory and optional BOA arguments.
3. Error class: it contains status code with a descriptive name.
4. Regex class: it contains regex strings.
5. Other class: it contains all the constants whose goal does not
   match with the other classes.
"""

class Meta:
    """Meta class.

    It contains information about BOA like the version, the description, ...
    """
    version = 0.1
    name = "BOA"
    description = "It attempts to detect buffer overflow threats in C language files."
    ok_code = 0
    modules_directory = "modules"
    abstract_module_name = "boam_abstract"
    abstract_module_class_name = "BOAM_abstract"

class Args:
    """Args class.

    It contains information about which kind of argumentes
    can be suplied to BOA. Concretely, in this class can
    be specified the name and the description of the
    mandatory and optional arguments.
    """
    # Mandatory arguments has not to start with "--"
    args_str = ["file",
                "rules_file"]
    args_help = ["C language file to analyze.",
                 "Rules file"]

    # Optional arguments has to start with "--"
    opt_args_str = ["--no-fail"]
    opt_args_help = ["If a user module loading fails, BOA will stop."]

class Error:
    """Error class.

    It contains information about the different error status code
    we can find through BOA's code. The information that it is in
    this class are just numeric status error with a descriptive
    name to know exactly the cause of the error.

    When BOA finishes the execution, it displays the status code.
    If the status code displayed matches with Meta.ok_code,
    it means that everything went fine. Otherwise, check the
    status code within this class.
    """
    # General errors
    # ok_code = 0
    error_unknown = 1
    error_file_not_found = 2

    # Args errors
    error_args_code = 10
    error_args_type = 11

    # Parsing errors
    error_parse_parse = 20

    # Modules errors
    error_module_some_mandatory_and_user_failed = 30
    error_module_some_mandatory_failed = 31
    error_module_some_user_failed = 32
    error_module_cannot_load_instance = 33
    error_module_some_instance_loading_failed = 34
    error_module_cannot_remove_not_loaded_module = 35

    # Rules errors
    error_rules_modules_classes_args_neq_length = 40
    error_rules_bad_naming_references = 41
    error_rules_could_not_open_file = 42
    error_rules_could_not_read_file = 43
    error_rules_could_not_close_file = 44
    error_rules_bad_checking = 45
    error_rules_args_not_found = 46

    # Main loop errors
    error_loop_args_wrong_type = 50
    error_loop_args_neq_length = 51
    error_loop_module_exception = 52

    # Report errors
    error_report_args_not_optional = 60
    error_report_args_not_expected_type = 61
    error_report_who_regex_fail = 62
    error_report_append_failed = 63



    # Other errors
    error_other_severity_enumeration_module_not_found = 1000
    error_other_severity_enumeration_module_not_loaded = 1001

class Regex:
    """Regex class.

    This class contains the regex which are used by
    other BOA modules.
    """
    regex_general_module_class_name = "^[a-zA-Z0-9_]+[.][a-zA-Z0-9_]+$"

class Other:
    """Other class.

    This class contains all the other information that
    does not match with the goal of the other classes.
    Or does not have a concrete goal.
    """
    other_report_default_severity_enum = "severity_base.SeverityBase"
