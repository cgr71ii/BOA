
# Own libs
from constants import Meta
from constants import Error
from util import eprint
from exceptions import BOAM_exception

class MainLoop:
    def __init__(self, instances, ast):
        self.instances = instances
        self.ast = ast

    def initialize(self):
        for instance in self.instances:
            try:
                instance.initialize()
            except BOAM_exception as e:
                eprint(f"Error: {e.message}.")
            except Exception as e:
                eprint(f"Error: {e}.")
            except:
                eprint(f"Error: could not initialize the instance {instance.__class__.__module__}.{instance.__class__.__name__}.")