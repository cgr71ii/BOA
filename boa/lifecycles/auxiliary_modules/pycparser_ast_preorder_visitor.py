"""File which implements the class NodeVisitor from Pycparser.

We implement the class NodeVisitor with the goal of be able to
make a preorder path through the AST.
"""

# Pycparser libs
from pycparser.c_ast import NodeVisitor

# Own libs
from util import do_nothing

class PreorderVisitor(NodeVisitor):
    """PreorderVisitor class. It implements the NodeVisitor class.

    It makes a preorder path through the AST and, optionally,
    invokes a given callback.
    """

    def __init__(self, callback=None):
        """It initializes the class.

        It sets the callback.

        Arguments:
            callback: callback to be invoked after. If *None*,
                *util.do_nothing* will be invoked instead.
        """
        if callback is None:
            self.callback = do_nothing
        else:
            self.callback = callback

    def visit(self, node):
        """It makes the preorder path throught the AST.

        Arguments:
            node: AST node which is going to be visited in
                preorder recursively.
        """
        if node is None:
            return

        for n in node:
            if not isinstance(n, tuple):
                self.callback(n)
            for t in n:
                if not isinstance(t, str):
                    self.callback(t)
                    self.visit(t.children())
