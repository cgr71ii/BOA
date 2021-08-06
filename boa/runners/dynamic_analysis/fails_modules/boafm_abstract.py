
"""File which contains the base class to inherit from to use
a fail module. Fail modules are those modules whose goal
must be deal with the output of a specific execution and know
if should considered as a fail or not. Consider a fail might
change depending on the module
"""

# Std libs
from abc import abstractmethod

# Own libs
from utils import get_name_from_class_instance

# This  file name has to match with constants.Meta.abstract_fail_module_name
# This class name has to match with constants.Meta.abstract_fail_module_class_name
class BOAFailModuleAbstract:
    """BOAFailModuleAbstract class.

    This class is the base class for those class whose want to
    be a Fail Module to know when a specific execution have failed
    (e.g. exit status different from 0). Those classes have to
    inherit from this class in order to be possible to invoke the
    methods defined here.
    """

    def __init__(self, args):
        """Init method which initializes the general variables which
        will be available from all the classes that inherits from this one.

        Arguments:
            args (dict): arguments.
        """
        self.args = args
        self.who_i_am = get_name_from_class_instance(self)

    @abstractmethod
    def initialize(self):
        """Method which will be invoked to initialize what is necessary.
        """

    @abstractmethod
    def execution_has_failed(self, execution_status):
        """Method which returns *True* if a specific execution have failed
        or *False* otherwise.

        Arguments:
            execution_status: information which should be necessary to
                infer if a specific execution has failed

        Returns:
            bool: *True* if the execution is considered as a fail
        """
