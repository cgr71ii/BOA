
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
    version = 0.2
    name = "BOA"
    description = "It attempts to detect buffer overflow threats in C language files."
    ok_code = 0

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
    error_module_cannot_load_abstract_instance = 36
    error_module_not_expected_type = 37
    error_module_importer_could_not_be_instantiated = 38

    # Rules errors
    error_rules_modules_classes_args_neq_length = 40
    error_rules_bad_naming_references = 41
    error_rules_could_not_open_file = 42
    error_rules_could_not_read_file = 43
    error_rules_could_not_close_file = 44
    error_rules_bad_checking = 45
    error_rules_args_not_found = 46

    # Lifecycle errors
    error_lifecycle_args_wrong_type = 50
    error_lifecycle_args_neq_length = 51
    error_lifecycle_module_exception = 52
    error_lifecycle_exception = 53
    error_lifecycle_module_not_found = 54
    error_lifecycle_could_not_load_abstract_instance = 55
    error_lifecycle_could_not_load_instance = 56
    error_lifecycle_not_expected_type = 57

    # Report errors
    error_report_args_not_optional = 600
    error_report_args_not_expected_type = 601
    error_report_who_regex_fail = 602
    error_report_append_failed = 603
    error_report_unknown = 604
    error_report_module_abstract_not_loaded = 605
    error_report_module_not_found = 606
    error_report_module_abstract_not_expected_type = 607

    # Report -> severity enum errors
    error_report_severity_enum_does_not_match = 610
    error_report_severity_enum_not_expected = 611
    error_report_severity_enum_module_not_found = 612
    error_report_severity_enum_module_not_loaded = 613

    # Parser module errors
    error_parser_module_not_found = 70
    error_parser_module_not_loaded = 71
    error_parser_module_abstract_not_loaded = 72
    error_parser_module_abstract_not_expected_type = 73
    error_parser_module_some_callback_not_executed = 74
    error_parser_module_no_callback_executed = 74
    error_parser_module_failed_in_initialization = 75
    error_parser_module_failed_in_parsing = 76
    error_parser_module_failed_in_execution = 77


    # Other errors


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
    other_report_default_severity_enum = "severity_syslog.SeveritySyslog"
    other_util_invoke_by_name_error_return = "check_with_id_or_is"
    other_lifecycle_default_handler = "boalc_basic.BOALCBasic"
    other_report_default_handler = "boar_stdout.BOARStdout"

    # Modules
    modules_directory = "modules"
    abstract_module_name = "boam_abstract"
    abstract_module_class_name = "BOAModuleAbstract"

    # Parser modules
    parser_modules_directory = "parser_modules"
    abstract_parser_module_filename = "boapm_abstract.py"
    abstract_parser_module_name = "boapm_abstract"
    abstract_parser_module_class_name = "BOAParserModuleAbstract"

    # Lifecycle modules
    lifecycle_modules_directory = "lifecycles"
    lifecycle_abstract_module_filename = "boalc_abstract.py"
    lifecycle_abstract_module_name = "lifecycles.boalc_abstract"
    lifecycle_abstract_module_class_name = "BOALifeCycleAbstract"

    # Report
    report_modules_directory = "reports"
    report_abstract_module_filename = "boar_abstract.py"
    report_abstract_module_name = "reports.boar_abstract"
    report_abstract_module_class_name = "BOAReportAbstract"
