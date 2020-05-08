
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
    version = 0.3
    name = "BOA"
    description = "In its first days attempted to detect buffer overflow" \
                  " threats in C language files. Nowadays, it attemts to" \
                  " detect all possible security threats from different" \
                  " programming languages. To achieve our goal, we use" \
                  " rules files."
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
    args_help = ["language file to analyze.",
                 "rules file"]
    # None or default value
    args_bool = [None,
                 None]

    # Optional arguments has to start with "--"
    opt_args_str = ["--no-fail"]
    opt_args_help = ["if a user module loading fails, execution will not stop." \
                     " Default value is False."]
    # None or default value
    opt_args_bool = [False]

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
    error_args_incorrect = 10
    error_args_type = 11

    # Parsing errors
    #error_parse_parse = 20

    # Modules errors
    error_module_some_mandatory_and_user_failed = 200
    error_module_some_mandatory_failed = 201
    error_module_some_user_failed = 202
    error_module_cannot_load_instance = 203
    error_module_some_instance_loading_failed = 204
    error_module_cannot_remove_not_loaded_module = 205
    error_module_cannot_load_abstract_instance = 206
    error_module_not_expected_type = 207
    error_module_importer_could_not_be_instantiated = 208
    # Modules errors -> dependencies
    error_module_dependency_failed = 210
    error_module_dependency_itself = 211
    error_module_dependencies_cyclic = 212
    error_module_dependency_callback_not_found = 213

    # Rules errors
    error_rules_modules_classes_args_neq_length = 30
    error_rules_bad_naming_references = 31
    error_rules_could_not_open_file = 32
    error_rules_could_not_read_file = 33
    error_rules_could_not_close_file = 34
    error_rules_bad_checking = 35
    error_rules_args_not_found = 36

    # Lifecycle errors
    error_lifecycle_args_wrong_type = 40
    error_lifecycle_args_neq_length = 41
    error_lifecycle_module_exception = 42
    error_lifecycle_exception = 43
    error_lifecycle_module_not_found = 44
    error_lifecycle_could_not_load_abstract_instance = 45
    error_lifecycle_could_not_load_instance = 46
    error_lifecycle_not_expected_type = 47

    # Report errors
    error_report_args_not_optional = 500
    error_report_args_not_expected_type = 501
    error_report_who_regex_fail = 502
    error_report_append_failed = 503
    error_report_unknown = 504
    error_report_module_abstract_not_loaded = 505
    error_report_module_not_found = 506
    error_report_module_abstract_not_expected_type = 507
    # Report -> severity enum errors
    error_report_severity_enum_does_not_match = 510
    error_report_severity_enum_not_expected = 511
    error_report_severity_enum_module_not_found = 512
    error_report_severity_enum_module_not_loaded = 513

    # Parser module errors
    error_parser_module_not_found = 60
    error_parser_module_not_loaded = 61
    error_parser_module_abstract_not_loaded = 62
    error_parser_module_abstract_not_expected_type = 63
    error_parser_module_some_callback_not_executed = 64
    error_parser_module_no_callback_executed = 64
    error_parser_module_failed_in_initialization = 65
    error_parser_module_failed_in_parsing = 66
    error_parser_module_failed_in_execution = 67


    # Other errors
    error_other_reserved_keyword_being_used = 1001

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
    other_argument_name_for_dependencies_in_modules = "__dependencies"

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
