
"""Module Imports.

This file contains the ModulesImporter class.
"""

# Std libs
import importlib.util
import sys

# Own libs
from constants import Meta
from util import eprint, get_current_path, file_exists, is_key_in_dict
from own_exceptions import BOAModuleNotLoaded

class ModulesImporter:
    """ModulesImporter class.

    This class has the goal of loading the modules which
    are specified in the given rules.
    """

    def __init__(self, modules):
        """It initializes the class.

        Arguments:
            modules (list): modules (str) which should be loaded after.
        """
        self.modules = []
        self.loaded = []
        self.nmodules = 0
        self.nloaded = 0

        for module in modules:
            self.modules.append(module)
            self.nmodules += 1
            self.loaded.append(False)

    def load(self):
        """It attempts to load all the modules which were specified.

        This method iterates through self.modules to attempt to loading
        the modules. First, it checks if the module is already loaded.
        Then, it attempts to load the module and if it is not able to,
        it skips the current module to next.

        The modules must be in *Meta.modules_directory* directory.
        """
        index = -1

        for module in self.modules:
            index = index + 1

            try:
                if module in sys.modules:
                    eprint(f"Warning: module '{module}' cannot have that name because it collides with a sys module or has been already loaded. Skipping current module.")
                    continue

                file_path = f'{get_current_path(__file__)}/{Meta.modules_directory}/{module}.py'
                spec = importlib.util.spec_from_file_location(module, file_path)

                # Check if we could get the module spec
                if spec is None:
                    eprint(f"Warning: module '{module}' could not be loaded. Skipping current module.")
                    continue

                new_module = importlib.util.module_from_spec(spec)

                # Check if the actual file path does exist
                if file_exists(file_path) is False:
                    eprint(f"Warning: file '{file_path}' does not exist. Skipping current module.")
                    continue

                sys.modules[module] = new_module

                spec.loader.exec_module(new_module)
                self.loaded[index] = True
                self.nloaded += 1

                print(f"Info: Module '{module}' successfully loaded.")
            except Exception as e:
                eprint(f"Warning: {e}. Skipping current module.")
                continue
            except:
                eprint(f"Warning: unknown error while loading module '{module}'. Skipping current module.")
                continue

    def is_module_loaded(self, module_name):
        """It checks if a concrete module is already loaded.

        Arguments:
            module_name (str): module to check if it is loaded.

        Returns:
            bool: module_name is loaded
        """
        index = self.modules.index(module_name)

        # Check if the module is loaded
        if self.loaded[index] is False:
            return False

        return True

    def get_module(self, module_name):
        """It returns a already loaded module.

        Arguments:
            module_name (str): module name which is attempted to return.

        Raises:
            BOAModuleNotLoaded: when it is attempted to get a module
                which is not loaded.
            Exception: when a module is detected as loaded but it is
                not loaded in *sys.modules*. It should not happen.

        Todo: change Exception raiseness with a custom exception.

        Returns:
            Module if loaded; *None* otherwise
        """
        try:
            if self.is_module_loaded(module_name) is False:
                raise BOAModuleNotLoaded()
            # It should not happen
            if is_key_in_dict(sys.modules, module_name) is False:
                raise Exception()

            return sys.modules[module_name]
        except ValueError:
            eprint(f"Error: could not get module '{module_name}' because it does not exist.")
        except BOAModuleNotLoaded:
            eprint(f"Error: could not get module '{module_name}' because it is not loaded.")
        except:
            eprint(f"Error: could not get module '{module_name}'. Unknown reason.")

        return None

    def get_instance(self, module_name, class_name):
        """It returns an instance of the class of a module.

        Arguments:
            module_name (str): module name which should contains *class_name*.
            class_name (str): class name which is attempted to return.

        Returns:
            Module instance if module is loaded; *None* otherwise
        """
        module = self.get_module(module_name)
        instance = None

        if module is None:
            return instance

        try:
            instance = getattr(sys.modules[module_name], class_name)
        except AttributeError as e:
            eprint(f"Error: {e}.")
        except:
            eprint(f"Error: unknown error while trying to get {module_name}.{class_name}.")

        return instance

    def get_nmodules(self):
        """It returns the number of modules which were suplied to the class
        to be loaded.

        A different variable is being used instead of len() method because
        the variable which contains the methods to be loaded mutates
        through the execution of the class methods.

        Returns:
            int: initial modules to be loaded
        """
        return self.nmodules

    def get_nloaded(self):
        """It returns the number of loaded modules at the moment of the calling.

        Returns:
            int: loaded modules
        """
        return self.nloaded

    def get_not_loaded_modules(self):
        """It returns the modules which have not been loaded.

        Returns:
            list: not loaded modules
        """
        index = 0
        not_loaded_modules = []

        while index < len(self.modules):
            if self.loaded[index] is False:
                not_loaded_modules.append(self.modules[index])

            index += 1

        return not_loaded_modules
