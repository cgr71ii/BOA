"""This file contains the class which defines the, possibly,
most basic BOA lifecycle. It defines a lifecycle which just
invokes the methods defined in *BOAParserModuleAbstract* in
the expected order defined in the same file.

This class has 2 main goals:
    1. Be used when a user do not want to define its own lifecycle.
    2. Be an example of how to define a custom lifecycle.
"""

# Own libs
from boalc_abstract import BOALifeCycleAbstract

class BOALCBasic(BOALifeCycleAbstract):
    """BOALCBasic class.

    It inherits from *BOALifeCycleAbstract* and implements
    the necessary methods.
    """

    def raise_exception_if_non_valid_analysis(self):
        """This lifecycle is compatible with all analysis
        """

    def execute_lifecycle(self):
        """It invokes the next methods:

            1. *initialize()*
            2. *process(self.args)*
            3. *clean()*
            4. *save(self.report)*
            5. *finish()*

        In case an unexpected error happens, only the method
        *finish* will be executed (its execution is forces), but
        this method will not be executed in case that the execution
        has been stopped on purpose (*stop* property).
        """
        # Initialize
        self.execute_method(self.instance, "initialize", None, False)

        # Process
        self.execute_method(self.instance, "process", self.args, False)

        # Clean
        self.execute_method(self.instance, "clean", None, False)

        # Save
        self.execute_method(self.instance, "save", self.report, False)

        # Finish
        self.execute_method(self.instance, "finish", None, True)
