
"""BOA Fail Module.

This module checks when the execution of a binary fails looking
the status code.
"""

# Own libs
from boafm_abstract import BOAFailModuleAbstract

class BOAFMExitStatus(BOAFailModuleAbstract):
    """BOAFMExitStatus class.
    """

    def initialize(self):
        """It does nothing.
        """
        pass

    def execution_has_failed(self, execution_status):
        """It checks if the status code has a value which means thath
        the execution has failed.

        Parameters:
            execution_status (int): status code of an execution.

        Returns:
            bool: *True* if *execution_status* is different of 0.
        """
        if execution_status != 0:
            return True

        return False