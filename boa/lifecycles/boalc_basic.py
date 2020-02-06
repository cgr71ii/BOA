"""
"""

# Own libs
from boalc_abstract import BOALifeCycleAbstract

class BOALCBasic(BOALifeCycleAbstract):
    """
    """

    def execute_lifecycle(self):
        """
        """
        # Initialize
        self.execute_method(self.instance, "initialize", "initialize", None, False)

        # Process
        self.execute_method(self.instance, "process", "process", self.args, False)

        # Clean
        self.execute_method(self.instance, "clean", "clean", None, False)

        # Save
        self.execute_method(self.instance, "save", "save (report)", self.report, False)

        # Finish
        self.execute_method(self.instance, "finish", "finish", None, True)
