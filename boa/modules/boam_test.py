
"""BOA module that does nothing. Test purposes.
"""

# Std libs
import logging

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from util import is_key_in_dict

class BOAModuleTest(BOAModuleAbstract):
    """BOAModuleTest class. It implements the class BOAModuleAbstract.

    Note:
        It uses *severity_syslog.SeveritySyslog* for showing severity.
    """

    def initialize(self):
        """It initializes the module.

        It appends fake threats for testing purposes.
        """
        self.threats = []

        # Expected report order:
        # EMERGENCY (desc: desc6)
        # ALERT (desc: desc2)
        # CRITICAL (desc: desc1)
        # CRITICAL (desc: desc3)
        # NOTICE (desc: desc5)
        # DEBUG (desc: desc4)
        self.threats.append((self.who_i_am, "desc1", "CRITICAL", "adv1", 5, None))
        self.threats.append((self.who_i_am, "desc2", "ALERT", "adv2", None, 4))
        self.threats.append((self.who_i_am, "desc3", "CRITICAL", "adv3", None, None))
        self.threats.append((self.who_i_am, "desc4", "DEBUG", "adv4", 1, 2))
        self.threats.append((self.who_i_am, "desc5", "NOTICE", "adv5", 2, 3))
        self.threats.append((self.who_i_am, "desc6", "EMERGENCY", "adv6", 3, 4))

        self.bcfg = None

        if (is_key_in_dict(self.dependencies, "boam_cfg.BOAModuleControlFlowGraph")
                and is_key_in_dict(self.dependencies\
                    ["boam_cfg.BOAModuleControlFlowGraph"], "get_basic_cfg")):
            self.bcfg = self.dependencies["boam_cfg.BOAModuleControlFlowGraph"]\
                                         ["get_basic_cfg"]()

    def process(self, token):
        """It processes an AST node. It does nothing.

        Arguments:
            token: AST node.
        """

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
