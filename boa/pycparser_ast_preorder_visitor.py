
# Pycparser libs
from pycparser.c_ast import NodeVisitor

class PreorderVisitor(NodeVisitor):

    def foo(self, node):
        pass

    def visit(self, node, callback = None, recursivity_level = 1):
        if (node == None):
            return
        if (type(recursivity_level) is not int):
            recursivity_level = 1
        if (callback == None):
            callback = self.foo

        for n in node:
            #if (type(n) is str):
            #        print(f" ;{n}")
            #else:
            #    print(f" **{'*' * len(n.__class__.__name__)}**")
            #    print(f" * {n.__class__.__name__} * ")
            #    print(f" **{'*' * len(n.__class__.__name__)}**")
            
            if (type(n) is not tuple):
                callback(n)
            for t in n:
                #if (type(t) is str):
                #    print(f" :{t}")
                #else:
                #    print(f" --{'-' * len(t.__class__.__name__)}--")
                #    print(f" - {t.__class__.__name__} - ")
                #    print(f" --{'-' * len(t.__class__.__name__)}--")
                #
                #    callback(t)
                #
                #    self.visit(t.children(), callback, recursivity_level + 1)
                if (type(t) is not str):
                    callback(t)
                    self.visit(t.children(), callback, recursivity_level + 1)