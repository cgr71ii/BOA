
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
        self.randomize_length = False

        if "length" in self.args:
            self.length = int(self.args["length"])
        if "randomize_length" in self.args:
            randomize_length = self.args["randomize_length"].lower().strip()

            if randomize_length == "true":
                self.randomize_length = True

                logging.debug("randomizing length from 0 to %d", self.length)

        logging.debug("inputs length: %d", self.length)

    def generate_input(self):
        """It generates random strings.

        The generated strings contain ascii uppercase letters and digits.

        Returns:
            str: random string.
        """
        length = self.length

        if self.randomize_length:
            length = random.randint(0, length)

        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))