
# Own libs
from constants import Meta
from util import eprint
from util import get_current_path
from util import file_exists
from util import value_exists_in_array
from exceptions import BOAModuleNotLoaded

# Std libs
import importlib.util
import sys

import tokenize

class ModulesImporter:

    def __init__(self, *modules):
        self.modules = []
        self.loaded = []

        for module in modules:
            self.modules.append(module)
            self.loaded.append(False)

    # TODO use custom exceptions to separate behaviour
    def load(self):
        index = -1

        for module in self.modules:
            index = index + 1

            try:
                if module in sys.modules:
                    eprint(f'Warning: module "{module}" cannot have that name because it collides with a sys module or has been already loaded. Skipping current module.')
                    continue

                file_path = f'{get_current_path(__file__)}/{Meta.modules_directory}/{module}.py'
                spec = importlib.util.spec_from_file_location(module, file_path)
                
                # Check if we could get the module spec
                if (spec is None):
                    eprint(f'Warning: module "{module}" could not be loaded. Skipping current module.')
                    continue

                new_module = importlib.util.module_from_spec(spec)
                
                # Check if the actual file path does exist
                if (file_exists(file_path) == False):
                    eprint(f'Warning: file "{file_path}" does not exist. Skipping current module.')
                    continue
                
                sys.modules[module] = new_module

                spec.loader.exec_module(new_module)
                self.loaded[index] = True

                print(f'Info: Module "{module}" successfully loaded.')
            except:
                eprint(f'Warning: unknown error while loading module "{module}". Skipping current module.')
                continue
    
    def get_module(self, module_name):
        try:
            index = self.modules.index(module_name)

            # Check if the module is loaded
            if (self.loaded[index] == False):
                raise BOAModuleNotLoaded()
            # It should not happen
            elif (value_exists_in_array(sys.modules, module_name) == False):
                raise Exception()

            return sys.modules[module_name]
        except ValueError:
            eprint(f'Error: could not get module "{module_name}" because it does not exist.')
        except BOAModuleNotLoaded:
            eprint(f'Error: could not get module "{module_name}" because it is not loaded.')
        except:
            eprint(f'Error: could not get module "{module_name}". Unknown reason.')
        
        return None