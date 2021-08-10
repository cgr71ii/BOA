
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
        self.log_input_and_output = False
        self.add_additional_args = True

        if "pipe" in self.args:
            pipe = self.args["pipe"].lower().strip()

            if pipe == "true":
                self.pipe = True

                logging.debug("providing input through pipe")
        if "log_input_and_output" in self.args:
            log_input_and_output = self.args["log_input_and_output"].lower().strip()

            if log_input_and_output == "true":
                self.log_input_and_output = True

                logging.debug("logging input and output (every iteration will be displayed as debug)")
        if "add_additional_args" in self.args:
            add_additional_args = self.args["add_additional_args"].lower().strip()

            if add_additional_args == "false":
                self.add_additional_args = False

                logging.debug("additional args will be added (if defined any)")

        logging.debug("iterations: %d", self.iterations)

        self.additional_args = []

        if "additional_args" in self.args:
            self.additional_args = re.findall(Regex.regex_which_respect_quotes_params, self.args["additional_args"])

            if not self.add_additional_args:
                logging.warning("there are additional args defined, but will not be added since 'add_additional_args' is 'false'")

    def process(self, runners_args):
        """It implements a basic fuzzing technique.

        Arguments:
            runners_args (dict): dict with runners arguments.
        """
        binary_path = runners_args["binary"]

        # TODO multiprocessing (self.iterations)

        for _ in range(self.iterations):
            input = runners_args["inputs"]["instance"].get_another_input()
            additional_args = self.additional_args

            if not self.add_additional_args:
                additional_args = []

            # TODO better process of quotes, backslashes and arguments splitting

            if not self.pipe:
                # Split taking into account quotes (doing this we avoid using "shell=True", which is not safe and
                #  might end up in unexpected behaviour; e.g. '|' as argument might be interpreted as pipe)
                binary_args = re.findall(Regex.regex_which_respect_quotes_params, input)

                # Remove quotes: this behaviour might change if Regex.regex_which_respect_quotes_params is modified
                binary_args = list(map(lambda arg: arg[1:-1] if (arg[0] == "\"" and arg[-1] == "\"") else arg, binary_args))

                run = subprocess.run([binary_path] + binary_args + additional_args,
                                     capture_output=self.log_input_and_output)

                output = (run.stdout, run.stderr)
            else:
                run = subprocess.Popen([binary_path] + additional_args, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                output = run.communicate(input=input.encode())

            # Output without decoding in order to avoid the backslashes preprocessing
            if self.log_input_and_output:
                logging.debug("(input, (stdout, stderr)): (%s, %s)", input.encode(), output)

            # Has the execution failed?
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
