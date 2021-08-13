
"""BOA module which uses fuzzing with basic binaries which are managed totally
from terminal.
"""

# TODO finish and check docstrings

# Std libs
import re
import os
import logging
import tempfile
import subprocess
import multiprocessing

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta, Regex
import utils

class BOAModuleGenAlgFuzzing(BOAModuleAbstract):
    """
    """

    def initialize(self):
        """It initializes the module.
        """
        if "boam_basic_fuzzing.BOAModuleBasicFuzzing" not in self.dependencies:
            raise BOAModuleAbstract("dependency 'boam_basic_fuzzing.BOAModuleBasicFuzzing' is necessary")
        if "instance" not in self.dependencies["boam_basic_fuzzing.BOAModuleBasicFuzzing"]:
            raise BOAModuleAbstract("callback 'instance' in 'boam_basic_fuzzing.BOAModuleBasicFuzzing' is necessary")

        self.genalg_child_instance = self.dependencies["boam_basic_fuzzing.BOAModuleBasicFuzzing"]["instance"]()
        self.epochs = 1 if not utils.is_key_in_dict(self.args, "epochs") else int(self.args["epochs"])

    def process(self, runners_args):
        """It implements a basic fuzzing technique.

        Arguments:
            runners_args (dict): dict with runners arguments.
        """
        for epoch in range(self.epochs):
            for yield_return in self.genalg_child_instance.process_wrapper(runners_args):
                if yield_return is None:
                    break

                # Process all results or part of them (multiprocessing)
                worker_args, worker_results, output_status = yield_return

                worker_args = sorted(worker_args)
                worker_results = sorted(worker_results)
                output_status = sorted(output_status)

                # Get relevant values for the genalg
                for idx, (input, instrumentation, fail) in enumerate(zip(worker_args, worker_results, output_status)):
                    if (input[0] != instrumentation[0] or input[0] != fail[0]):
                        logging.warning("epoch %d child unk. idx %d: mismatch of child idxs (%d vs %d vs %d): skipping",
                                        idx, epoch, input[0], instrumentation[0], fail[0])
                        continue

                    # Relevant values
                    input = input[1]
                    instrumentation = instrumentation[2]
                    fail = fail[1]

                    # TODO finish

            logging.info("epoch %d of %d: %.2f completed", epoch + 1, self.epochs, (epoch / self.epochs) * 100.0)

    def clean(self):
        """It does nothing.
        """

    def finish(self):
        """It does nothing.
        """
