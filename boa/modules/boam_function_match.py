
# Own libs
from boam_abstract import BOAM_abstract
#from exceptions import BOAM_exception

class BOAM_function_match(BOAM_abstract):
    
    def initialize(self):
        #print("Calling to initialize.")
        #raise BOAM_exception("initialize exception", self)
        pass

    def process(self, token):
        if (str(type(token)) == "<class 'pycparser.c_ast.FuncCall'>"):
            function_name = token.name.name

            if (function_name in self.args['methods']):
                index = self.args['methods'].index(function_name)
                row = str(token.coord).split(':')[-2]
                col = str(token.coord).split(':')[-1]
                
                print(f"{self.__class__.__name__}: {function_name}:{row}:{col} -> {self.args['severity'][index]} -> {self.args['description'][index]}")

    def clean(self):
        #print("Calling to clean.")
        pass

    def save(self, report):
        #print("Calling to save.")
        pass

    def finish(self):
        #print("Calling to finish.")
        pass