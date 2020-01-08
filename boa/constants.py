
class Meta:
    version = 0.1
    name = "BOA"
    description = "It attempts to detect buffer overflow threats in C language files."
    ok_code = 0
    modules_directory = "modules"
    abstract_module_name = "boam_abstract"
    abstract_module_class_name = "BOAM_abstract"

class Args:
    # Mandatory arguments has not to start with "--"
    args_str   = [   "file",
                     "rules_file"]
    args_help  = [   "C language file to analyze.",
                     "Rules file"]

    # Optional arguments has to start with "--"
    opt_args_str  = [   ]

    opt_args_help = [   ]

class Error:
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