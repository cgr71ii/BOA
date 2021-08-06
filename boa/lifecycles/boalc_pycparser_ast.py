"""This file contains the class which defines the lifecycle
to be executed when the parser Pycparser is being used and
you want to use an AST and process each token separately.
"""

# Std libs
import logging

# Own libs
from boalc_abstract import BOALifeCycleAbstract
from auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
from utils import is_key_in_dict
from exceptions import BOALCAnalysisException

class BOALCPycparserAST(BOALifeCycleAbstract):
    """BOALCPycparserAST class.

    It implements the necessary logic to process each token
    and not just give all the AST to the *process* method.
    """

    def raise_exception_if_non_valid_analysis(self):
        """This analysis is only compatible with static analysis
        """
        if self.analysis != "static":
            raise BOALCAnalysisException(f"lifecycle '{self.who_i_am}' is only"
                                         " compatible with 'static' analysis, but"
                                         f" actual was '{self.analysis}'")

    def execute_lifecycle(self):
        """It invokes the next methods:

            1. *initialize()*
            2. *process(self.args["parser"]["ast"])*: it will be invoked
               token by token.
            3. *clean()*
            4. *save(self.report)*
            5. *finish()*

        If the key "parser", "ast" is not found in *self.args*, the
        execution will be stopped.
        """
        # Initialize
        self.execute_method(self.instance, "initialize", None, False)

        # Process
        if not is_key_in_dict(self.args, "parser.ast", split="."):
            logging.warning("'%s' needs to have 'ast' in the provided arguments to work: skipping lifecycle", self.who_i_am)

            self.execute_method(self.instance, "set_stop_execution", True, False)
        else:
            ast = self.args["parser"]["ast"]

            visitor = PreorderVisitor(self.process_each_ast_node)

            visitor.visit(ast)

        # If the execution was stopped above, the next methods will not be executed

        # Clean
        self.execute_method(self.instance, "clean", None, False)

        # Save
        self.execute_method(self.instance, "save", self.report, False)

        # Finish
        self.execute_method(self.instance, "finish", None, True)

    def process_each_ast_node(self, node):
        """This method will be invoked as a callback while the
        *PreorderVisitor* instance is walking through the AST
        and will give node by node to this method.

        Once this method is invoked, *process* method will be
        invoked.

        Arguments:
            node: AST node to be processed by *process* method.
        """
        self.execute_method(self.instance, "process", node, False)
