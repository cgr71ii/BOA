
# Own libs
from constants import Meta
from constants import Error
from args_manager import ArgsManager
from exceptions import ParseError
from util import eprint

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

	# parse_file (__init__.py) returns an AST or ParseError if doesn't parse successfully
	try:
		ast = parse_file(file_path, use_cpp = False)
		ast.show()
	except ParseError:
		eprint(f'Error: could not parse file "{file_path}".')

		return Error.error_parse_parse
	except FileNotFoundError:
		eprint(f'Error: file "{file_path}" not found.')

		return Error.error_file_not_found
	except:
		eprint('Error: unknown error while parsing file.')

		return Error.error_unknown

	return Meta.ok_code



def main():
	print(f"Welcome to {Meta.name} - Version {Meta.version}\n")

	rtn_code = manage_args()

	if (rtn_code != 0):
		return rtn_code
	
	rtn_code = parse_c_file()

	return Meta.ok_code

if __name__ == '__main__':
	return_code = main()
	exit(return_code)