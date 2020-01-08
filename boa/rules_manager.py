
# Own libs
from constants import Meta
from constants import Error
from util import eprint
from util import is_key_in_dict

# Std libs
import os
import copy

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
    
    # This method will be called by 'check_rules_arg' with the 
    #   purpose of get recursively the args from the rules file
    def check_rules_arg_recursive(self, arg, element, father, arg_reference, args_reference, save_args, sort_args):
        # Make a list if it is not
        _element = arg[element]
        if (type(_element) is not list):
            _element = [_element]

        for __element in _element:
            # Necessary deep copy of 'arg_reference' to avoid 'same reference' problems
            #_arg_reference = arg_reference
            _arg_reference = None

            if (arg_reference != None):
                _arg_reference = copy.deepcopy(arg_reference)
            elif (element == "element"):
                if (not is_key_in_dict(__element, "@value")):
                    return False
                
                _arg_reference = __element["@value"]
            else:
                # It should not happen
                return False

            if (father == "dict"):
                if (not is_key_in_dict(__element, "@name")):
                    return False
                
                name = __element["@name"]
                args_reference[name] = _arg_reference
            elif (father == "list"):
                args_reference.append(_arg_reference)
            else:
                # It should not happen
                return False

            # Recursive checking
            if (not self.check_rules_arg(__element, element, father, save_args, _arg_reference, sort_args)):
                return False

    def get_index_from_tuple_with_dict_flavour(self, t, value, key_position = 0):
        index = 0

        if (type(t) is not list):
            t = [t]

        for i in t:
            if (i[key_position] == value):
                return index

            index += 1

        return None

    def check_rules_arg(self, arg, father, grandpa, save_args, args_reference, sort_args):
        _arg = arg

        if (father == "args" and save_args):
            if (type(args_reference) is not dict or len(args_reference) != 0):
                eprint(f"Error: check_rules_arg have to get an empty 'dict' as first args reference.")
                return False

        if (_arg == None):
            return True
        if (type(_arg) is not list):
            _arg = [_arg]

        sort_args_calling_queue = {}
        sort_args_arg_list = None
        index = 0

        for __arg in _arg:
            #print(f"grandpa:father -> {grandpa}:{father}")
            #print(f"args_reference: {args_reference}")
            #print(f"type(__arg): {type(__arg)}")
            #print(f"len(__arg): {len(__arg)}")
            #print(f"__arg: {__arg}")
            #print(f"__arg")

            if (sort_args and sort_args_arg_list == None):
                sort_args_arg_list = list(__arg.items())

            # 1st checking
            if (father == "args" and len(__arg) != 1):
                return False
            elif (father == "args"):
                # Mandatory and unique element as first arg
                if (is_key_in_dict(__arg, "dict")):
                    # Recursive checking
                    return self.check_rules_arg(__arg["dict"], "dict", father, save_args, args_reference, sort_args)
                else:
                    return False

            # nth checking
            valid = 0

            # Dict (optional)
            if (is_key_in_dict(__arg, "dict")):
                valid += 1
                arg_reference = {}
                sort_args_index = None

                if (sort_args):
                    sort_args_index = self.get_index_from_tuple_with_dict_flavour(sort_args_arg_list, "dict")

                if (sort_args_index != None):
                    # Sorting calls
                    sort_args_calling_queue[str(sort_args_index)] = "dict"
                    sort_args_calling_queue[f"{str(sort_args_index)}.arg_reference"] = arg_reference
                else:
                    if (sort_args_index == None and sort_args):
                        eprint(f"Warning: args sorting failed. The result might be disordered.")

                    # Recursive checking
                    self.check_rules_arg_recursive(__arg, "dict", father, arg_reference, args_reference, save_args, sort_args)

            # List (optional)
            if (is_key_in_dict(__arg, "list")):
                #valid += 1
                #arg_reference = []
                #
                # If we want to save the args, we need a call for each args processing in case of a list (>1 list at same deepness)
                # However, in the case we need not, the same number of calls will be processed in the next call, so we make the job now and we avoid to complex the logic
                #if (type(__arg["list"]) is list and save_args):
                #    for _list in __arg["list"]:
                #       # Recursive checking
                #       if (not self.check_rules_arg(_list, "list", father, save_args, args_reference)):
                #           return False
                # Avoid to complex the logic:
                #else:
                #    # Recursive checking
                #    if (not self.check_rules_arg(__arg["list"], "list", father, save_args, args_reference)):
                #        return False
                #
                # Make a list if it is not
                #_list = __arg["list"]
                #if (type(__arg["list"]) is not list):
                #    _list = [_list]
                #
                #for __list in _list:
                #    arg_reference = []
                #
                #    if (father == "dict"):
                #        if (not is_key_in_dict(__list, "@name")):
                #            return False
                #        
                #        name = __list["@name"]
                #        args_reference[name] = arg_reference
                #    elif (father == "list"):
                #        args_reference.append(arg_reference)
                #    else:
                #        # It should not happen
                #        return False
                #
                #    # Recursive checking
                #    if (not self.check_rules_arg(__list, "list", father, save_args, arg_reference)):
                #        return False

                valid += 1
                arg_reference = []
                sort_args_index = None

                if (sort_args):
                    sort_args_index = self.get_index_from_tuple_with_dict_flavour(sort_args_arg_list, "list")

                if (sort_args_index != None):
                    # Sorting calls
                    sort_args_calling_queue[str(sort_args_index)] = "list"
                    sort_args_calling_queue[f"{str(sort_args_index)}.arg_reference"] = arg_reference
                else:
                    if (sort_args_index == None and sort_args):
                        eprint(f"Warning: args sorting failed. The result might be disordered.")
                        
                    # Recursive checking
                    self.check_rules_arg_recursive(__arg, "list", father, arg_reference, args_reference, save_args, sort_args)

            # Element (optional)
            if (is_key_in_dict(__arg, "element")):
                valid += 1
                arg_reference = None
                sort_args_index = None

                if (sort_args):
                    sort_args_index = self.get_index_from_tuple_with_dict_flavour(sort_args_arg_list, "element")

                if (sort_args_index != None):
                    # Sorting calls
                    sort_args_calling_queue[str(sort_args_index)] = "element"
                    sort_args_calling_queue[f"{str(sort_args_index)}.arg_reference"] = arg_reference
                else:
                    if (sort_args_index == None and sort_args):
                        eprint(f"Warning: args sorting failed. The result might be disordered.")

                    # Recursive checking
                    self.check_rules_arg_recursive(__arg, "element", father, arg_reference, args_reference, save_args, sort_args)

            # If sort_args, make the calls now orderly
            if (sort_args and sort_args_arg_list != None):
                for i in range(len(sort_args_arg_list)):
                    if (is_key_in_dict(sort_args_calling_queue, str(i))):
                        element = sort_args_calling_queue[str(i)]
                        arg_reference = sort_args_calling_queue[f"{str(i)}.arg_reference"]

                        self.check_rules_arg_recursive(__arg, element, father, arg_reference, args_reference, save_args, sort_args)


            # Attribute checking
            # Elements inside a "dict" has to have the "name" attribute
            if (grandpa == "dict"):
                # Mandatory "name" attribute
                if (is_key_in_dict(__arg, "@name")):
                    __arg["@name"]
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
                    __arg["@value"]
                    valid += 1
                else:
                    return False

            if (valid != len(__arg)):
                # Argument defined but not all are valid
                return False
            elif (valid == 0 and father != "args"):
                # No valid arguments defined inside the tag
                return False

            index += 1

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
                args_sorting_defined_test = False

                if (len(module) == 4):
                    args_sorting_defined_test = True
                elif (len(module) != 3):
                    raise Exception("boa_rules.modules.module has not the expected #elements")

                module_name = module["module_name"]
                class_name = module["class_name"]
                
                args = module["args"]
                sort_args = False

                try:
                    if (module["args_sorting"].lower() == "true"):
                        sort_args = True
                except:
                    if (args_sorting_defined_test):
                        raise Exception("boa_rules.modules.module has not the expected #elements")

                if (type(args) is not list):
                    args = [args]

                arg_reference = {}

                if (save_args and self.args == None):
                    # Initialize args to dict to work with the reference
                    self.args = {}

                for arg in args:
                    if (not self.check_rules_arg(arg, "args", "module", save_args, arg_reference, sort_args)):
                        if (save_args):
                            # Reset the args because the args checking failed
                            self.args = None

                        raise Exception("boa_rules.modules.module.args is not correct")

                if (save_args and not self.set_args(f"{module_name}.{class_name}", arg_reference)):
                    # Reset the args because we could not set the args
                    self.args = None
                    raise Exception("boa_rules.modules.module is not correct (f'{module's name}.{class's name}' already set?)")

        except Exception as e:
            eprint(f"Warning: rules did not pass the checking: {e}.")
            return False

        return True

    def get_rules(self, path = None, list_type = False):
        if (path == None):
            return self.rules
        else:
            rules = self.rules

            for p in path.split("."):
                try:
                    rules = rules[p]
                except Exception as e:
                    eprint(f"Error: could not get the rules concrete rules: {e}. Returning all the rules.")

                    return self.rules

            if (list_type):
                if (type(rules) is not list):
                    rules = [rules]

            return rules

    def set_args(self, module, arg):
        if (self.args == None):
            self.args = {}
        elif (type(self.args) is not dict):
            eprint("Error: args type is not a dict.")
            return False
        elif (is_key_in_dict(self.args, module)):
            eprint(f"Warning: args for module '{module}' already exists. Overwriting it.")

        try:
            self.args[module] = arg

            return True
        except Exception as e:
            eprint(f"Error: {e}.")

            return False

    def get_args(self, module = None):
        if (module == None):
            return self.args

        if (self.args != None and
            type(self.args) is dict and
            is_key_in_dict(self.args, module)):
            return self.args[module]
        else:
            eprint(f"Warning: could not get the args for module '{module}'.")
            return None