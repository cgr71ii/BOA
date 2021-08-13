
"""BOA module that does nothing. Test purposes.
"""

# Std libs
import logging

# Own libs
from boam_abstract import BOAModuleAbstract
from constants import Meta
from utils import is_key_in_dict

class BOAModuleTest(BOAModuleAbstract):
    """BOAModuleTest class. It implements the class BOAModuleAbstract.

    Note:
        It uses *severity_syslog.SeveritySyslog* for showing severity.
    """

    def initialize(self):
        """It initializes the module.

        It appends fake threats for testing purposes.
        """
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

    def finish(self):
        """It does nothing.
        """
