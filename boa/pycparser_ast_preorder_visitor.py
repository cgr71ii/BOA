
# Pycparser libs
from pycparser.c_ast import NodeVisitor

class PreorderVisitor(NodeVisitor):

    def __init__(self, callback):
        self.callback = callback

        if callback is None:
            self.callback = self.do_nothing

    def do_nothing(self, node):
        pass

    def visit(self, node):
        if node is None:
            return

        for n in node:
            if type(n) is not tuple:
                self.callback(n)
            for t in n:
                if type(t) is not str:
                    self.callback(t)
                    self.visit(t.children())
