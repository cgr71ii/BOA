
"""BOA module which uses fuzzing with basic binaries which are managed totally
from terminal.
"""

# Std libs
import re
import logging
import subprocess

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta, Regex
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

        self.additional_args = []

        if "additional_args" in self.args:
            self.additional_args = re.findall(Regex.regex_which_respect_quotes_params, self.args["additional_args"])

    def process(self, runners_args):
        """It implements a basic fuzzing technique.

        Arguments:
            runners_args (dict): dict with runners arguments.
        """
        binary_path = runners_args["binary"]

        for _ in range(self.iterations):
            input = runners_args["inputs"]["instance"].get_another_input()

            # TODO parametrize the adding of the additional args (default value: True)?
            # TODO check that the calls to subprocess are working

            if not self.pipe:
                binary_args = re.findall(Regex.regex_which_respect_quotes_params, input)
                run = subprocess.run([binary_path] + binary_args + self.additional_args)
            else:
                run = subprocess.Popen([binary_path] + self.additional_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

                run.communicate(input=input.encode())

                # Output without decoding in order to avoid the backslashes preprocessing
                #output = run.communicate(input=input.encode())
                #logging.debug("(input, output): (%s, %s)", input.encode(), output[0])

            fail = runners_args["fails"]["instance"].execution_has_failed(run.returncode)

            if fail:
                # The input is encoded in order to avoid backslashes interpretation
                self.threats.append((self.who_i_am,
                                     f"the input {input.encode()} returned the status code {run.returncode}",
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
