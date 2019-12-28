
class Meta:
    version = 0.1
    name = "BOA"
    description = "It attempts to detect buffer overflow threats in C language files."
    ok_code = 0
    modules_directory = "modules"
    abstract_module_class_name = "boam_abstract"

class Args:
    args_str   = [   "file"]
    args_help  = [   "C language file to analyze."]

    opt_args_str  = [   "--pycparser_args", 
                        "--rules_file"]

    opt_args_help = [   "It defines the PYCPARSER args.", 
                        "Path to the used rules to analyze the C file."]

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

    # Rules errors
    error_rules_modules_classes_neq_length = 40