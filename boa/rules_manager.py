
# Own libs
from constants import Meta
from constants import Error
from util import eprint
from util import is_key_in_dict

# Std libs
import os

# 3rd libs
import xmltodict

class RulesManager:

    def __init__(self, rules_file):
        self.rules_file_path = rules_file
        self.file = None
        self.xml = None
        self.xml_str = None
        self.rules = None
        self.args = None

    def open(self):
        if (not os.path.exists(self.rules_file_path)):
            eprint(f"Error: file '{self.rules_file_path}' does not exist.")
            return Error.error_file_not_found

        try:
            self.file = open(self.rules_file_path, "r")
        except Exception as e:
            eprint(f"Error: {e}.")
            return Error.error_rules_could_not_open_file

        return Meta.ok_code
        
    def read(self):
        try:
            self.xml = self.file.readlines()
            self.xml_str = ''

            for line in self.xml:
                self.xml_str += line.replace("\n", "")

            self.rules = xmltodict.parse(self.xml_str)
        except Exception as e:
            eprint(f"Error: {e}.")
            return Error.error_rules_could_not_read_file
        return Meta.ok_code
    
    def close(self):
        try:
            self.file.close()
        except Exception as e:
            eprint(f"Error: {e}.")
            return Error.error_rules_could_not_close_file

        return Meta.ok_code

    def check_rules_arg(self, arg, father, grandpa, save_args, args_reference):
        _arg = arg

        if (self.args == None and save_args):
            # Initialize args
            self.args = {}

        if (_arg == None):
            return True
        if (type(_arg) is not list):
            _arg = [_arg]

        for __arg in _arg:
            # 1st checking
            if (father == "args" and len(__arg) != 1):
                return False
            elif (father == "args"):
                # Mandatory and unique element as first arg
                if (is_key_in_dict(__arg, "dict")):
                    # Recursive checking
                    # TODO args_reference not finished
                    return self.check_rules_arg(__arg["dict"], "dict", father, save_args)
                else:
                    return False

            # nth checking
            valid = 0

            # Dict (optional)
            if (is_key_in_dict(__arg, "dict")):
                valid += 1

                # Recursive checking
                if (not self.check_rules_arg(__arg["dict"], "dict", father, save_args)):
                    return False

            # List (optional)
            if (is_key_in_dict(__arg, "list")):
                valid += 1

                # Recursive checking
                if (not self.check_rules_arg(__arg["list"], "list", father, save_args)):
                    return False

            # Element (optional)
            if (is_key_in_dict(__arg, "element")):
                valid += 1

                # Recursive checking
                if (not self.check_rules_arg(__arg["element"], "element", father, save_args)):
                    return False
            
            name = None
            value = None

            # Attribute checking
            # Elements inside a "dict" has to have the "name" attribute
            if (grandpa == "dict"):
                # Mandatory "name" attribute
                if (is_key_in_dict(__arg, "@name")):
                    name = __arg["@name"]
                    valid += 1
                else:
                    return False
            # "element" attributes
            if (father == "element"):
                if (grandpa != "dict" and grandpa != "list"):
                    # An "element" has to be inside a dict or a list
                    return False
                # Mandatory "value" attribute
                elif (is_key_in_dict(__arg, "@value")):
                    value = __arg["@value"]
                    valid += 1
                else:
                    return False

            if (valid != len(__arg)):
                # Argument defined but not all are valid
                return False
            elif (valid == 0 and father != "args"):
                # No valid arguments defined inside the tag
                return False

        return True

    def check_rules(self, save_args):
        if (self.rules == None):
            return False

        try:
            self.rules["boa_rules"]

            if (len(self.rules["boa_rules"]) != 2):
                raise Exception("boa_rules has not the expected #elements")

            self.rules["boa_rules"]["parser"]

            if (len(self.rules["boa_rules"]["parser"]) != 5):
                raise Exception("boa_rules.parser has not the expected #elements")

            self.rules["boa_rules"]["parser"]["name"]
            self.rules["boa_rules"]["parser"]["lang_objective"]
            self.rules["boa_rules"]["parser"]["module_name"]
            self.rules["boa_rules"]["parser"]["class_name"]
            self.rules["boa_rules"]["parser"]["callback"]
            self.rules["boa_rules"]["parser"]["callback"]["method"]

            if (len(self.rules["boa_rules"]["parser"]["callback"]) != 1):
                raise Exception("boa_rules.parser.callback has not the expected #elements")

            methods = self.rules["boa_rules"]["parser"]["callback"]["method"]

            if (type(methods) is not list):
                methods = [methods]

            for method in methods:
                if (len(method) != 2):
                    raise Exception("boa_rules.parser.callback.method has not the expected #elements")

                method["@name"]
                method["@callback"]

            self.rules["boa_rules"]["modules"]

            if (len(self.rules["boa_rules"]["modules"]) != 1):
                raise Exception("boa_rules.modules has not the expected #elements")

            modules = self.rules["boa_rules"]["modules"]["module"]

            if (type(modules) is not list):
                modules = [modules]
            
            for module in modules:
                if (len(module) != 3):
                    raise Exception("boa_rules.modules.module has not the expected #elements")

                module["module_name"]
                module["class_name"]
                
                args = module["args"]

                if (type(args) is not list):
                    args = [args]

                for arg in args:
                    if (not self.check_rules_arg(arg, "args", "module", save_args, self.args)):
                        if (save_args):
                            # Reset the args because the args checking failed
                            self.args = None

                        raise Exception("boa_rules.modules.module.args is not correct")

        except Exception as e:
            eprint(f"Warning: rules did not pass the checking: {e}.")
            return False

        return True

    def get_rules(self):
        return self.rules

    def get_args(self):
        return self.args