
"""BOA module which implements a genetic algorithm and uses a basic fuzzing module
as dependency in order to, in last instance, implement a greybox mutation-based fuzzer.

Different mutators are implemented and the crossover operation is based on select a
random point of the two selected elements and from that point, which is an offset,
part of one element is copied to the new element and the same from the other element.

The main dependency of this module is the module *boam_basic_fuzzing*.
"""

# Std libs
import random
import logging

# Own libs
from boam_abstract import BOAModuleAbstract
import utils
from exceptions import BOAModuleException

class BOAModuleGenAlgFuzzing(BOAModuleAbstract):
    """BOAModuleGenAlgFuzzing class. It implements the class BOAModuleAbstract.

    This class implements the general behaviour necessary to implement a genetic
    algorithm using a fuzzer module as dependency.
    """

    def initialize(self):
        """It initializes the module.

        Moreover, it handles the values which are not compatible based on the
        provided arguments.
        """
        if "boam_basic_fuzzing.BOAModuleBasicFuzzing" not in self.dependencies:
            raise BOAModuleException("dependency 'boam_basic_fuzzing.BOAModuleBasicFuzzing' is necessary")
        if "instance" not in self.dependencies["boam_basic_fuzzing.BOAModuleBasicFuzzing"]:
            raise BOAModuleException("callback 'instance' in 'boam_basic_fuzzing.BOAModuleBasicFuzzing' is necessary")

        # Dependency instance
        self.genalg_child_instance = self.dependencies["boam_basic_fuzzing.BOAModuleBasicFuzzing"]["instance"]()

        # Args
        self.epochs = 1 if not utils.is_key_in_dict(self.args, "epochs") else int(self.args["epochs"])
        self.population = self.genalg_child_instance.iterations
        self.elitism = 1 if not utils.is_key_in_dict(self.args, "elitism") else int(self.args["elitism"])
        self.mutation_rate = 0.05 if not utils.is_key_in_dict(self.args, "mutation_rate") else float(self.args["mutation_rate"])
        self.crossover_rate = 0.95 if not utils.is_key_in_dict(self.args, "crossover_rate") else float(self.args["crossover_rate"])
        self.mutation_regex = "^.$" if not utils.is_key_in_dict(self.args, "mutation_regex") else self.args["mutation_regex"]
        self.mutation_binary_granularity = False
        self.add_input_to_report = True
        self.elements_from_input_module_new_population = 0 if not utils.is_key_in_dict(self.args, "elements_from_input_module_new_population") else int(self.args["elitism"])
        self.report_instance = None # It will set in the process method (maybe)
        self.print_threats_while_running = False
        self.execution_ids = set()
        self.power_schedule = "exploit" if not utils.is_key_in_dict(self.args, "power_schedule") else self.args["power_schedule"]
        self.power_schedule_beta = 1.0 if not utils.is_key_in_dict(self.args, "power_schedule_beta") else float(self.args["power_schedule_beta"])

        if "mutation_binary_granularity" in self.args:
            mutation_binary_granularity = self.args["mutation_binary_granularity"].lower().strip()

            if mutation_binary_granularity == "true":
                self.mutation_binary_granularity = True
                self.mutation_regex = self.mutation_regex.encode()

                logging.debug("working with binary instead of char granularity")
                logging.warning("provided mutation regex will be treated as binary due to the binary granularity")
        if "print_threats_while_running" in self.args:
            print_threats_while_running = self.args["print_threats_while_running"].lower().strip()

            if print_threats_while_running == "true":
                self.print_threats_while_running = True

                logging.warning("threats will be displayed while running, but this option will 'fake' the reporting numbers since the found threats of this module will not be taked into account")
        if "add_input_to_report" in self.args:
            add_input_to_report = self.args["add_input_to_report"].lower().strip()

            if add_input_to_report == "false":
                self.add_input_to_report = False

                logging.debug("inputs are not going to be added to the report")

        if self.elitism > self.population:
            logging.warning("elitism value (%d) is higher than population (%d): elitism value is "
                            "going to be set to population value", self.elitism, self.population)

            self.elitism = self.population
        if self.elements_from_input_module_new_population > self.population:
            logging.warning("elements_from_input_module_new_population value (%d) is higher than population (%d): "
                            "elements_from_input_module_new_population value is going to be set to population value",
                            self.elements_from_input_module_new_population, self.population)

            self.elements_from_input_module_new_population = self.population
        if self.elitism + self.elements_from_input_module_new_population > self.population:
            q = self.elitism + self.elements_from_input_module_new_population

            raise BOAModuleException(f"elitism + elements_from_input_module_new_population value ({q}) is higher "
                                     f"than population ({self.population})")
        elif self.elitism + self.elements_from_input_module_new_population == self.population:
            logging.warning("since elitism + elements_from_input_module_new_population (%d) is equal to the population size (%d), "
                            "there will not be crossover, so the genetic algorithm will just be a 'fair' selection of "
                            "elements based on rewards and random mutations: it is highly recommended to increase the "
                            "population size or decrease either elitism or elements_from_input_module_new_population",
                            self.elitism + self.elements_from_input_module_new_population, self.population)
        if self.power_schedule not in ("fast", "coe", "explore", "quad", "lin", "exploit"):
            raise BOAModuleException(f"unknown power schedule ('{self.power_schedule}'); allowed power schedules are: "
                                     "'fast', 'coe', 'explore', 'quad', 'lin', 'exploit'")

        logging.info("using power schedule '%s' (beta value: %.2f)", self.power_schedule, self.power_schedule_beta)

        if self.power_schedule_beta < 1.0:
            logging.warning("you set a beta value lower than 1.0, and this might break the expected behaviour of the power schedule")

    def crossover(self, inputs_instance, population, rewards):
        """It performs the crossover operation using the Roulette Wheel Selection
        algorithm.

        Arguments:
            inputs_instance (BOAInputModuleAbstract): input module instance which will be
                used to generate random inputs if *self.elements_from_input_module_new_population*
                > 0.
            population (list): list of children which will be used to select the best children
                if *self.elitism* > 0.
            rewards (list): reward which children (i.e. *population*) obtained.

        Returns:
            list: new population.
        """
        new_population = []
        generate_n_children = self.elements_from_input_module_new_population

        # Check if no children were provided
        if len(rewards) == 0:
            logging.warning("no children were provided for the crossover: generating all of them")

            generate_n_children = self.population

        # Add elements from input module
        while len(new_population) < generate_n_children:
            new_population.append(inputs_instance.get_another_input())

        # Select best children
        for _, idx in sorted(zip(rewards, range(len(rewards))), reverse=True):
            if len(new_population) - self.elements_from_input_module_new_population < self.elitism:
                new_population.append(population[idx])
            else:
                break

        # Select children based on roulette wheel selection algorithm from the provided population
        while len(new_population) < self.population:
            father_idx = utils.roulette_wheel_selection(rewards)
            mother_idx = utils.roulette_wheel_selection(rewards)
            father = population[father_idx]
            mother = population[mother_idx]
            r = random.random()

            if r < self.crossover_rate:
                # Crossover
                offset = random.randint(0, max(max(len(father), len(mother)) - 1, 0))
                child = father[:offset] + mother[offset:]

                new_population.append(child)
            else:
                # Do not crossover
                r = random.random()

                if r <= 0.5:
                    # Add father
                    new_population.append(father)
                else:
                    # Add mother
                    new_population.append(mother)

        return new_population

    def mutation_replace(self, child):
        """Mutator which replaces elements of the provided child.

        Arguments:
            child (str): element which is going to be mutated.

        Returns:
            str: *child* mutated.

        Note:
            The provided arguments and returned value will be str
            or bytes depending on the value of *self.mutation_binary_granularity*.
        """
        new_child = b"" if self.mutation_binary_granularity else ""

        for idx in range(len(child)):
            r = random.random()

            if r < self.mutation_rate:
                # Mutate
                new_child_tmp = utils.get_random_utf8_seq(1, regex=self.mutation_regex if not self.mutation_binary_granularity
                                                                                       else self.mutation_regex.decode())
                new_child += new_child_tmp.encode() if self.mutation_binary_granularity else new_child_tmp
            else:
                # Do not mutate
                new_child += chr(child[idx]).encode("utf-8", "ignore") if self.mutation_binary_granularity else child[idx]

        return new_child

    def mutation_insert(self, child):
        """Mutator which inserts new elements in the provided child.

        Arguments:
            child (str): element which is going to be mutated.

        Returns:
            str: *child* mutated.

        Note:
            The provided arguments and returned value will be str
            or bytes depending on the value of *self.mutation_binary_granularity*.
        """
        new_child = b"" if self.mutation_binary_granularity else ""
        idx = 0

        while idx < len(child):
            r = random.random()
            child_char = chr(child[idx]).encode("utf-8", "ignore") if self.mutation_binary_granularity \
                                                                               else child[idx]

            if r < self.mutation_rate:
                # Mutate
                new_char = utils.get_random_utf8_seq(1, regex=self.mutation_regex if not self.mutation_binary_granularity
                                                                                  else self.mutation_regex.decode())
                new_char = new_char.encode() if self.mutation_binary_granularity else new_char

                new_child += child_char + new_char
            else:
                # Do not mutate
                new_child += child_char

            idx += 1

        return new_child

    def mutation_swap(self, child):
        """Mutator which swaps elements of the provided child.

        Arguments:
            child (str): element which is going to be mutated.

        Returns:
            str: *child* mutated.

        Note:
            The provided arguments and returned value will be str
            or bytes depending on the value of *self.mutation_binary_granularity*.
        """
        new_child = [chr(c).encode("utf-8", "ignore") if self.mutation_binary_granularity else c for c in child] # List of characters

        for idx, char in enumerate(new_child):
            r = random.random()

            if r < self.mutation_rate:
                # Mutate
                swap_idx = random.randint(0, len(new_child) - 1)
                swap_char = new_child[swap_idx]

                new_child[idx] = swap_char
                new_child[swap_idx] = char
            else:
                # Do not mutate
                pass

        return (b"" if self.mutation_binary_granularity else "").join(new_child) # Return str

    def mutation_delete(self, child):
        """Mutator which deletes elements of the provided child.

        Arguments:
            child (str): element which is going to be mutated.

        Returns:
            str: *child* mutated.

        Note:
            The provided arguments and returned value will be str
            or bytes depending on the value of *self.mutation_binary_granularity*.
        """
        new_child = b"" if self.mutation_binary_granularity else ""

        for idx in range(len(child)):
            r = random.random()

            if r < self.mutation_rate:
                # Mutate -> do not add = remove
                pass
            else:
                # Do not mutate
                new_child += chr(child[idx]).encode("utf-8", "ignore") if self.mutation_binary_granularity else child[idx]

        return new_child

    def mutation(self, population):
        """This method performs the mutations of the provided population.

        The mutator which will be used will be selected randomly for each
        child of the population.

        Arguments:
            population (list): list of children which will be mutated.

        Returns:
            list: mutated new population based on the initial *population*.
        """
        new_population = []
        mutators = [self.mutation_replace,
                    self.mutation_insert,
                    self.mutation_swap,
                    self.mutation_delete]

        for child in population:
            if self.mutation_binary_granularity:
                child = child.encode("utf-8", "ignore")

            new_child = random.choice(mutators)(child)

            if self.mutation_binary_granularity:
                #new_child = new_child.decode("utf-8", "backslashreplace")
                new_child = new_child.decode("utf-8", "ignore")

            new_population.append(new_child)

        return new_population

    def process(self, runners_args):
        """It implements a basic fuzzing technique.

        Arguments:
            runners_args (dict): dict with runners arguments.
        """
        current_population = None

        # Check if the args were provided coded
        if utils.is_key_in_dict(runners_args, "__args__"):
            self.report_instance = runners_args["__report_instance__"] if utils.is_key_in_dict(runners_args, "__report_instance__") \
                                                                       else self.report_instance
            runners_args = runners_args["__args__"]
        # Check if is possible to print the threats while running (report instance is mandatory for this option)
        if (self.report_instance is None and self.print_threats_while_running):
            self.print_threats_while_running = False

            logging.warning("the report instance was not provided and you set the printing of the threats while running, but this is not possible because the report instance is mandatory (this problema might be related to the selected lifecycle module)")

        average_time = 0.0
        total_executions = 0
        inputs_which_have_been_executed_n_times = {}
        inputs_with_same_path_executed_n_times = {}
        total_inputs_processed = 0

        for epoch in range(self.epochs):
            current_population_input = []
            current_population_reward = []
            current_population_id = []

            for yield_return in self.genalg_child_instance.process_wrapper(runners_args, input_list=current_population):
                if yield_return is None:
                    break

                # Process all results or part of them (multiprocessing)
                worker_args, worker_results, output_status = yield_return

                # Sort in order to avoid problems with possible misordering from multiprocessing
                worker_args = sorted(worker_args)
                worker_results = sorted(worker_results)
                output_status = sorted(output_status)

                # Get relevant values for the genalg
                for idx, (input, results, fail) in enumerate(zip(worker_args, worker_results, output_status)):
                    if (input[0] != results[0] or input[0] != fail[0]):
                        logging.warning("epoch %d child unk. idx %d: mismatch of child idxs (%d vs %d vs %d): skipping",
                                        idx, epoch, input[0], results[0], fail[0])
                        continue

                    total_executions += 1

                    # Relevant values
                    input_value = input[1]
                    return_code = results[1]
                    instrumentation_reward = results[2][0]
                    instrumentation_id = results[2][1]
                    instrumentation_id_value = instrumentation_id[0]
                    instrumentation_id_faked = instrumentation_id[1]
                    time_it_took_secs = results[3]
                    fail_bool = fail[1]
                    reward = 0.0

                    # Update average value iteratively
                    average_time = (average_time * (total_executions - 1) + time_it_took_secs) / total_executions

                    # Update values
                    input_value_hash = hash(input_value)

                    if input_value_hash not in inputs_which_have_been_executed_n_times:
                        inputs_which_have_been_executed_n_times[input_value_hash] = 0
                    if instrumentation_id_value not in inputs_with_same_path_executed_n_times:
                        inputs_with_same_path_executed_n_times[instrumentation_id_value] = 0

                    inputs_which_have_been_executed_n_times[input_value_hash] += 1 # s(i)
                    inputs_with_same_path_executed_n_times[instrumentation_id_value] += 1 # f(i)
                    mu = (total_inputs_processed + 1) / (len(self.execution_ids) + (1 if instrumentation_id_value not in self.execution_ids else 0))
                    beta = self.power_schedule_beta
                    alpha = instrumentation_reward * (2 if fail_bool else 1) # base reward
                    alpha *= 1.0 + (1.0 if time_it_took_secs < average_time else -1.0) * (average_time / time_it_took_secs - 1.0) # alpha(i)

                    # Is it available an ID of the executed path?
                    if not instrumentation_id_faked:
                        # Check if the input is useful

                        if instrumentation_id_value not in current_population_id:
                            current_population_id.append(instrumentation_id[0])
                        else:
                            # This input is not useful (same path execution)

                            total_inputs_processed += 1

                            # Do not report threat since should has been reported earlier
                            continue

                    # Update reward
                    ## The more path coverage, the better!
                    #reward += instrumentation_reward * (2 if fail_bool else 1)
                    ## Update based on the time it took the execution (relative): the faster, the better!
                    ### 1.0 + 1.0 if better time than avg else -1.0 * times better or worse
                    #reward *= 1.0 + (1.0 if time_it_took_secs < average_time else -1.0) * (average_time / time_it_took_secs - 1.0) # alpha(i)
                    ## Reward the new paths
                    #reward *= 2.0 if instrumentation_id_value not in self.execution_ids else 1.0

                    # Power schedules
                    ## We are using power schedules for reward instead of number of mutations for a specific input
                    ##  but this might be consider similar since a higher reward in a genetic algorithm means
                    ##  a higer likelihood of be selected across epochs and mutation will be applied to this seed
                    if self.power_schedule == "fast":
                        ok = False
                        fix = 0

                        while not ok:
                            try:
                                reward = (alpha / beta) * \
                                         ((2 ** (inputs_which_have_been_executed_n_times[input_value_hash] - fix)) / \
                                          inputs_with_same_path_executed_n_times[instrumentation_id_value])
                                ok = True
                            except OverflowError:
                                if fix == 0:
                                    logging.warning("overflow detected while calculating the reward: trying to fix it...")

                                fix += 1

                    elif self.power_schedule == "coe":
                        if inputs_with_same_path_executed_n_times[instrumentation_id_value] > mu:
                            reward = 0.0
                        else:
                            ok = False
                            fix = 0

                            try:
                                reward = (alpha / beta) * (2 ** (inputs_which_have_been_executed_n_times[input_value_hash] - fix))
                                ok = True
                            except OverflowError:
                                if fix == 0:
                                    logging.warning("overflow detected while calculating the reward: trying to fix it...")

                                fix += 1

                    elif self.power_schedule == "explore":
                        reward = (alpha / beta)
                    elif self.power_schedule == "quad":
                        reward = (alpha / beta) * \
                                 ((inputs_which_have_been_executed_n_times[input_value_hash] ** 2) / \
                                  inputs_with_same_path_executed_n_times[instrumentation_id_value])
                    elif self.power_schedule == "lin":
                        reward = (alpha / beta) * \
                                 (inputs_which_have_been_executed_n_times[input_value_hash] / \
                                  inputs_with_same_path_executed_n_times[instrumentation_id_value])
                    elif self.power_schedule == "exploit":
                        reward = alpha

                    # Add values to the population (new child)
                    current_population_input.append(input_value)
                    current_population_reward.append(reward)

                    if self.add_input_to_report:
                        input_value = input_value.encode()
                    else:
                        input_value = "-"

                    # Threat? Add only if not had not been observed before
                    if (fail_bool and instrumentation_id_value not in self.execution_ids):
                        instrumentation_info = "" if instrumentation_id_faked else f" (id: {instrumentation_id_value})"

                        self.threats.append((self.who_i_am,
                                             f"genetic algorithm (epoch {epoch + 1}): the input {input_value} "
                                             f"returned the status code {return_code}{instrumentation_info}",
                                             "FAILED",
                                             "check if the fail is not a false positive",
                                             None, None))

                        self.execution_ids.add(instrumentation_id[0])

                    total_inputs_processed += 1

            # TODO multiprocessing? problem with mutator choice becuse same will be always selected?

            # Crossover
            current_population = self.crossover(runners_args["inputs"]["instance"], current_population_input, current_population_reward)

            # Mutation
            current_population = self.mutation(current_population)

            # Check if we have available the report instance
            if self.report_instance is not None:
                # Save current threats in order to avoid filling up the memory
                self.save(self.report_instance)

                # Print all threats?
                if self.print_threats_while_running:
                    # WARNING: this option will 'fake' the counts of the final report, since the threats of this module will not be taken into account

                    if self.who_i_am in self.report_instance.summary:
                        for t in self.report_instance.summary[self.who_i_am]:
                            self.report_instance.pretty_print_tuple(t)

                        # Remove threats of the final report in order to avoid printing the threats twice
                        del self.report_instance.summary[self.who_i_am]

                # Remove current threats
                self.threats = []

            logging.debug("average time of execution: %.4f", average_time)
            logging.info("epoch %d of %d finished: %.2f%% completed", epoch + 1, self.epochs, ((epoch + 1) / self.epochs) * 100.0)

    def clean(self):
        """It does nothing.
        """

    def finish(self):
        """It does nothing.
        """
