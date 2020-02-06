"""
"""

# Own libs
from boalc_abstract import BOALifeCycleAbstract
from lifecycles.auxiliary_modules.pycparser_ast_preorder_visitor import PreorderVisitor
from util import is_key_in_dict

class BOALCPycparserAST(BOALifeCycleAbstract):
    """
    """

    def execute_lifecycle(self):
        """
        """
        # Initialize
        self.execute_method(self.instance, "initialize", "initialize", None, False)

        # Process
        if not is_key_in_dict(self.args, "ast"):
            print(f"Warning: '{self.who_i_am}' needs to have 'ast' in the"
                  " given arguments to work. Skipping lifecycle.")
            self.execute_method(self.instance,
                                "set_stop_execution",
                                "stop the execution",
                                True, False)
        else:
            ast = self.args["ast"]

            visitor = PreorderVisitor(self.process_each_ast_node)

            visitor.visit(ast)

        # If the execution was stopped above, the next methods will not be executed

        # Clean
        self.execute_method(self.instance, "clean", "clean", None, False)

        # Save
        self.execute_method(self.instance, "save", "save (report)", self.report, False)

        # Finish
        self.execute_method(self.instance, "finish", "finish", None, True)

    def process_each_ast_node(self, node):
        """
        """
        self.execute_method(self.instance, "process", "process", node, False)
