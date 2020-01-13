
# Std libs
import importlib.util
import sys

# Own libs
from constants import Meta
from util import eprint
from util import get_current_path
from util import file_exists
from util import value_exists_in_array
from own_exceptions import BOAModuleNotLoaded

class ModulesImporter:

    def __init__(self, modules):
        self.modules = []
        self.loaded = []
        self.nmodules = 0
        self.nloaded = 0

        for module in modules:
            self.modules.append(module)
            self.nmodules += 1
            self.loaded.append(False)

    def load(self):
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
        index = self.modules.index(module_name)

        # Check if the module is loaded
        if self.loaded[index] is False:
            return False

        return True

    def get_module(self, module_name):
        try:
            if self.is_module_loaded(module_name) is False:
                raise BOAModuleNotLoaded()
            # It should not happen
            if value_exists_in_array(sys.modules, module_name) is False:
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
        return self.nmodules

    def get_nloaded(self):
        return self.nloaded

    def get_not_loaded_modules(self):
        index = 0
        not_loaded_modules = []

        while index < len(self.modules):
            if self.loaded[index] is False:
                not_loaded_modules.append(self.modules[index])

            index += 1

        return not_loaded_modules
