
# Own libs
from constants import Meta
from constants import Error
from args_manager import ArgsManager
from exceptions import ParseError
from util import eprint
from modules_importer import ModulesImporter

# Pycparser libs
from pycparser import c_parser, c_ast, parse_file

# Std libs
import sys

def manage_args():

	if (len(sys.argv) == 1):
		sys.argv.append("-h")

	args_manager = ArgsManager()

	args_manager.load_args()
	args_manager.parse()

	rtn_code = args_manager.check()

	if (rtn_code != Meta.ok_code):
		return rtn_code

	return Meta.ok_code

def parse_c_file():
	file_path = ArgsManager.args.file
	ast = None

	# parse_file (__init__.py) returns an AST or ParseError if doesn't parse successfully
	try:
		ast = parse_file(file_path, use_cpp = False)
	except ParseError:
		eprint(f'Error: could not parse file "{file_path}".')

		return [Error.error_parse_parse, ast]
	except FileNotFoundError:
		eprint(f'Error: file "{file_path}" not found.')

		return [Error.error_file_not_found, ast]
	except:
		eprint('Error: unknown error while parsing file.')

		return [Error.error_unknown, ast]

	return [Meta.ok_code, ast]

def main():
	print(f"Welcome to {Meta.name} - Version {Meta.version}\n")

	# Parse and check args
	rtn_code = manage_args()

	if (rtn_code != 0):
		return rtn_code
	
	# TODO Parse and check rules
	
	# Parse C file
	rtn = parse_c_file()
	rtn_code = rtn[0]
	ast = rtn[1]

	if (rtn_code != 0):
		return rtn_code

	# TODO Load modules
	# Through mod_loader we can get modules, but it is not necessary (sys.modules)
	mod_loader = ModulesImporter('constants', 'args_manager', 'unexistent_asdasdasd', 'unexistent_asdasdasd', 'boam_function_match')
	mod_loader.load()
	#mod_loader.get_module('boam_function_match').first_boam()

	# Test
	function_match = mod_loader.get_module('boam_function_match')

	if (function_match != None):
		function_match = function_match.BOAM_function_match('my args')

	# End test

	# TODO Load rules

	return Meta.ok_code

if __name__ == '__main__':
	return_code = main()
	exit(return_code)