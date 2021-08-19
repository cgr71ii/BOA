"""This lifecycle is exactly the same that the basic one, but
the *save* method of the module will not be executed and the
report instance will be provided to the *process* method in
a dictionary with the arguments.
"""

# Own libs
from boalc_abstract import BOALifeCycleAbstract

class BOALCWithoutAutomaticReporting(BOALifeCycleAbstract):
    """BOALCWithoutAutomaticReporting class.

    It inherits from *BOALifeCycleAbstract* and implements
    the necessary methods.
    """

    def raise_exception_if_non_valid_analysis(self):
        """This lifecycle is compatible with all analysis
        """

    def execute_lifecycle(self):
        """It invokes the following methods:

            1. *initialize()*
            2. *process({'__args__': self.args, '__report_instance__': self.report})*
            3. *clean()*
            4. *finish()*

        In case an unexpected error happens, only the method
        *finish* will be executed (its execution is forces), but
        this method will not be executed in case that the execution
        has been stopped on purpose (*stop* property).
        """
        # Initialize
        self.execute_method(self.instance, "initialize", None, False)

        # Process
        self.execute_method(self.instance, "process", {"__args__": self.args,
                                                       "__report_instance__": self.report}, False)

        # Clean
        self.execute_method(self.instance, "clean", None, False)

        # Finish
        self.execute_method(self.instance, "finish", None, True)
