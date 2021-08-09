
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
    description = "Static and dynamic analyzer of general purpose written in Python"
    ok_code = 0

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
    error_logging_configuration = 3

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
    #error_module_some_instance_loading_failed = 204
    error_module_cannot_remove_not_loaded_module = 204
    error_module_cannot_load_abstract_instance = 205
    error_module_not_expected_type = 206
    error_module_importer_could_not_be_instantiated = 207
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
    #error_lifecycle_args_wrong_type = 40
    #error_lifecycle_args_neq_length = 41
    error_lifecycle_module_exception = 40
    error_lifecycle_exception = 41
    error_lifecycle_module_not_found = 42
    error_lifecycle_could_not_load_abstract_instance = 43
    error_lifecycle_could_not_load_instance = 44
    error_lifecycle_not_expected_type = 45
    error_lifecycle_wrong_analysis = 46

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

    # Runner modules errors
    error_runner_module_not_found = 60
    error_runner_module_not_loaded = 61
    error_runner_module_abstract_not_loaded = 62
    error_runner_module_abstract_not_expected_type = 63
    error_runner_module_some_callback_not_executed = 64
    error_runner_module_no_callback_executed = 64
    error_runner_module_failed_in_initialization = 65
    error_runner_module_failed_in_parsing = 66
    error_runner_module_failed_in_execution = 67


    # Other errors
    error_other_reserved_keyword_being_used = 1001

class Regex:
    """Regex class.

    This class contains the regex which are used by
    other BOA modules.
    """
    regex_general_module_class_name = r'^[a-zA-Z0-9_]+[.][a-zA-Z0-9_]+$'
    regex_which_respect_quotes_params = r'(?:[^\s,"]|"(?:\\.|[^"])*")+'

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
    other_logging_format = "[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s"
    other_valid_analysis = ("static", "dynamic")

    # Modules
    modules_directory = "modules"
    abstract_module_name = "boam_abstract"
    abstract_module_class_name = "BOAModuleAbstract"
    ## Static analysis
    modules_static_analysis_subdir = "static_analysis"
    ## Dynamic analysis
    modules_dynamic_analysis_subdir = "dynamic_analysis"

    # Runners
    runners_static_analysis_directory = "runners/static_analysis"
    runners_dynamic_analysis_directory = "runners/dynamic_analysis"
    ## Static analysis
    ### Parser modules
    parser_modules_directory = "parser_modules"
    abstract_parser_module_filename = "boapm_abstract.py"
    abstract_parser_module_name = "boapm_abstract"
    abstract_parser_module_class_name = "BOAParserModuleAbstract"
    ## Dynamic analysis
    ### Fail modules
    fail_modules_directory = "fails_modules"
    abstract_fail_module_filename = "boafm_abstract.py"
    abstract_fail_module_name = "boafm_abstract"
    abstract_fail_module_class_name = "BOAFailModuleAbstract"
    ### Input modules
    input_modules_directory = "inputs_modules"
    abstract_input_module_filename = "boaim_abstract.py"
    abstract_input_module_name = "boaim_abstract"
    abstract_input_module_class_name = "BOAInputModuleAbstract"

    # Lifecycle modules
    lifecycle_modules_directory = "lifecycles"
    lifecycle_abstract_module_filename = "boalc_abstract.py"
    lifecycle_abstract_module_name = "boalc_abstract"
    lifecycle_abstract_module_class_name = "BOALifeCycleAbstract"
    ## Static analysis
    lifecycle_static_analysis_subdir = "static_analysis"
    ## Dynamic analysis
    lifecycle_dynamic_analysis_subdir = "dynamic_analysis"

    # Report
    report_modules_directory = "reports"
    report_abstract_module_filename = "boar_abstract.py"
    report_abstract_module_name = "reports.boar_abstract"
    report_abstract_module_class_name = "BOAReportAbstract"
