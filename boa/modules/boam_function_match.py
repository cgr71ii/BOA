

# Own libs
from boam_abstract import BOAM

class BOAM_function_match(BOAM):
    
    def __init__(self, args):
        super().__init__(args)
        print('Calling to constructor.')

    def process(self, token):
        print('Calling to process.')

    def save(self, report):
        print('Calling to save.')

    def clean(self):
        print('Calling to clean.')

    def finish(self):
        print('Calling to finish.')