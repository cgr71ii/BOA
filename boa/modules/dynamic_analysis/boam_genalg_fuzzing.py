
"""BOA module which uses fuzzing with basic binaries which are managed totally
from terminal.
"""

# TODO finish and check docstrings

# Std libs
import random
import logging

# Own libs
from boam_abstract import BOAModuleAbstract
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

        # Dependency instance
        self.genalg_child_instance = self.dependencies["boam_basic_fuzzing.BOAModuleBasicFuzzing"]["instance"]()

        # Args
        self.epochs = 1 if not utils.is_key_in_dict(self.args, "epochs") else int(self.args["epochs"])
        self.population = self.genalg_child_instance.iterations
        self.elitism = 1 if not utils.is_key_in_dict(self.args, "elitism") else int(self.args["elitism"])
        self.mutation_rate = 0.05 if not utils.is_key_in_dict(self.args, "mutation_rate") else float(self.args["mutation_rate"])
        self.crossover_rate = 0.95 if not utils.is_key_in_dict(self.args, "crossover_rate") else float(self.args["crossover_rate"])
        self.mutation_regex = "^.$" if not utils.is_key_in_dict(self.args, "mutation_regex") else self.args["mutation_regex"]

        if self.elitism > self.population:
            logging.warning("elitism value (%d) is higher than population (%d): elitism value is "
                            "going to be set to population value", self.elitism, self.population)

            self.elitism = self.population

    def crossover(self, population, rewards):
        """
        """
        new_population = []

        # Select best children
        for reward, idx in sorted(zip(rewards, range(len(rewards))), reverse=True):
            if len(new_population) < self.elitism:
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
                child = father[:len(father) // 2] + mother[len(mother) // 2:]

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

    def mutation(self, population):
        """
        """
        new_population = []

        for child in population:
            new_child = ""

            for idx in range(len(child)):
                r = random.random()

                if r < self.mutation_rate:
                    # Mutate
                    new_child += utils.get_random_utf8_seq(1, regex=self.mutation_regex)
                else:
                    # Do not mutate
                    new_child += child[idx]

            new_population.append(new_child)

        return new_population

    def process(self, runners_args):
        """It implements a basic fuzzing technique.

        Arguments:
            runners_args (dict): dict with runners arguments.
        """
        current_population = None

        for epoch in range(self.epochs):
            current_population_input = []
            current_population_reward = []

            for yield_return in self.genalg_child_instance.process_wrapper(runners_args, input_list=current_population):
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
                    input_value = input[1]
                    return_code = instrumentation[1]
                    instrumentation_reward = instrumentation[2]
                    fail_bool = fail[1]

                    # Threat?
                    if fail_bool:
                        self.threats.append((self.who_i_am,
                                             f"genetic algorithm (epoch {epoch}): the input {input_value.encode()} returned the status code {return_code}",
                                             "FAILED",
                                             "check if the fail is not a false positive",
                                             None, None))

                    # Add values to the population (new child)
                    current_population_input.append(input_value)
                    current_population_reward.append(instrumentation_reward)

            # Crossover
            current_population = self.crossover(current_population_input, current_population_reward)

            # Mutation
            current_population = self.mutation(current_population)

            logging.info("epoch %d of %d: %.2f completed", epoch + 1, self.epochs, (epoch / self.epochs) * 100.0)

    def clean(self):
        """It does nothing.
        """

    def finish(self):
        """It does nothing.
        """
