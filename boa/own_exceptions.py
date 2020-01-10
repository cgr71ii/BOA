

# Own libs
from util import get_name_from_class_instance

class ParseError(Exception): pass

class BOAModuleNotLoaded(Exception): pass

class BOAModuleException(Exception):
    def __init__(self, message, module):
        self.message = f"BOAM exception in {get_name_from_class_instance(module)}: {message}"