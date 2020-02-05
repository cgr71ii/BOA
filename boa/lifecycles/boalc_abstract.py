"""
"""

# Std libs
from abc import abstractmethod

class BOALifeCycleAbstract:
    """
    """

    def __init__(self, instance, report, lifecycle_args, loop_method_callback):
        """
        """
        self.instance = instance
        self.report = report
        self.args = lifecycle_args
        self.loop = loop_method_callback

    @abstractmethod
    def execute_lifecycle(self):
        """
        """
