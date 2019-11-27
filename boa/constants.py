
class Meta:
    version = 0.1
    name = "BOA"
    description = "It attempts to detect buffer overflow threats in C language files."
    ok_code = 0

class Args:
    args_str   = [   'file']
    args_help  = [   'C language file to analyze.']

    opt_args_str  = [   '--pycparser_args', 
                        '--rules_file']

    opt_args_help = [   'It defines the PYCPARSER args.', 
                        'Path to the used rules to analyze the C file.']

class Error:
    error_unknown = 1
    error_file_not_found = 2

    error_args_code = 10
    error_args_type = 11

    error_parse_parse = 20