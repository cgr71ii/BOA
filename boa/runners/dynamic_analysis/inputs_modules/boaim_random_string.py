
"""BOA Input Module.

This module generates random strings as inputs.
"""

# Std libs
import string
import random
import logging

# Own libs
from boaim_abstract import BOAInputModuleAbstract

class BOAIMRandomString(BOAInputModuleAbstract):
    """BOAIMRandomString class.
    """

    def initialize(self):
        """It initializes the necessary variables.
        """
        self.length = 10

        if "length" in self.args:
            self.length = int(self.args["length"])

        logging.debug("inputs length: %d", self.length)

    def generate_input(self):
        """It generates random strings.

        The generated strings contain ascii uppercase letters and digits.

        Returns:
            str: random string.
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=self.length))