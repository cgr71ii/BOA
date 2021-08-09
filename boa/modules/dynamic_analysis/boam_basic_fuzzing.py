
"""BOA module which uses fuzzing with basic binaries which are managed totally
from terminal.
"""

# Std libs
import logging
import subprocess
from sys import stdin

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from utils import is_key_in_dict

class BOAModuleBasicFuzzing(BOAModuleAbstract):
    """BOAModuleBasicFuzzing class. It implements the class BOAModuleAbstract.

    This class implements the general behaviour necessary to implement the basics
    of fuzzing.
    """

    def initialize(self):
        """It initializes the module.
        """
        self.threats = []
        self.iterations = 1 if not is_key_in_dict(self.args, "iterations") else int(self.args["iterations"])
        self.pipe = False

        if "pipe" in self.args:
            pipe = self.args["pipe"].lower().strip()

            if pipe == "true":
                self.pipe = True

                logging.debug("providing input through pipe")

        logging.debug("iterations: %d", self.iterations)

    def process(self, runners_args):
        """It implements a basic fuzzing technique.

        Arguments:
            runners_args (dict): dict with runners arguments.
        """
        binary_path = runners_args["binary"]

        for _ in range(self.iterations):
            input = runners_args["inputs"]["instance"].generate_input()
            return_code = 0

            # TODO add option to add new line to the input (there are too many programs which expect this new line)
            ## TODO add \n by default and add option to DO NOT add the new line
            input += "\n"

            if not self.pipe:
                run = subprocess.run(f"{binary_path} {input}", shell=True)
                return_code = run.returncode
            else:
                # TODO add additional args when pipe
                run = subprocess.Popen([binary_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

                output = run.communicate(input=input.encode())

                # Output without decoding in order to avoid the backslashes preprocessing
                logging.debug("(input, output): (%s, %s)", input.encode(), output[0])

                return_code = run.returncode

            fail = runners_args["fails"]["instance"].execution_has_failed(return_code)

            if fail:
                # The input is encoded in order to avoid backslashes interpretation
                self.threats.append((self.who_i_am,
                                     f"the input {input.encode()} returned the status code {return_code}",
                                     "FAILED",
                                     "check if the fail is not a false positive",
                                     None, None))

    def clean(self):
        """It does nothing.
        """

    def save(self, report):
        """It appends the found threats.

        Arguments:
            report: Report instante to save all the found threats.
        """
        index = 0

        for threat in self.threats:
            severity = report.get_severity_enum_instance_by_who(self.who_i_am)

            if severity is None:
                logging.error("could not append the threat record #%d in '%s': wrong severity enum instance", index, self.who_i_am)
            else:
                severity = severity[threat[2]]
                rtn_code = report.add(threat[0], threat[1], severity, threat[3], threat[4], threat[5])

                if rtn_code != Meta.ok_code:
                    logging.error("could not append the threat record #%d (status code: %d) in '%s'", index, rtn_code, self.who_i_am)

            index += 1

    def finish(self):
        """It does nothing.
        """
