"""File which implements the class NodeVisitor from Pycparser.

We implement the class NodeVisitor with the goal of be able to
make a preorder path through the AST.
"""

# 3rd libs
from pycparser.c_ast import NodeVisitor

# Own libs
from utils import do_nothing

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
                *utils.do_nothing* will be invoked instead. When
                callback is invoked, the current Pycparser node
                is set as parameter.
        """
        if callback is None:
            self.callback = do_nothing
        else:
            self.callback = callback

    def visit(self, node):
        """It makes the preorder path throught the AST.

        Arguments:
            node (pycparser.c_ast.Node): AST node which
                is going to be visited in preorder
                recursively.
        """
        self._visit(node, None)

    def visit_and_return_path(self, node):
        """It makes the preorder path throught the AST.

        Arguments:
            node (pycparser.c_ast.Node): AST node which
                is going to be visited in preorder
                recursively.

        Returns:
            list: path
        """
        if node is None:
            return []

        result = []

        for n in node:
            if not isinstance(n, tuple):
                self.callback(n)
                result.append(n)
            for t in n:
                if not isinstance(t, str):
                    result.append(t)
                    for res in self.visit_and_return_path(t.children()):
                        result.append(res)

        return result

    def visit_and_return_first_path(self, node):
        """It makes the preorder path throught the AST.

        Arguments:
            node (pycparser.c_ast.Node): AST node which
                is going to be visited in preorder
                recursively.

        Returns:
            list: first path (direct children)
        """
        if node is None:
            return []

        result = []

        for n in node:
            if not isinstance(n, tuple):
                self.callback(n)
                result.append(n)

        return result

    def _visit(self, node, recursion_deepness):
        """It makes the preorder path throught the AST.
        You can specify a recursion deepness.

        Arguments:
            node (pycparser.c_ast.Node): AST node which
                is going to be visited in preorder
                recursively.
            recursion_deepness (int): deepness of recursion.
                If you specify *None*, recursion deepness
                will not used.
        """
        if node is None:
            return

        for n in node:
            if not isinstance(n, tuple):
                if (recursion_deepness is None or
                        recursion_deepness > 0):
                    self.callback(n)
            for t in n:
                if not isinstance(t, str):
                    if recursion_deepness is None:
                        self.callback(t)
                        self._visit(t.children(), recursion_deepness)
                    elif recursion_deepness > 0:
                        self.callback(t)
                        self._visit(t.children(), recursion_deepness - 1)
