"""This file contains the class from which all lifecycles
will have to inherit in order to be executed as a lifecycle.
If a lifecycle does not inherit from the implemented class
in this file, an error will be raised.
"""

# Std libs
from abc import abstractmethod

# Own libs
from util import get_name_from_class_instance

class BOALifeCycleAbstract:
    """BOALifeCycleAbstract class.

    This class implements the necessary methods which will be
    invoked after by *BOALifeCycleManager*. Moreover, it defines
    variables with important information (e.g. "args" variable
    which contains the given arguments throught the rules file).
    """

    def __init__(self, instance, report, lifecycle_args, execute_method_callback):
        """
        """
        self.instance = instance
        self.report = report
        self.args = lifecycle_args
        self.execute_method = execute_method_callback
        self.who_i_am = get_name_from_class_instance(self)

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
