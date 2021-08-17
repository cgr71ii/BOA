
"""BOA Input Module.

This module generates random strings as inputs or returns
one of the provided seed inputs.
"""

# Std libs
import random
import logging

# Own libs
from boaim_abstract import BOAInputModuleAbstract
from exceptions import BOARunnerModuleError
import utils

class BOAIMInputSeed(BOAInputModuleAbstract):
    """BOAIMInputSeed class.
    """

    def initialize(self):
        """It initializes the necessary variables.
        """
        self.input_seed = []
        self.random_max_length = 100
        self.random_likelihood = 0.1
        self.max_random_inputs = None
        self.generated_inputs = 0

        if "random_max_length" in self.args:
            self.random_max_length = int(self.args["random_max_length"])
        if "random_likelihood" in self.args:
            self.random_likelihood = float(self.args["random_likelihood"])
        if "max_random_inputs" in self.args:
            self.max_random_inputs = int(self.args["max_random_inputs"])
        if "input_seed" in self.args:
            if (isinstance(self.args["input_seed"], list) and len(self.args["input_seed"]) != 0):
                for seed in self.args["input_seed"]:
                    if not isinstance(seed, str):
                        raise BOARunnerModuleError("not all provided inputs are strings")

                self.input_seed = self.args["input_seed"]

        if len(self.input_seed) == 0:
            raise BOARunnerModuleError("length of seed inputs is 0")

        logging.debug("random inputs max. length: %d", self.random_max_length)
        logging.debug("random inputs likelihood: %.2f", self.random_likelihood)

    def generate_input(self):
        """It generates random strings.

        The generated strings contain ascii uppercase letters and digits.

        Returns:
            str: random string.
        """
        r = random.random()

        if r < self.random_likelihood and (self.max_random_inputs is None or self.generated_inputs < self.max_random_inputs):
            length = random.randint(0, self.random_max_length)
            self.max_random_inputs = self.max_random_inputs + 1 if self.max_random_inputs is not None else None
            self.generated_inputs += 1

            return utils.get_random_utf8_seq(length, force_printable=random.random() < 0.5)
        else:
            idx = random.randint(0, len(self.input_seed) - 1)

            return self.input_seed[idx]
