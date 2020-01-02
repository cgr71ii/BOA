

# Own libs
from boam_abstract import BOAM_abstract
#from exceptions import BOAM_exception

class BOAM_function_match(BOAM_abstract):
    
    def initialize(self):
        #print("Calling to initialize.")
        #raise BOAM_exception("initialize exception", self)
        pass

    def process(self, token):
        print(f"type: {str(type(token))}")
        if (str(type(token)) == "<class 'pycparser.c_ast.FuncDecl'>"):
            #print(token)
            pass

    def clean(self):
        #print("Calling to clean.")
        pass

    def save(self, report):
        #print("Calling to save.")
        pass

    def finish(self):
        #print("Calling to finish.")
        pass