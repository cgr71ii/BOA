
# Std libs
from abc import ABCMeta, abstractmethod

'''
Advice: use exception with descriptive messages if you want 
        to know descriptive information about your errors.
        You can use exceptions.BOAM_exception for that purpose
'''

# This  file name has to match with constants.Meta.abstract_module_name
# This class name has to match with constants.Meta.abstract_module_class_name
class BOAM_abstract:

    # This method saves the args and should not be overriden 
    #  (override 'initialize' method instead for initialization purposes)
    def __init__(self, args):
        self.args = args

    # This method loads the args and initializes the module
    @abstractmethod
    def initialize(self):
        pass

    # This method process each token
    @abstractmethod
    def process(self, token):
        pass

    # This method will be invoked before the next token is processed
    @abstractmethod
    def clean(self):
        pass

    # This method will be invoked after all tokens have been processed
    # This method has the responsibility of save the records in the given report
    @abstractmethod
    def save(self, report):
        pass

    # This method will be invoked when all the tokens have been processed
    @abstractmethod
    def finish(self):
        pass