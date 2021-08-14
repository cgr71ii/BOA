
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

class BOAModuleBasicFuzzing(BOAModuleAbstract):
    """BOAModuleBasicFuzzing class. It implements the class BOAModuleAbstract.

    This class implements the general behaviour necessary to implement the basics
    of fuzzing.
    """

    def initialize(self):
        """It initializes the module.
        """
        self.iterations = 1 if not utils.is_key_in_dict(self.args, "iterations") else int(self.args["iterations"])
        self.pipe = False
        self.log_args_and_input_and_output = False
        self.add_additional_args = True
        self.path_to_pin_binary = None
        self.pintool = None
        self.instrumentation = False
        self.subprocess_shell = False
        self.processes = 1 if not utils.is_key_in_dict(self.args, "processes") else min(int(self.args["processes"]), self.iterations)
        self.skip_process = False

        logging.debug("using %d processes", self.processes)

        cores_available = multiprocessing.cpu_count()

        if self.processes > cores_available:
            logging.warning("you set a number of processes higher than the available cores (%d): the best value should be %d,"
                            " not %d since it might achieve even a worse performance", cores_available, cores_available, self.iterations)
        if (self.processes > 1 and cores_available > 1):
            logging.warning("multiprocessing might lead to unordered messages")

        if "pipe" in self.args:
            pipe = self.args["pipe"].lower().strip()

            if pipe == "true":
                self.pipe = True

                logging.debug("providing input through pipe")
        if "log_args_and_input_and_output" in self.args:
            log_args_and_input_and_output = self.args["log_args_and_input_and_output"].lower().strip()

            if log_args_and_input_and_output == "true":
                self.log_args_and_input_and_output = True

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
        if "path_to_pin_binary" in self.args:
            self.path_to_pin_binary = self.args["path_to_pin_binary"]
        else: # Alternative method to get PIN path
            envvar = utils.get_environment_varibles("PIN_BIN")

            if "PIN_BIN" in envvar:
                self.path_to_pin_binary = envvar["PIN_BIN"]
        if "pintool" in self.args:
            self.pintool = self.args["pintool"]
        if "subprocess_shell" in self.args:
            subprocess_shell = self.args["subprocess_shell"].lower().strip()

            if subprocess_shell == "true":
                self.subprocess_shell = True

                logging.debug("using subprocess shell=True")
        if "skip_process" in self.args:
            skip_process = self.args["skip_process"].lower().strip()

            if skip_process == "true":
                self.skip_process = True

                logging.debug("skipping process")

        if ((self.path_to_pin_binary is None) ^ (self.pintool is None)):
            logging.warning("if you want to apply instrumentation, 'path_to_pin_binary' (or 'PIN_BIN' envvar) and 'pintool' have to be both defined")

            self.path_to_pin_binary = None
            self.pintool = None
        if (self.path_to_pin_binary is not None and self.pintool is not None):
            self.instrumentation = True

            logging.debug("using instrumentation (path: '%s') with pintool '%s'", self.path_to_pin_binary, self.pintool)

    def process_worker(self, return_id, input, binary_path):
        """
        """
        instrumentation_tmp_file = tempfile.NamedTemporaryFile().name if self.instrumentation else None
        instrumentation = [ self.path_to_pin_binary, "-t",
                            f"{utils.get_current_path(path=__file__)}/instrumentation/PIN/{self.pintool}",
                            "-o", instrumentation_tmp_file, "--"] \
                            if self.instrumentation else []
        additional_args = self.additional_args

        # TODO better process of quotes, backslashes and arguments splitting

        if not self.add_additional_args:
            additional_args = []

        if not self.pipe:
            # Split taking into account quotes (doing this we avoid using "shell=True", which is not safe and
            #  might end up in unexpected behaviour; e.g. '|' as argument might be interpreted as pipe)
            binary_args = re.findall(Regex.regex_which_respect_quotes_params, input)

            if not self.subprocess_shell:
                # Remove quotes: this behaviour might change if Regex.regex_which_respect_quotes_params is modified
                binary_args = list(map(lambda arg: arg[1:-1] if (arg[0] == "\"" and arg[-1] == "\"") else arg, binary_args))

            args = instrumentation + [binary_path] + binary_args + additional_args
            args = ' '.join(args) if self.subprocess_shell else args    # Str if shell=True

            run = subprocess.run(args, capture_output=self.log_args_and_input_and_output, shell=self.subprocess_shell)

            output = (run.stdout, run.stderr)
        else:
            args = instrumentation + [binary_path] + additional_args
            args = ' '.join(args) if self.subprocess_shell else args    # Str if shell=True
            run = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=self.subprocess_shell)

            output = run.communicate(input=input.encode())

        # Output without decoding in order to avoid the backslashes preprocessing
        if self.log_args_and_input_and_output:
            logging.debug("process %s: args: %s", os.getpid(), args)
            logging.debug("process %s: (input, (stdout, stderr)): (%s, %s)", os.getpid(), input.encode(), output)

        instrumentation_result = 0.0

        # Instrumentation results
        if instrumentation_tmp_file is not None:
            with open(instrumentation_tmp_file) as f:
                instrumentation_result = float(f.read().strip())

            logging.debug("process %s: instrumentation result: %.2f", os.getpid(), instrumentation_result)

            # Remove file
            os.remove(instrumentation_tmp_file)

        return return_id, run.returncode, instrumentation_result

    def process_worker_results(self, fails_instance, worker_return_list, worker_args):
        """
        """
        fails = []

        for multiprocessing_idx, return_code, instrumentation_result in worker_return_list:
            # Has the execution failed?
            fail = fails_instance.execution_has_failed(return_code)

            if fail:
                input = worker_args[multiprocessing_idx][1].encode() # Encoded in order to avoid backslashes interpretation

                self.threats.append((self.who_i_am,
                                     f"the input {input} returned the status code {return_code}",
                                     "FAILED",
                                     "check if the fail is not a false positive",
                                     None, None))

            fails.append((multiprocessing_idx, fail))

        return fails

    def process_wrapper(self, runners_args, input_list=None):
        """
        """
        binary_path = runners_args["binary"]
        fails_instance = runners_args["fails"]["instance"]
        workers = self.processes
        pool = multiprocessing.Pool(processes=self.processes)
        worker_args = []

        if (input_list is not None and len(input_list) != self.iterations):
            if len(input_list) < self.iterations:
                logging.warning("not enought inputs were provided: %d inputs were provided, so %d inputs"
                                " are going to be generated", len(input_list), self.iterations - len(input_list))
            else:
                logging.warning("too many inputs were provided, and not all of them are going to be used:"
                                " only the %d first elements are going to be used", self.iterations)

        for idx, iteration in enumerate(range(self.iterations)):
            if (input_list is not None and idx < len(input_list)):
                input = input_list[idx]
            else:
                input = runners_args["inputs"]["instance"].get_another_input()

            worker_args.append((iteration % workers, input, binary_path,))

            if len(worker_args) >= workers:
                results = pool.starmap(self.process_worker, worker_args)

                # Process threats
                fails = self.process_worker_results(fails_instance, results, worker_args)

                yield worker_args, results, fails

                worker_args = []

                logging.info("iteration %d of %d: %.2f completed", iteration + 1, self.iterations, (iteration / self.iterations) * 100.0)
            else:
                logging.info("iteration %d of %d: multiprocessing", iteration + 1, self.iterations)

        if len(worker_args) != 0:
            # Only when self.iterations % self.processes != 0
            results = pool.starmap(self.process_worker, worker_args)

            # Process threats
            fails = self.process_worker_results(fails_instance, results, worker_args)

            yield worker_args, results, fails

            worker_args = []

        logging.info("100.00% completed")

        yield

    def process(self, runners_args):
        """It implements a basic fuzzing technique.

        Arguments:
            runners_args (dict): dict with runners arguments.
        """
        if self.skip_process:
            return

        for _ in self.process_wrapper(runners_args):
            pass

    def clean(self):
        """It does nothing.
        """

    def finish(self):
        """It does nothing.
        """
