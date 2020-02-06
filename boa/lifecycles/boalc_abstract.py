"""
"""

# Std libs
from abc import abstractmethod

# Own libs
from util import get_name_from_class_instance

class BOALifeCycleAbstract:
    """
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
        """
        """

    def get_name(self):
        """
        """
        return self.who_i_am
