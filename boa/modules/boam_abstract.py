
# Std libs
from abc import ABCMeta, abstractmethod

# This class name has to match with constants.Meta.abstract_module_class_name
class BOAM_abstract:

    # This method initializes the class
    @abstractmethod
    def __init__(self, args):
        self.args = args

    # This method process each token
    @abstractmethod
    def process(self, token):
        pass

    # This method will be invoked after each token is processed
    # This method has the responsibility of save the records in the given report
    @abstractmethod
    def save(self, report):
        pass

    # This method will be invoked before the next token is processed
    @abstractmethod
    def clean(self):
        pass

    # This method will be invoked when all the tokens have been processed
    @abstractmethod
    def finish(self):
        pass