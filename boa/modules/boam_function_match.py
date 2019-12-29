

# Own libs
from boam_abstract import BOAM_abstract
from exceptions import BOAM_exception

class BOAM_function_match(BOAM_abstract):
    
    def initialize(self):
        print("Calling to initialize.")
        #raise BOAM_exception("initialize exception", self)

    def process(self, token):
        print("Calling to process.")

    def save(self, report):
        print("Calling to save.")

    def clean(self):
        print("Calling to clean.")

    def finish(self):
        print("Calling to finish.")