
class ParseError(Exception): pass

class BOAModuleNotLoaded(Exception): pass

class BOAM_exception(Exception):
    def __init__(self, message, module):
        module_name = module.__class__.__module__
        class_name = module.__class__.__name__
        self.message = f"BOAM exception in {module_name}.{class_name}: {message}"