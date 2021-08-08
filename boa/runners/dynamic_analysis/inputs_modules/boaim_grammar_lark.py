
# TODO docstrings

# Std libs
import random
import logging

# 3rd libs
from lark import Lark
import exrex

# Own libs
from boaim_abstract import BOAInputModuleAbstract
from utils import get_current_path

class BOAIMGrammarLark(BOAInputModuleAbstract):
    """
    """

    def initialize(self):
        """
        """
        # Parameters from rules file
        self.soft_limit_rules = 100
        self.soft_limit_depth = 1
        self.hard_limit_rules = 200

        if "soft_limit_rules" in self.args:
            self.soft_limit_rules = int(self.args["soft_limit_rules"])
        if "soft_limit_depth" in self.args:
            self.soft_limit_depth = int(self.args["soft_limit_depth"])
        if "hard_limit_rules" in self.args:
            self.hard_limit_rules = int(self.args["hard_limit_rules"])
        if self.soft_limit_rules < 0:
            logging.warning("soft limit value is not valid: changing from %d to 0", self.soft_limit_rules)

            self.soft_limit_rules = 0
        if self.soft_limit_depth < 0:
            logging.warning("soft limit depth is not valid: changing from %d to 0", self.soft_limit_depth)

            self.soft_limit_depth = 0
        if self.hard_limit_rules < self.soft_limit_rules:
            logging.warning("hard limit value is not valid, since is lower than the soft limit: setting hard "
                            "limit to soft limit: from %d to %d", self.hard_limit_rules, self.soft_limit_rules)

            self.hard_limit_rules = self.soft_limit_rules

        logging.debug("soft limit of recursive rules: %d", self.soft_limit_rules)
        logging.debug("soft limit depth: %d", self.soft_limit_depth)
        logging.debug("hard limit of recursive rules: %d", self.hard_limit_rules)

        # Initialization of the grammar parser
        self.grammar, self.likelihood = self.get_grammar()
        self.parser = Lark(self.grammar)
        self.parser = {'parser': self.parser,
                       'rules': self.parser.rules,
                       'terminals': self.parser.terminals,}

        self.index = self.index_grammar()
        self.fix_partial_likelihood()

        if "start" not in self.index["rules_names"]:
            raise BOAInputModuleAbstract("rule 'start' not found in the provided grammar")

    def get_random_rule(self, rule):
        """Obtain a random rule from the provided *rule*.
        We use the roulette wheel selection algorithm to select the rule
        with the higher likelihood.

        Arguments:
            rule (str): rule to start from the graph.

        Returns:
            tuple: 
        """
        n_rules = len(self.index["graph"][rule])

        if n_rules == 0:
            raise BOAInputModuleAbstract(f"there was 0 dependencies in the graph for the rule '{rule}'")

        likelihood = sorted(self.likelihood[rule].items(), key=lambda item: item[1]) # <
        acummulated = 0.0
        index = likelihood[-1][0]

        # Update likelihood in order to obtain the acummulated values
        for idx, (l_idx, l_l) in enumerate(likelihood):
            acummulated += l_l
            likelihood[idx] = (l_idx, acummulated)

        # Obtain index with higher likelihood
        random_number = random.random()

        for l_idx, l_l in likelihood:
            if l_l >= random_number:
                index = l_idx
                break

#        index = random.randint(0, n_rules - 1)

        return self.index["graph"][rule][index]

    def minimize_non_terminals_from_rule(self, rule, depth=0, first_call=True):
        """It iterates the childs in depth of the *rule* and minimizes the
        number of *NonTerminal* symbols.

        Arguments:
            rule (str): rule of *self.index["graph"]* (key).
            depth (int): depth which we are going to recursive in order to
                minimize the number of *NonTerminal* symbols.
            first_call (bool): variable which must not be set, since is used
                to know when the used called this function

        Returns:
            tuple: element of *self.index["graph"]*.

        Note:
            This method might lead to a buffer overflow if *depth* is too
            high due to recursivity. This is even worse if the grammar has
            too many branches.
        """
        if depth <= 0:
            rules_non_terminal_symbols = [0] * len(self.index["graph"][rule])

            for idx, r in enumerate(self.index["graph"][rule]):
                for rr_name, rr_type in r:
                    if rr_type == "NonTerminal":
                        rules_non_terminal_symbols[idx] += 1

            if not first_call:
                return rules_non_terminal_symbols
        else:
            rules_non_terminal_symbols = [0] * len(self.index["graph"][rule])

            for idx, r in enumerate(self.index["graph"][rule]):
                for rr_name, rr_type in r:
                    if rr_type == "NonTerminal":
                        rules_non_terminal_symbols[idx] += \
                            sum(self.minimize_non_terminals_from_rule(rr_name, depth=depth - 1, first_call=False))
                

            if not first_call:
                return rules_non_terminal_symbols

        # First call
        return self.index["graph"][rule][rules_non_terminal_symbols.index(min(rules_non_terminal_symbols))]

    def generate_input(self):
        """
        """
        input = ""
        stack = []
        recursive_rules = 0
        soft_limit = False

        new_selected_rule = self.get_random_rule("start")
        stack.extend(list(reversed(new_selected_rule)))

        while len(stack) != 0:
            if recursive_rules >= self.hard_limit_rules:
                logging.warning("hard limit of rules reached: stopping right now")
                break
            elif recursive_rules >= self.soft_limit_rules:
                logging.warning("soft limit of rules reached: trying to avoid recursivity")
                soft_limit = True

            graph_node_name, graph_node_type = stack.pop()

            #print(graph_node)

            if graph_node_type == "NonTerminal":
                # Rule -> recursive

                if soft_limit:
                    new_selected_rule = self.minimize_non_terminals_from_rule(graph_node_name, depth=self.soft_limit_depth)
                else:
                    new_selected_rule = self.get_random_rule(graph_node_name)

                # Add the new rules to the stack
                stack.extend(list(reversed(new_selected_rule)))

                recursive_rules += 1
            else:
                # Terminal -> generate input
                pattern = self.index["terminals_patterns"][graph_node_name]

                if self.index["terminals_is_re"][graph_node_name]:
                    # regex -> generate from regex
                    input += exrex.getone(pattern)
                else:
                    # No regex
                    input += pattern

        return input

    def fix_partial_likelihood(self):
        for rule in self.index["rules_names"]:
            n_rr = len(self.index["graph"][rule])

            if rule not in self.likelihood:
                # We set the likelihood of the current non-defined rule
                self.likelihood[rule] = {}

                for idx, rr in enumerate(self.index["graph"][rule]):
                    self.likelihood[rule][idx] = 1.0 / n_rr
            else:
                # We check if all the rules were defined a likelihood
                # If not, we set the remaining likelihood
                idx_rules_not_defined = []
                total_likelihood_set = 0.0

                # Get the acummulated likelihood which has been set
                for already_set_likelihood_idx in self.likelihood[rule]:
                    if already_set_likelihood_idx >= n_rr:
                        logging.warning("you defined the likelihood for the index %d of the rule '%s',"
                                        " whose index does not exist: ignoring this likelihood",
                                        already_set_likelihood_idx, rule)
                    else:
                        total_likelihood_set += self.likelihood[rule][already_set_likelihood_idx]

                # Check the rules which are not defined
                for idx in range(n_rr):
                    if idx not in self.likelihood[rule]:
                        idx_rules_not_defined.append(idx)

                if total_likelihood_set > 1.0:
                    logging.warning("total likelihood defined for the rule '%s' is higher than 1.0:"
                                    " the rest of rules will be assigned a likelihood of 0.0")

                    likelihood = 0.0
                else:
                    likelihood = (1.0 - total_likelihood_set) / len(idx_rules_not_defined)

                # Set likelihood to those rules which do not have likehood set
                for idx in idx_rules_not_defined:
                    self.likelihood[rule][idx] = likelihood

    def get_grammar(self):
        """
        """
        if "lark_grammar" not in self.args:
            raise BOAInputModuleAbstract("'lark_grammar' has not been provided in the arguments")

        # TODO better way to reference the grammar file?
        path = f"{get_current_path(path=__file__).rsplit('/', 1)[0]}/../../grammars/{self.args['lark_grammar']}"
        grammar = ""
        likelihood = {}

        with open(path) as f:
            for idx, line in enumerate(f):
                line = line.strip()

                if line == "":
                    continue
                if line[0:2] == "//":
                    if (len(line) >= 2 and line[2] == "#"):
                        # BOA line to process -> likelihood
                        line = line[line.index("BOA"):]
                        line = line.split(":")

                        if (len(line) != 4 or line[0] != "BOA"):
                            raise BOAInputModuleAbstract("unexpected format in the grammar file when specifying"
                                                         f" the likelihood of the rules: line {idx}")

                        _, non_terminal_rule, rule_index, likelihood_of_rule = line

                        rule_index = int(rule_index)
                        likelihood_of_rule = float(likelihood_of_rule)

                        if non_terminal_rule not in likelihood:
                            likelihood[non_terminal_rule] = {}

                        if rule_index in likelihood[non_terminal_rule]:
                            raise BOAInputModuleAbstract(f"the likelihood of the rule '{non_terminal_rule}' was"
                                                         " multiple times")

                        likelihood[non_terminal_rule][rule_index] = likelihood_of_rule
                    else:
                        # Lark comment
                        pass
                else:
                    grammar += f"{line}\n"

        return grammar, likelihood

    def index_grammar(self):
        """
        """
        index = {"rules_names": set(),
                 "terminals_names": set(),
                 "terminals_is_re": {},
                 "terminals_patterns": {},
                 "graph": {}}

        for terminal in self.parser["terminals"]:
            t = terminal.serialize()
            t_name = t["name"]
            t_type = t["pattern"]["__type__"]

            if t_type not in ("PatternRE", "PatternStr"):
                logging.warning("terminal type of '%s' is not an expected value (it will evaluated as if it was NOT a regex): '%s'", t_name, t_type)

            index["terminals_is_re"][t_name] = t_type == "PatternRE"
            index["terminals_names"].add(t_name)
            index["terminals_patterns"][t_name] = t["pattern"]["value"]

        for rule in self.parser["rules"]:
            r = rule.serialize()
            r_name = r["origin"]["name"]

            index["rules_names"].add(r_name)

            # There might be multiple definitions of the same rule
            if r_name not in index["graph"]:
                index["graph"][r_name] = []

            index["graph"][r_name].append([])

            for expansion in r["expansion"]:
                if expansion["__type__"] not in ("Terminal", "NonTerminal"):
                    logging.warning("expansion type of rule '%s' is not an expected value: '%s'", r_name, expansion["__type__"])

                index["graph"][r_name][-1].append((expansion["name"], expansion["__type__"]))

        return index
