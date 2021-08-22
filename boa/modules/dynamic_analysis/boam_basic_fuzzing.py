
"""BOA module which uses fuzzing with basic binaries which are managed totally
from terminal.
"""

# Std libs
import re
import os
import time
import random
import logging
import tempfile
import subprocess
import multiprocessing

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Regex, Other
import utils
from exceptions import BOAModuleException

class BOAModuleBasicFuzzing(BOAModuleAbstract):
    """BOAModuleBasicFuzzing class. It implements the class BOAModuleAbstract.

    This class implements the general behaviour necessary to implement the basics
    of fuzzing.
    """

    def initialize(self):
        """It initializes the module.

        It handles the arguments, envvars and logging messages of the initialization.
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
        self.add_input_to_report = True

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
        if "add_input_to_report" in self.args:
            add_input_to_report = self.args["add_input_to_report"].lower().strip()

            if add_input_to_report == "false":
                self.add_input_to_report = False

                logging.debug("inputs are not going to be added to the report")

        logging.debug("iterations: %d", self.iterations)

        self.additional_args = []
        self.sandboxing_command = Other.modules_dynamic_analysis_sandboxing # TODO return code is 255 instead of the real return code when signals finish the execution (issue: https://github.com/netblue30/firejail/issues/4474)

        if "additional_args" in self.args:
            self.additional_args = re.findall(Regex.regex_which_respect_quotes_params, self.args["additional_args"])

            if not self.add_additional_args:
                logging.warning("there are additional args defined, but will not be added since 'add_additional_args' is 'false'")
        if "sandboxing_command" in self.args:
            self.sandboxing_command = re.findall(Regex.regex_which_respect_quotes_params, self.args["sandboxing_command"])
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
        """Worker for multiprocessing. This worker executes with subprocess
        a process with the provided input. It handles all the necessary about
        the different parts of the calling (e.g. sandboxing binary and args,
        instrumentation binary and args).

        Arguments:
            return_id (int): id which is returned as it was provided and is
                useful just to differentiate one worker from the others.
            input (str): input which is going to be provided to the target
                binary.
            binary_path (str): path to the target binary.

        Returns:
            tuple: *return_id*, return code of the execution and instrumentation
            result as *float*.

        Note:
            The subprocess module returns a negative return code when the execution
            has been finished by a signal. The return code which we return fixes
            this situation in order to have the same behaviour than other shells
            (e.g. /usr/bin/bash) and it returns 128 + return_code * -1, which is
            the same return code which others shells would return in case of signals.
        """
        instrumentation_tmp_file = tempfile.NamedTemporaryFile().name if self.instrumentation else None
        instrumentation = [ self.path_to_pin_binary, "-t",
                            f"{utils.get_current_path(path=__file__)}/instrumentation/PIN/{self.pintool}",
                            "-o", instrumentation_tmp_file, "--"] \
                            if self.instrumentation else []
        additional_args = self.additional_args
        sandboxing_command = self.sandboxing_command

        # TODO better process of quotes, backslashes and arguments splitting

        if not self.add_additional_args:
            additional_args = []

        # Measure time
        start = time.time()

        if not self.pipe:
            # Split taking into account quotes (doing this we avoid using "shell=True", which is not safe and
            #  might end up in unexpected behaviour; e.g. '|' as argument might be interpreted as pipe)
            binary_args = re.findall(Regex.regex_which_respect_quotes_params, input)

            if not self.subprocess_shell:
                # Remove quotes: this behaviour might change if Regex.regex_which_respect_quotes_params is modified
                binary_args = list(map(lambda arg: arg[1:-1] if (arg[0] == "\"" and arg[-1] == "\"") else arg, binary_args))
                additional_args = list(map(lambda arg: arg[1:-1] if (arg[0] == "\"" and arg[-1] == "\"") else arg, additional_args))
                sandboxing_command = list(map(lambda arg: arg[1:-1] if (arg[0] == "\"" and arg[-1] == "\"") else arg, sandboxing_command))

            args = sandboxing_command + instrumentation + [binary_path] + binary_args + additional_args
            args = ' '.join(args) if self.subprocess_shell else args    # Str if shell=True

            run = subprocess.run(args, capture_output=self.log_args_and_input_and_output, shell=self.subprocess_shell)

            output = (run.stdout, run.stderr)
        else:
            args = sandboxing_command + instrumentation + [binary_path] + additional_args
            args = ' '.join(args) if self.subprocess_shell else args    # Str if shell=True
            run = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=self.subprocess_shell)

            #input = chr(6 * 16) + "val" + input # TODO remove (it triggers LAVA-M base64 bug)

            output = run.communicate(input=input.encode())

        time_it_took_secs = time.time() - start
        returncode = run.returncode

        if returncode < 0:
            # subprocess signals (check man bash and subprocess documentation)
            ## for bash, if signal, the return code is return_code + n, where n is the signal n
            ## for subprocess, returns n * -1 when signal
            returncode = 128 + returncode * -1

        # Output without decoding in order to avoid the backslashes preprocessing
        if self.log_args_and_input_and_output:
            logging.debug("process %d: args: %s", os.getpid(), args)
            logging.debug("process %d: input: %s", os.getpid(), input.encode())
            logging.debug("process %d: (stdout, stderr): %s", os.getpid(), output)

        logging.debug("process %d: (return code, time): (%d, %.4f)", os.getpid(), returncode, time_it_took_secs)

        # Format: reward, (id, id_faked)
        instrumentation_result = [0.0, (random.randint(0, 0xFFFFFFFF), True)]

        # Instrumentation results
        if instrumentation_tmp_file is not None:
            with open(instrumentation_tmp_file) as f:
                instrumentation_result = list(map(lambda v: float(v), f.read().strip().split("\t")))

            if len(instrumentation_result) == 0:
                raise BOAModuleException(f"wrong instrumentation format: {len(instrumentation_result)} elements")
            if len(instrumentation_result) == 1:
                # Fake id of the execution
                instrumentation_result.append((int(instrumentation_result[0]), True))
            elif len(instrumentation_result) > 2:
                raise BOAModuleException(f"wrong instrumentation format: {len(instrumentation_result)} elements and max. is 2")
            else:
                # We are saying that the id has not been faked
                instrumentation_result[1] = (int(instrumentation_result[1]), False)

            logging.debug("process %d: instrumentation result (format: reward<tab>(id, id_faked)): %s", os.getpid(),
                          " ".join(map(lambda v: str(v), instrumentation_result)))

            # Remove file
            os.remove(instrumentation_tmp_file)

        return return_id, returncode, instrumentation_result, time_it_took_secs

    def process_worker_results(self, fails_instance, worker_return_list, worker_args):
        """Method which should be invoked by the main thread instead of by every
        individually worker. This method has been implemented apart of the main
        worker method because when multiprocessing is being run, every process
        have its own memory, and the results which would store in *self.threats*,
        they will be lost when the worker process finishes the execution.

        This method stores the found threats reported by every worker.

        Arguments:
            fails_instance (BOAFailModuleAbstract): fails module instance which
                will allow us to know if an execution failed or not.
            worker_return_list (list): list of tuples which contains the results
                from every worker (i.e. the return value of *self.process_worker*).
            worker_args (list): list with the arguments which were provided
                to the workers.

        Returns:
            list: list which contains if the execution of the workers failed or not.
        """
        fails = []

        for multiprocessing_idx, return_code, instrumentation, time_it_took_secs in worker_return_list:
            # Has the execution failed?
            fail = fails_instance.execution_has_failed(return_code)

            if fail:
                if self.add_input_to_report:
                    input = worker_args[multiprocessing_idx][1].encode() # Encoded in order to avoid backslashes interpretation
                else:
                    input = "-"

                self.threats.append((self.who_i_am,
                                     f"the input {input} returned the status code {return_code} (time: {time_it_took_secs:.4f} secs; "
                                     f"instrumentation: {' '.join(map(lambda v: str(v), instrumentation))})",
                                     "FAILED",
                                     "check if the fail is not a false positive",
                                     None, None))

            fails.append((multiprocessing_idx, fail))

        return fails

    def process_wrapper(self, runners_args, input_list=None):
        """Wrapper which contains all the behaviour which should contain
        *self.process*. This wrapper has been done since it might be necessary
        by other modules to run this module as dependency.

        This generator contains all the necessary behaviour to run the fuzzer.
        It is the main workflow of the module.

        Arguments:
            runners_args (dict): dict which contains data about the defined
                runner modules (e.g. fails module, inputs module).
            input_list (list): list of *str* which, if provided (default value
            is *None*), will be used as inputs for the execution of the target
            binary. If not defined, module from *runners_args* will be used to
            generate inputs.

        Returns:
            tuple: the tuple contains the arguments which were provided to every
            worker, the result of the execution of every worker and information
            about if the execution failed or not.

        Note:
            This method is a *generator*.
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

        worker_args = []

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

                logging.info("iteration %d of %d finished: %.2f%% completed", iteration + 1, self.iterations, ((iteration + 1) / self.iterations) * 100.0)
            else:
                logging.info("iteration %d of %d: multiprocessing", iteration + 1, self.iterations)

        if len(worker_args) != 0:
            # Only when self.iterations % self.processes != 0
            results = pool.starmap(self.process_worker, worker_args)

            # Process threats
            fails = self.process_worker_results(fails_instance, results, worker_args)

            yield worker_args, results, fails

            worker_args = []

            logging.info("iteration %d of %d: %.2f%% completed", self.iterations, self.iterations, (self.iterations / self.iterations) * 100.0)

        # Close pool
        pool.close()
        pool.terminate()

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
