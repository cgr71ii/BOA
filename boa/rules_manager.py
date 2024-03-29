
"""Rules Manager file.

This file contains the necessary methods in the
RulesManager class to load, check and process the
rules file.

The file rules should contain all the necessary
information to execute a concrete analysis.
However, multiple and independent analysis
might be executed.

Each rules file should contain a complete analysis
technique defined. If multiple modules are being used,
this should be to reach the goal of execute a complex
but concrete analysis.
"""

# Std libs
import os
import re
import copy
import logging

# 3rd libs
import xmltodict

# Own libs
from constants import Meta, Error, Other, Regex
from utils import is_key_in_dict, get_index_if_match_element_in_tuples
from exceptions import BOARulesUnexpectedFormat, BOARulesIncomplete, BOARulesError

class RulesManager:
    """RulesManager class.

    This class defines the necessary methods to load,
    check and process the rules from a file.
    """

    def __init__(self, rules_file):
        """It initializes the necessary variables.

        Arguments:
            rules_file (str): path to the rules file.
        """
        self.rules_file_path = rules_file
        self.file = None
        self.xml = None
        self.xml_str = None
        self.rules = None
        self.args = None
        self.dependencies = None
        self.report_args = None
        self.runner_args = {"inputs": None, "fails": None}

    def open(self):
        """It opens the rules file, checking if exists first.

        Returns:
            int: status code
        """
        if not os.path.exists(self.rules_file_path):
            logging.error("file '%s' does not exist", self.rules_file_path)
            return Error.error_file_not_found

        try:
            self.file = open(self.rules_file_path, "r")
        except Exception as e:
            logging.error("RulesManager: %s", str(e))
            return Error.error_rules_could_not_open_file

        return Meta.ok_code

    def read(self):
        """It reads the rules file and saves the necessary information.

        Returns:
            int: status code
        """
        try:
            self.xml = self.file.readlines()
            self.xml_str = ''

            for line in self.xml:
                self.xml_str += line.replace("\n", "")

            self.rules = xmltodict.parse(self.xml_str)
        except Exception as e:
            logging.error("RulesManager: %s", str(e))
            return Error.error_rules_could_not_read_file
        return Meta.ok_code

    def close(self):
        """It closes the rules file to release the resource.

        Returns:
            int: status code
        """
        try:
            self.file.close()
        except Exception as e:
            logging.error("RulesManager: %s", str(e))
            return Error.error_rules_could_not_close_file

        return Meta.ok_code

    # This method will be called by 'check_rules_arg' with the
    #   purpose of get recursively the args from the rules file
    def check_rules_arg_recursive(self, arg, element, father, arg_reference,
                                  args_reference, save_args, sort_args):
        """This method is used by *check_rules_arg* method.

        This method wraps the common behaviour for saving the arguments
        references and makes the necessary recursive calls for each
        element. Moreover, it checks that the arguments, depending on
        the concrete element, contains the expected attributes (e.g.
        a dictionary's element contains a name attribute).

        For details, check *check_rules_arg* documentation.

        Arguments:
            arg: current arg which is being checked (processed recursively).
            element (str): the concrete type of element which is being given.
                It may be "dict", "list" or *None*. If *None*, it indicates
                that the element is a "element".
            father (str): arg's father.
            arg_reference: the new reference which will be appended to
                *args_reference*.
            args_reference: if *save_args* is *True*, this is the concrete
                arg reference which it changes while recursion is being
                processed. It changes the reference from call to call to
                save the concrete args here.
            save_args (bool): it indicates if you want to save the args
                while they are being checked.
            sort_args (bool): it indicates if you want a partial sorting
                when you mix different type of elements.

        Returns:
            bool: true if the arguments are valid; false otherwise
        """
        # Make a list if it is not
        _element = arg[element]
        if not isinstance(_element, list):
            _element = [_element]

        for __element in _element:
            # Necessary deep copy of 'arg_reference' to avoid 'same reference' problems
            #_arg_reference = arg_reference
            _arg_reference = None

            if arg_reference is not None:
                _arg_reference = copy.deepcopy(arg_reference)
            # When "arg_reference" is None it indicates that "element" should contain
            #  the value "element"
            elif element == "element":
                if not is_key_in_dict(__element, "@value"):
                    return False

                _arg_reference = __element["@value"]
            else:
                # It should not happen
                return False

            if father == "dict":
                # If the father is a "dict", it should contain a "name" attr
                if not is_key_in_dict(__element, "@name"):
                    return False

                name = __element["@name"]
                args_reference[name] = _arg_reference
            elif father == "list":
                args_reference.append(_arg_reference)
            else:
                # It should not happen
                return False

            # Recursive checking
            if not self.check_rules_arg(__element, element, father, save_args,
                                        _arg_reference, sort_args):
                return False

        return True

    def check_rules_arg(self, arg, father, grandpa, save_args, args_reference, sort_args):
        """It checks if the <args> elements are correct recursevely.

        This method works recursively making the following calls:\n
        * check_rules_arg -> check_rules_arg_recursive
        * check_rules_arg_recursive -> check_rules_arg

        What this method makes is checking if the <args> elements
        which are inside are correct and, optionally, save them to
        being used by the target module which is specified in the
        rules file.

        If the arguments want to be saved, the order may not be the
        expected. If the <args> elements are mixed, the predefined
        order will be:\n
        1. Dictionaries\n
        2. Lists\n
        3. Elements\n
        If you want to have the elements in the correct order
        which you wrote, you can avoid mixing the elements
        or use the *sort_args* argument to have a partial sorting
        (this partial sorting makes worse the performance while
        checking). We say "partial" because the result will be
        that if you are mixing elements, all them will be grouped
        and will appear in the order which the first type of
        element appeared.

        Arguments:
            arg: current arg which is being checked (processed recursively).
            father (str): arg's father.
            grandpa (str): arg's grandpa; father's father.
            save_args (bool): it indicates if you want to save the args
                while they are being checked.
            args_reference: if *save_args* is *True*, this is the concrete
                arg reference which it changes while recursion is being
                processed. It changes the reference from call to call to
                save the concrete args here.
            sort_args (bool): it indicates if you want a partial sorting
                when you mix different type of elements.

        Example:
            <args>\n
            \t<dict>\n
            \t\t<list name="l1"></list>\n
            \t\t<dict name="d"></dict>\n
            \t\t<element name="e" value="v" />\n
            \t\t<list name="l2"></list>\n
            \t</dict>\n
            </args>\n

            Unsorted result: {"d": {}, "l1": [], "l2": [], "e": "v"}\n
            Partial sorted result: {"l1": [], "l2": [], "d": {}, "e": "v"}

        Returns:
            bool: true if the arguments are valid; false otherwise
        """
        _arg = arg

        if (father == "args" and save_args):
            if (not isinstance(args_reference, dict) or len(args_reference) != 0):
                logging.error("check_rules_arg have to get an empty 'dict' as first args reference")
                return False

        if _arg is None:
            return True
        if not isinstance(_arg, list):
            _arg = [_arg]

        sort_args_calling_queue = {}
        sort_args_arg_list = None
        index = 0

        for __arg in _arg:
            if (sort_args and sort_args_arg_list is None):
                sort_args_arg_list = list(__arg.items())

            # 1st checking
            if (father == "args" and len(__arg) != 1):
                return False
            if father == "args":
                # Mandatory and unique element as first arg
                if is_key_in_dict(__arg, "dict"):
                    # Recursive checking
                    return self.check_rules_arg(__arg["dict"], "dict", father,
                                                save_args, args_reference, sort_args)

                return False

            # nth checking
            valid = 0

            # Dict (optional)
            if is_key_in_dict(__arg, "dict"):
                valid += 1
                arg_reference = {}
                sort_args_index = None

                if sort_args:
                    sort_args_index = get_index_if_match_element_in_tuples(sort_args_arg_list,
                                                                           "dict")

                if sort_args_index is not None:
                    # Sorting calls
                    sort_args_calling_queue[str(sort_args_index)] = "dict"
                    sort_args_calling_queue[f"{str(sort_args_index)}.arg_reference"] = arg_reference
                else:
                    if (sort_args_index is None and sort_args):
                        logging.warning("args sorting failed: the result might be disordered")

                    # Recursive checking
                    self.check_rules_arg_recursive(__arg, "dict", father, arg_reference,
                                                   args_reference, save_args, sort_args)

            # List (optional)
            if is_key_in_dict(__arg, "list"):
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

                if sort_args:
                    sort_args_index = get_index_if_match_element_in_tuples(sort_args_arg_list,
                                                                           "list")

                if sort_args_index is not None:
                    # Sorting calls
                    sort_args_calling_queue[str(sort_args_index)] = "list"
                    sort_args_calling_queue[f"{str(sort_args_index)}.arg_reference"] = arg_reference
                else:
                    if (sort_args_index is None and sort_args):
                        logging.warning("args sorting failed: the result might be disordered")

                    # Recursive checking
                    self.check_rules_arg_recursive(__arg, "list", father, arg_reference,
                                                   args_reference, save_args, sort_args)

            # Element (optional)
            if is_key_in_dict(__arg, "element"):
                valid += 1
                arg_reference = None
                sort_args_index = None

                if sort_args:
                    sort_args_index = get_index_if_match_element_in_tuples(sort_args_arg_list,
                                                                           "element")

                if sort_args_index is not None:
                    # Sorting calls
                    sort_args_calling_queue[str(sort_args_index)] = "element"
                    sort_args_calling_queue[f"{str(sort_args_index)}.arg_reference"] = arg_reference
                else:
                    if (sort_args_index is None and sort_args):
                        logging.warning("args sorting failed: the result might be disordered.")

                    # Recursive checking
                    self.check_rules_arg_recursive(__arg, "element", father, arg_reference,
                                                   args_reference, save_args, sort_args)

            # If sort_args, make the calls now orderly
            if (sort_args and sort_args_arg_list is not None):
                for i in range(len(sort_args_arg_list)):
                    if is_key_in_dict(sort_args_calling_queue, str(i)):
                        element = sort_args_calling_queue[str(i)]
                        arg_reference = sort_args_calling_queue[f"{str(i)}.arg_reference"]

                        self.check_rules_arg_recursive(__arg, element, father, arg_reference,
                                                       args_reference, save_args, sort_args)


            # Attribute checking
            # Elements inside a "dict" has to have the "name" attribute
            if grandpa == "dict":
                # Mandatory "name" attribute
                if is_key_in_dict(__arg, "@name"):
                    #__arg["@name"]
                    valid += 1
                else:
                    return False
            # "element" attributes
            if father == "element":
                if (grandpa not in ["dict", "list"]):
                    # An "element" has to be inside a dict or a list
                    return False
                # Mandatory "value" attribute
                if is_key_in_dict(__arg, "@value"):
                    #__arg["@value"]
                    valid += 1
                else:
                    return False

            if valid != len(__arg):
                # Argument defined but not all are valid
                return False
            if (valid == 0 and father != "args"):
                # No valid arguments defined inside the tag
                return False

            index += 1

        return True

    def check_rules_init(self):
        """It makes the initial checks.

        Raises:
            BOARulesIncomplete: when the number of expected
                mandatory rules does not match with the actual
                number of rules or when a concrete rule is not
                found.
        """
        mandatory_rules = ("boa_rules", "boa_rules.@analysis", "boa_rules.runners",
                           "boa_rules.modules", "boa_rules.report")
        optional_rules = ("boa_rules.env_vars",)

        # Check mandatory rules
        for rule in mandatory_rules:
            is_key_in_dict(self.rules, rule, split=".",
                           raise_exception=BOARulesIncomplete,
                           exception_args=f"'{rule}'")

        # Check optional rules
        for rule in optional_rules:
            if not is_key_in_dict(self.rules, rule, split="."):
                # Set None to optional rules which were not set
                keys = rule.split(".")
                value = self.rules

                for key in keys:
                    try:
                        value = value[key]
                    except KeyError:
                        value[key] = None

        # Check if the number of rules are the expected
        if len(self.rules["boa_rules"]) != len(mandatory_rules) - 1 + len(optional_rules):
            raise BOARulesIncomplete("'boa_rules' has not the expected #elements")


        # Check if the analysis attribute contains a valid value
        if self.rules["boa_rules"]["@analysis"] not in Other.other_valid_analysis:
            raise BOARulesUnexpectedFormat("unexpected value in 'boa_rules.@analysis': "
                                           f"valid values are: {str(Other.other_valid_analysis)[1:-1]}")

    def check_rules_parser(self):
        """It makes the checks relative to the parser.

        Raises:
            BOARulesIncomplete: when the number of expected
                mandatory rules does not match with the actual
                number of rules or when a concrete rule is not
                found.
        """
        # Check if there are the expected #elements in the parser element
        if len(self.rules["boa_rules"]["runners"]["parser"]) != 5:
            raise BOARulesIncomplete("'boa_rules.runners.parser' has not the expected #elements")

        # Check if the expected elements are in the parser element
        is_key_in_dict(self.rules, "boa_rules.runners.parser.name", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.runners.parser.name'")
        is_key_in_dict(self.rules, "boa_rules.runners.parser.lang_objective", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.runners.parser.lang_objective'")
        is_key_in_dict(self.rules, "boa_rules.runners.parser.module_name", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.runners.parser.module_name'")
        is_key_in_dict(self.rules, "boa_rules.runners.parser.class_name", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.runners.parser.class_name'")
        is_key_in_dict(self.rules, "boa_rules.runners.parser.callback", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.runners.parser.callback'")
        is_key_in_dict(self.rules, "boa_rules.runners.parser.callback.method", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.runners.parser.callback.method'")

        # Check concrete restrictions about the elements of the parser element
        if len(self.rules["boa_rules"]["runners"]["parser"]["callback"]) != 1:
            raise BOARulesIncomplete("'boa_rules.runners.parser.callback' has not"
                                     " the expected #elements")

        is_key_in_dict(self.rules, "boa_rules.runners.parser.callback.method", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.runners.parser.callback.method'")

        methods = self.rules["boa_rules"]["runners"]["parser"]["callback"]["method"]

        if not isinstance(methods, list):
            methods = [methods]

        # Check parser callback elements
        for method in methods:
            if len(method) != 2:
                raise BOARulesIncomplete("'boa_rules.runners.parser.callback.method'"
                                         " has not the expected #elements")

            is_key_in_dict(method, "@name",
                           raise_exception=BOARulesIncomplete,
                           exception_args="'boa_rules.runners.parser.callback.method@name'")
            is_key_in_dict(method, "@callback",
                           raise_exception=BOARulesIncomplete,
                           exception_args="'boa_rules.runners.parser.callback.method@callback'")

    def check_rules_dynamic_analysis_runner(self, save_args, runner_module):
        """It makes the checks relative to the runner modules which
        are used in the dynamic analysis.

        Arguments:
            save_args (bool): it indicates that the arguments
                have to be saved while they are being checked.
            runner_module (str): runner which is going to be processed
                in order to check the rules.

        Raises:
            BOARulesIncomplete: when the number of expected
                mandatory rules does not match with the actual
                number of rules or when a concrete rule is not
                found.
            BOARulesError: when a semantic rule is broken.
                You have to follow the rules documentation to
                avoid this exception.
            KeyError: if *runner_module* is not an expected runner.
        """
        # Check if there are the expected #elements in the modules element
        runner = self.rules["boa_rules"]["runners"][runner_module]
        total_tags_found = 0

        if is_key_in_dict(runner, "module_name"):
            total_tags_found += 1

        if is_key_in_dict(runner, "class_name"):
            total_tags_found += 1

        if is_key_in_dict(runner, "args_sorting"):
            total_tags_found += 1

        if is_key_in_dict(runner, "args"):
            total_tags_found += 1

        if len(runner) != total_tags_found:
            raise BOARulesIncomplete(f"'boa_rules.runners.{runner_module}' has not the expected #elements")

        # Args checking
        arg_reference = {}

        try:
            arg_reference = self.check_rules_arg_high_level(runner,
                                                            runner_module,
                                                            f"boa_rules.runners.{runner_module}",
                                                            save_args)
        except BOARulesError as e:
            raise BOARulesError(f"rules error in 'boa_rules.runners.{runner_module}'") from e

        # Set the report args
        self.runner_args[runner_module] = arg_reference

    def get_runner_args(self, runner_module):
        """It returns the args of a runner module.

        Arguments:
            runner_module (str): key of *self.runner_args* which is where
                the parameters are stored.

        Returns:
            dict: args if they exist, but empty dict and logging warning
            if does not
        """
        if runner_module in self.runner_args:
            if not isinstance(self.runner_args[runner_module], dict):
                logging.warning("runner module is not a dict (returning empty dict): %s", str(type(self.runner_args[runner_module])))

                return {}
            else:
                return self.runner_args[runner_module]

        logging.warning("runner module is not defined (returning empty dict): %s", runner_module)

        return {}

    def check_rules_arg_high_level(self, dict_tag, parent_tag_name, tag_prefix, save_args):
        """This is the method that should be invoked when
        you want to check, and optionally parse, the arguments
        from the rules file.

        Raises:
            BOARulesIncomplete: when the number of expected
                mandatory rules does not match with the actual
                number of rules or when a concrete rule is not
                found.
            BOARulesUnexpectedFormat: when the format of a rule
                is not the expected.
            BOARulesError: when an non-specific error happens.
        """
        is_key_in_dict(dict_tag, "args",
                       raise_exception=BOARulesIncomplete,
                       exception_args=f"'{tag_prefix}.args'")

        args = dict_tag["args"]
        sort_args = False

        if is_key_in_dict(dict_tag, "args_sorting"):
            if dict_tag["args_sorting"].lower() == "true":
                sort_args = True
            elif dict_tag["args_sorting"].lower() != "false":
                raise BOARulesUnexpectedFormat(f"'{tag_prefix}.args_sorting' has not"
                                               " the expected format (allowed values"
                                               " are 'true' and 'false')")

        if not isinstance(args, list):
            args = [args]

        arg_reference = {}

        # Args processing
        for arg in args:
            if not self.check_rules_arg(arg, "args", parent_tag_name, save_args,
                                        arg_reference, sort_args):
                raise BOARulesError(f"'{tag_prefix}.args' is not correct")

        return arg_reference

    def check_rules_modules(self, save_args):
        """It makes the checks relative to the modules.

        Arguments:
            save_args (bool): it indicates that the arguments
                have to be saved while they are being checked.

        Raises:
            BOARulesIncomplete: when the number of expected
                mandatory rules does not match with the actual
                number of rules or when a concrete rule is not
                found.
            BOARulesUnexpectedFormat: when the format of a rule
                is not the expected.
            BOARulesError: when an non-specific error happens.
        """
        # Check if there are the expected #elements in the modules element
        if len(self.rules["boa_rules"]["modules"]) != 1:
            raise BOARulesIncomplete("'boa_rules.modules' has not the expected #elements")

        is_key_in_dict(self.rules, "boa_rules.modules.module", split=".",
                       raise_exception=BOARulesIncomplete,
                       exception_args="'boa_rules.modules.module'")

        modules = self.rules["boa_rules"]["modules"]["module"]

        if not isinstance(modules, list):
            modules = [modules]

        # Check concrete restrictions for each module
        for module in modules:
            severity_enum = Other.other_report_default_severity_enum
            lifecycle_handler = Other.other_lifecycle_default_handler
            module_name = module["module_name"]
            class_name = module["class_name"]
            dependencies = None
            total_tags_found = 0    # Madantory + optional
            total_mandatory_tags = 3

            # <args_sorting> checking
            if is_key_in_dict(module, "args_sorting"):
                total_tags_found += 1
            # <severity_enum> checking
            if is_key_in_dict(module, "severity_enum"):
                if not module["severity_enum"]:
                    raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                   ".severity_enum' cannot be"
                                                   f" empty ('{module_name}.{class_name}')")

                regex_result = re.match(Regex.regex_general_module_class_name,
                                        module["severity_enum"])

                if regex_result is None:
                    raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                   ".severity_enum' does not match with"
                                                   f" the expected regex "
                                                   f"('{module_name}.{class_name}')")

                severity_enum = module["severity_enum"]
                total_tags_found += 1
            # <lifecycle_handler> checking
            if is_key_in_dict(module, "lifecycle_handler"):
                if not module["lifecycle_handler"]:
                    raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                   ".lifecycle_handler' cannot be"
                                                   f" empty ('{module_name}.{class_name}')")

                regex_result = re.match(Regex.regex_general_module_class_name,
                                        module["lifecycle_handler"])

                if regex_result is None:
                    raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                   ".lifecycle_handler' does not match with"
                                                   f" the expected regex "
                                                   f"('{module_name}.{class_name}')")

                lifecycle_handler = module["lifecycle_handler"]
                total_tags_found += 1
            # <dependencies> checking
            if is_key_in_dict(module, "dependencies"):
                if not module["dependencies"]:
                    raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                   ".dependencies' cannot be"
                                                   f" empty ('{module_name}.{class_name}')")

                dependencies = module["dependencies"]
                total_tags_found += 1


            if len(module) != (total_mandatory_tags + total_tags_found):
                raise BOARulesIncomplete("'boa_rules.modules.module' has not the expected"
                                         f" #elements in '{module_name}.{class_name}'")

            # Set default values if no value was set
            if not is_key_in_dict(module, "severity_enum"):
                module["severity_enum"] = severity_enum
            if not is_key_in_dict(module, "lifecycle_handler"):
                module["lifecycle_handler"] = lifecycle_handler

            # Dependencies checking
            dependencies_reference = None

            if dependencies is not None:
                dependencies_reference = {}

                is_key_in_dict(dependencies, "dependency",
                               raise_exception=BOARulesIncomplete,
                               exception_args="'boa_rules.modules.module."
                                              "dependencies.dependency'")

                if len(dependencies) != 1:
                    raise BOARulesIncomplete("'boa_rules.modules.module.dependencies' has not the"
                                             f" expected #elements in '{module_name}.{class_name}'")

                dependencies = dependencies["dependency"]

                if not isinstance(dependencies, list):
                    dependencies = [dependencies]

                for dependency in dependencies:
                    dependency_key = f"{dependency['module_name']}.{dependency['class_name']}"

                    if is_key_in_dict(dependencies_reference, dependency_key):
                        raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                       ".dependencies.dependency' cannot have"
                                                       " different dependencies with same"
                                                       " module and class name"
                                                       f" ('{module_name}.{class_name}')")

                    dependencies_reference[dependency_key] = {}

                    if not dependency:
                        raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                       ".dependencies.dependency' cannot be"
                                                       f" empty ('{module_name}.{class_name}')")
                    if len(dependency) != 3:
                        raise BOARulesIncomplete("'boa_rules.modules.module.dependencies"
                                                 ".dependency' has not the expected #elements"
                                                 f" in '{module_name}.{class_name}'")

                    is_key_in_dict(dependency, "module_name",
                                   raise_exception=BOARulesIncomplete,
                                   exception_args="'boa_rules.modules.module."
                                                  "dependencies.dependency.module_name'")
                    is_key_in_dict(dependency, "class_name",
                                   raise_exception=BOARulesIncomplete,
                                   exception_args="'boa_rules.modules.module."
                                                  "dependencies.dependency.class_name'")
                    is_key_in_dict(dependency, "callback",
                                   raise_exception=BOARulesIncomplete,
                                   exception_args="'boa_rules.modules.module."
                                                  "dependencies.dependency.callback'")
                    is_key_in_dict(dependency, "callback.method", split=".",
                                   raise_exception=BOARulesIncomplete,
                                   exception_args="'boa_rules.modules.module."
                                                  "dependencies.dependency.callback.method'")

                    callback = dependency["callback"]

                    if not callback:
                        raise BOARulesUnexpectedFormat("'boa_rules.modules.module"
                                                       ".dependencies.dependency.callback' cannot"
                                                       f" be empty ('{module_name}.{class_name}')")
                    if len(callback) != 1:
                        raise BOARulesIncomplete("'boa_rules.modules.module.dependencies."
                                                 ".dependency.callback' has not the expected"
                                                 f" #elements in '{module_name}.{class_name}'")

                    methods = callback["method"]

                    if not isinstance(methods, list):
                        methods = [methods]

                    for method in methods:
                        if len(method) != 2:
                            raise BOARulesIncomplete("'boa_rules.modules.module.dependencies"
                                                     ".dependency.callback.method' has not the"
                                                     " expected #elements in"
                                                     f" '{module_name}.{class_name}'")

                        is_key_in_dict(method, "@name",
                                       raise_exception=BOARulesIncomplete,
                                       exception_args="'boa_rules.modules.module.dependencies."
                                                      "dependency.callback.method@name'")
                        is_key_in_dict(method, "@callback",
                                       raise_exception=BOARulesIncomplete,
                                       exception_args="'boa_rules.modules.module.dependencies."
                                                      "dependency.callback.method@callback'")

                        if is_key_in_dict(dependencies_reference, method["@name"]):
                            logging.warning("dependency '%s' has been smashed", method['@name'])

                        dependencies_reference[dependency_key][method["@name"]] = \
                            method["@callback"]

            # Args checking
            arg_reference = {}

            try:
                arg_reference = self.check_rules_arg_high_level(module,
                                                                "module",
                                                                "boa_rules.modules.module",
                                                                save_args)
            except BOARulesIncomplete as e:
                raise BOARulesIncomplete(f"rules incomplete in '{module_name}.{class_name}'") from e
            except BOARulesUnexpectedFormat as e:
                raise BOARulesUnexpectedFormat(f"rules unexpected format in '{module_name}.{class_name}'") from e
            except BOARulesError as e:
                raise BOARulesError(f"rules error in '{module_name}.{class_name}'") from e

            # Set the args
            if (save_args and not self.set_args(f"{module_name}.{class_name}", arg_reference)):
                raise BOARulesError("'boa_rules.modules.module' is not correct "
                                    f"('{module_name}.{class_name}' already set?)")
            # Set the dependencies
            if (dependencies_reference is not None and
                    not self.set_dependencies(f"{module_name}.{class_name}",
                                              dependencies_reference)):
                raise BOARulesError("'boa_rules.modules.module.dependencies' is not correct "
                                    f"('{module_name}.{class_name}' already set?)")
            elif (dependencies_reference is None and
                  not self.set_dependencies(f"{module_name}.{class_name}",
                                            {})):
                raise BOARulesError("'boa_rules.modules.module.dependencies' is not correct "
                                    f"('{module_name}.{class_name}' already set?)")

    def check_rules_report(self, save_args):
        """It makes the checks relative to the report.

        Arguments:
            save_args (bool): it indicates that the arguments
                have to be saved while they are being checked.

        Raises:
            BOARulesIncomplete: when the number of expected
                mandatory rules does not match with the actual
                number of rules or when a concrete rule is not
                found.
            BOARulesError: when a semantic rule is broken.
                You have to follow the rules documentation to
                avoid this exception.
        """
        # Check if there are the expected #elements in the modules element
        report = self.rules["boa_rules"]["report"]
        total_tags_found = 0

        # The 'report' tag can have [1, 4] #elements
        if (len(report) == 0 or len(report) > 4):
            raise BOARulesIncomplete("'boa_rules.report' has not the expected #elements")

        # Check if both, module and class name, are defined or not
        if is_key_in_dict(report, "module_name") ^ is_key_in_dict(report, "class_name"):
            raise BOARulesError("'boa_rules.report' has to have defined both 'module_name'"
                                " and 'class_name' or have not defined any of them")

        if is_key_in_dict(report, "module_name"):
            # Both 'module_name' and 'class_name' are defined
            total_tags_found += 2

        if is_key_in_dict(report, "args_sorting"):
            total_tags_found += 1

        if is_key_in_dict(report, "args"):
            total_tags_found += 1

        if len(report) != total_tags_found:
            raise BOARulesIncomplete("'boa_rules.report' has not the expected #elements")

        # Args checking
        arg_reference = {}

        try:
            arg_reference = self.check_rules_arg_high_level(report,
                                                            "report",
                                                            "boa_rules.report",
                                                            save_args)
        except BOARulesError as e:
            raise BOARulesError("rules error in 'boa_rules.report'") from e

        # Set the report args
        self.report_args = arg_reference

    def check_rules(self, save_args):
        """It checks if the rules file contains the mandatory
        rules. The checking is performed by name and elements
        quantity, so it has to match in both properties.

        If *self.rules* is *None*, the checking fails.

        Arguments:
            save_args (bool): it indicates that the arguments
                have to be saved while they are being checked.

        Returns:
            bool: true if the rules are valid; false otherwise
        """
        if self.rules is None:
            return False

        try:
            # It makes the initial checks about the main tags
            self.check_rules_init()

            # Analysis (we are sure we can access, since the initial tests passed)
            analysis = self.rules["boa_rules"]["@analysis"]

            if analysis == "static":
                # It makes the checks relative to the parser
                self.check_rules_parser()
            elif analysis == "dynamic":
                # It makes the checks relative to dynamic analysis modules
                self.check_rules_dynamic_analysis_runner(save_args, "inputs")
                self.check_rules_dynamic_analysis_runner(save_args, "fails")
            else:
                raise Exception(f"unexpected analysis attribute value: {analysis}")

            # It makes the checks relative to the modules
            self.check_rules_modules(save_args)

            # It makes the checks relative to the report
            self.check_rules_report(save_args)

        except BOARulesUnexpectedFormat as e:
            logging.error("wrong format: %s", str(e))
            return False
        except BOARulesIncomplete as e:
            logging.error("rules are incomplete: %s", str(e))
            return False
        except BOARulesError as e:
            logging.error("something is wrong (format and completeness seem to be ok): %s", str(e))
            return False
        except Exception as e:
            logging.error("rules did not pass the checking: %s", str(e))
            return False

        return True

    def get_rules(self, path=None, list_type=False):
        """It returns the rules.

        The rules can be obtained with a concrete *path*, which
        means that you can obtain the rules you want directly,
        without go through them. The path is a string which
        will be splited with '.'.

        Arguments:
            path (str): the returned rules will be from a starting
                point. If you to get all the modules rules, the path
                has to have the value "boa_rules.modules.module".
                The default value is *None*.
            list_type (bool): the returned rules will be wrapped
                in a list. The default value is *False*.

        Returns:
            dict: rules from the rules file. If *list_type* is *True*,
            the returning type will not be *dict* but *list*.
        """
        if path is None:
            return self.rules

        rules = self.rules

        for p in path.split("."):
            try:
                rules = rules[p]
            except KeyError as e:
                logging.error("could not get the rules (returning all the rules): %s", str(e))
                return self.rules
            except Exception as e:
                logging.error("unexpected error while getting the rules (returning all the rules): %s", str(e))
                return self.rules

        if list_type:
            if not isinstance(rules, list):
                rules = [rules]

        return rules

    def set_args(self, module, arg):
        """It sets the arguments for a concrete module.
        This method should only be used for internal management.

        Arguments:
            module (str): instance identification as string. The
                expected format is (without quotes): "module_name
                .class_name". Check *utils.get_name_from_class_instance*.
            arg (dict): the new args for the module.

        Returns:
            bool: *True* if the args could be set; *False* otherwise
        """
        if self.args is None:
            self.args = {}
        elif not isinstance(self.args, dict):
            logging.error("args type is not a dict")
            return False
        elif is_key_in_dict(self.args, module):
            logging.warning("args for module '%s' already exists: overwriting it", module)

        try:
            self.args[module] = arg

            return True
        except Exception as e:
            logging.error("RulesManager: %s", str(e))

            return False

    def get_args(self, module=None):
        """It returns the args for a concrete module.

        Arguments:
            module (str): module from which args are going
                to be returned. The expected format is
                (without quotes): "module_name.class_name".
                Check *utils.get_name_from_class_instance*.
                The default value is *None*.

        Returns:
            dict: module args or all the modules args;
            *None* if a module were specified and could
            not find it
        """
        if module is None:
            return self.args

        if (self.args is not None and
            isinstance(self.args, dict) and
            is_key_in_dict(self.args, module)):
            return self.args[module]

        logging.warning("could not get the args for module '%s'", module)
        return None

    def set_dependencies(self, module, dependencies):
        """It adds dependencies for a concrete module.
        This method should only be used for internal management.

        Arguments:
            module (str): instance identification as string. The
                expected format is (without quotes): "module_name
                .class_name". Check *utils.get_name_from_class_instance*.
            dependencies (dict): the new dependencies for the module.

        Returns:
            bool: *True* if the dependencies could be apppended; *False* otherwise
        """
        if self.dependencies is None:
            self.dependencies = {}
        elif not isinstance(self.dependencies, dict):
            logging.error("dependencies type is not a dict")
            return False
        if not is_key_in_dict(self.dependencies, module):
            self.dependencies[module] = {}
        elif not isinstance(self.dependencies[module], dict):
            logging.error("dependencies['%s'] type is not a dict", module)
            return False

        try:
            for key, value in dependencies.items():
                if is_key_in_dict(self.dependencies[module], key):
                    logging.warning("dependency '%s' for module '%s' already exists: overwriting it", key, module)

                self.dependencies[module][key] = value

            return True
        except Exception as e:
            logging.error("RulesManager: %s", str(e))

            return False

    def get_dependencies(self, module=None):
        """It returns the dependencies for a concrete module.

        Arguments:
            module (str): module from which args are going
                to be returned. The expected format is
                (without quotes): "module_name.class_name".
                Check *utils.get_name_from_class_instance*.
                The default value is *None*.

        Returns:
            dict: module dependencies or all the modules dependencies;
            *None* if a module were specified and could not find it,
            what means that the module does not have dependencies
        """
        if module is None:
            return self.dependencies

        if (self.dependencies is not None and
                isinstance(self.dependencies, dict) and
                is_key_in_dict(self.dependencies, module)):
            return self.dependencies[module]

        return None

    def get_report_args(self):
        """It returns the args for the Report instance.

        Returns:
            dict: report args
        """
        return self.report_args
