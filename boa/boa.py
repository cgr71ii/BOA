
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
		eprint(f"Error: could not parse file '{file_path}'.")

		return [Error.error_parse_parse, ast]
	except FileNotFoundError:
		eprint(f"Error: file '{file_path}' not found.")

		return [Error.error_file_not_found, ast]
	except:
		eprint("Error: unknown error while parsing file.")

		return [Error.error_unknown, ast]

	return [Meta.ok_code, ast]

def load_modules(user_modules):
	mandatory_modules = [Meta.abstract_module_class_name]
	modules = mandatory_modules + user_modules

	# Through mod_loader we can get modules, but it is not necessary (sys.modules)
	mod_loader = ModulesImporter(modules)
	mod_loader.load()

	# Check if mandatory or user modules failed
	mandatory_module_failed = False
	user_module_failed = False
	rtn_code = Meta.ok_code

	# Checking mandatory modules
	for mandatory_module in mandatory_modules:
		if (mod_loader.is_module_loaded(mandatory_module) == False):
			mandatory_module_failed = True
			break
	
	# Checking user modules
	for user_module in user_modules:
		if (mod_loader.is_module_loaded(user_module) == False):
			user_module_failed = True
			break

	if (mandatory_module_failed and user_module_failed):
		rtn_code = Error.error_module_some_mandatory_and_user_failed
	elif (mandatory_module_failed):
		rtn_code = Error.error_module_some_mandatory_failed
	elif (user_module_failed):
		rtn_code = Error.error_module_some_user_failed
		
	return [rtn_code, mod_loader]

def main():
	print(f"Welcome to {Meta.name} - Version {Meta.version}\n")

	# Parse and check args
	rtn_code = manage_args()

	if (rtn_code != Meta.ok_code):
		return rtn_code
	
	# TODO Parse and check rules (XML)
	modules = []
	classes = []

	# Parse XML ...
	# Append ...

	# FIXME Tmp for testing
	modules = ["boam_function_match"]
	classes = ["BOAM_function_match"]

	if (len(modules) != len(classes)):
		eprint(f"Error: modules length ({len(modules)}) is not equal to classes length ({len(classes)}).")
		return Error.error_rules_modules_classes_neq_length
	
	# Parse C file
	rtn = parse_c_file()
	rtn_code = rtn[0]
	ast = rtn[1]

	if (rtn_code != Meta.ok_code):
		return rtn_code

	# Load modules
	rtn = load_modules(modules)	
	rtn_code = rtn[0]
	mod_loader = rtn[1]
	fail_if_some_user_module_failed = True	# TODO BOA arg

	if (rtn_code == Error.error_module_some_user_failed and
		fail_if_some_user_module_failed):
		return rtn_code
	if (rtn_code != Meta.ok_code and
		rtn_code != Error.error_module_some_user_failed):
		return rtn_code

	# TODO Load rules and instances with that rules as args

	# Test
	index = 0
	while (index < len(modules)):
		function_match = mod_loader.get_instance(modules[index], classes[index])

		if (function_match != None):
			function_match = function_match("my args")

		index += 1

	# End test

	return Meta.ok_code

if __name__ == "__main__":
	rtn_code = main()

	print(f"Exit status: {rtn_code}")

	exit(rtn_code)