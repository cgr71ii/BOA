"""This file contains the class from which all lifecycles
will have to inherit in order to be executed as a lifecycle.
If a lifecycle does not inherit from the implemented class
in this file, an error will be raised.
"""

# Std libs
from abc import abstractmethod

# Own libs
from utils import get_name_from_class_instance

class BOALifeCycleAbstract:
    """BOALifeCycleAbstract class.

    This class implements the necessary methods which will be
    invoked after by *BOALifeCycleManager*. Moreover, it defines
    variables with important information (e.g. "args" variable
    which contains the given arguments throught the rules file).
    """

    def __init__(self, instance, report, lifecycle_args, execute_method_callback, analysis):
        """It initializes the class.
        """
        self.instance = instance
        self.report = report
        self.args = lifecycle_args
        self.execute_method = execute_method_callback
        self.analysis = analysis
        self.who_i_am = get_name_from_class_instance(self)

        # Check if the selected analysis is valid for the current lifecycle
        self.raise_exception_if_non_valid_analysis()

    @abstractmethod
    def raise_exception_if_non_valid_analysis(self):
        """Method which will be executed when a lifecycle has been initialized
        and should raise an exception if the analysis is not valid for the
        lifecycle.

        Raises:
            BOALCAnalysisException: when the selected analysis is not compatible
                with the lifecycle.
        """

    @abstractmethod
    def execute_lifecycle(self):
        """Method which defines the concrete lifecycle to be
        executed. This method will have to be implemented
        by those lifecycles which want to define a new lifecycle.
        """

    def get_name(self):
        """Method which returns the name of the concrete instance.

        This method is defined because a security module can only
        access method by name (it invokes the methods by a method
        which is given by a callback) and no directly access to the
        variables.

        This method could be invoked by a security modules in order
        to, for example, give a concrete error message.

        Returns:
            str: self.who_i_am (i.e. '"module_name"."class_name"')
        """
        return self.who_i_am
