
"""BOA Parser Module for Pycparser.
"""

# Own libs
from boapm_abstract import BOAParserModuleAbstract
from util import eprint

class BOAPMPycparser(BOAParserModuleAbstract):
    """BOAPMPycparser class.
    """

    def initialize(self):
        """
        """
        self.ast = None

    def parse(self):
        """
        """

    def getAST(self):
        if self.ast is None:
            eprint("Warning: returning ast=None.")

        return self.ast
