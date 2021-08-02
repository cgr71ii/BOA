"""Module Imports.

This file contains the ModulesImporter class.
"""

# Std libs
import importlib.util
import logging
import sys

# Own libs
from constants import Other
from utils import get_current_path, file_exists, is_key_in_dict
from exceptions import BOAModuleNotLoaded, BOAModulesImporterException

class ModulesImporter:
    """ModulesImporter class.

    This class has the goal of loading the modules which
    are specified in the given rules.
    """

    def __init__(self, modules, filenames=None):
        """It initializes the class.

        Arguments:
            modules (list): modules (str) which should be loaded after.
            filenames (list): modules filenames (str). The default
                value is *None*, and if this value remains, *modules*
                will be used as filename.
        """
        self.modules = []
        self.filenames = []
        self.loaded = []
        self.nmodules = 0
        self.nloaded = 0

        for module in modules:
            self.modules.append(module)
            self.nmodules += 1
            self.loaded.append(False)

            if filenames is None:
                self.filenames.append(f"{module}.py")

        if filenames is not None:
            for filename in filenames:
                self.filenames.append(filename)

        if len(self.modules) != len(self.filenames):
            raise BOAModulesImporterException("len(modules) has to be equal to "
                                              "len(filenames) and is not")

    def load(self, module_subdir=None):
        """It attempts to load all the modules which were specified.

        This method iterates through self.modules to attempt to loading
        the modules. First, it checks if the module is already loaded.
        Then, it attempts to load the module and if it is not able to,
        it skips the current module to next.

        The modules must be in *Other.modules_directory* directory.

        Arguments:
            module_subdir (str): subdir of *Other.modules_directory* where
                the module will be looked for instead of directly look for
                in *Other.modules_directory*
        """
        index = 0

        while index < len(self.modules):
            module = self.modules[index]
            filename = self.filenames[index]
            file_path = f"{get_current_path(__file__)}/{Other.modules_directory}"

            if module_subdir is not None:
                module_subdir = module_subdir.strip("/")
                file_path = f"{file_path}/{module_subdir}/{filename}"
            else:
                file_path = f"{file_path}/{filename}"

            try:
                # Check if the module is already loaded
                if module in sys.modules:
                    logging.warning("module '%s' cannot have that name because it collides with a sys"
                                    " module or has been already loaded: skipping current module", module)
                    index += 1
                    continue

                # Check if the actual file path does exist
                if file_exists(file_path) is False:
                    logging.warning("file '%s' does not exist: skipping current module", file_path)
                    index += 1
                    continue

                spec = importlib.util.spec_from_file_location(module, file_path)

                # Check if we could get the module spec
                if spec is None:
                    logging.warning("module '%s' could not be loaded: skipping current module", module)
                    index += 1
                    continue

                # Load and save the module
                new_module = importlib.util.module_from_spec(spec)
                sys.modules[module] = new_module

                spec.loader.exec_module(new_module)
                self.loaded[index] = True
                self.nloaded += 1

                logging.info("module '%s' successfully loaded", module)
            except Exception as e:
                logging.warning("skipping current module: %s", str(e))
                index += 1
                continue

            index += 1

    def is_module_loaded(self, module_name):
        """It checks if a concrete module is already loaded.

        Arguments:
            module_name (str): module to check if it is loaded.

        Returns:
            bool: module_name is loaded
        """
        index = self.modules.index(module_name)

        # Check if the module is loaded
        if not self.loaded[index]:
            return False

        return True

    def get_module(self, module_name):
        """It returns an already loaded module.

        Arguments:
            module_name (str): module name which is attempted to return.

        Raises:
            BOAModuleNotLoaded: when it is attempted to get a module
                which is not loaded.
            Exception: when a module is detected as loaded but it is
                not loaded in *sys.modules*. It should not happen.

        Returns:
            Module if loaded; *None* otherwise
        """
        try:
            if self.is_module_loaded(module_name) == False:
                raise BOAModuleNotLoaded()
            # It should not happen
            if is_key_in_dict(sys.modules, module_name) == False:
                raise Exception()

            return sys.modules[module_name]
        except ValueError:
            logging.error("could not get module '%s' because it does not exist", module_name)
        except BOAModuleNotLoaded:
            logging.error("could not get module '%s' because it is not loaded", module_name)
        except Exception as e:
            logging.error("could not get module '%s': %s", module_name, str(e))

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
            logging.error("ModulesImporter: %s", str(e))
        except Exception as e:
            logging.error("unknown error while trying to get '%s.%s': %s", module_name, class_name, str(e))

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
            if not self.loaded[index]:
                not_loaded_modules.append(self.modules[index])

            index += 1

        return not_loaded_modules

    @classmethod
    def load_and_get_instance(cls, module, absolute_file_path, class_name, verbose=True):
        """Class method which attempts to load a module and return an
        instance of it.

        If the module is already loaded, it will skip the loading part
        and it will continue to next phase: get the instance.

        Arguments:
            module (str): module name to be loaded.
            absolute_file_path (str): full path to the file which contains
                the module to be loaded.
            class_name (str): class name inside the module which is going
                to be instantiated.
            verbose (bool): if *True*, a message will be displayed if the
                loading success.

        Returns:
            instance: an instance of "module.class" which has been specified
            or *None* if could not.
        """
        instance = None

        # Check if the actual file path does exist
        if not file_exists(absolute_file_path):
            logging.warning("file '%s' does not exist: skipping current module", absolute_file_path)
            return None

        try:
            if not module in sys.modules:
                spec = importlib.util.spec_from_file_location(module, absolute_file_path)

                # Check if we could get the module spec
                if spec is None:
                    logging.warning("module '%s' could not be loaded: skipping current module", module)
                    return None

                new_module = importlib.util.module_from_spec(spec)
                sys.modules[module] = new_module

                spec.loader.exec_module(new_module)

                if verbose:
                    logging.info("module '%s' successfully loaded", module)
        except Exception as e:
            logging.warning("error when importing module '%s': %s", module, str(e))
            return None

        # Module has been loaded once reached this point (or it was already loaded)

        tmp_module = sys.modules[module]

        # Check if the module is already loaded (it should be if we have reached this point)
        if tmp_module is None:
            return None

        # Get the instance
        try:
            instance = getattr(sys.modules[module], class_name)
        except AttributeError as e:
            logging.error("ModulesImporter: %s", str(e))
        except Exception as e:
            logging.error("unknown error while trying to get '%s.%s': %s", module, class_name, str(e))

        return instance
