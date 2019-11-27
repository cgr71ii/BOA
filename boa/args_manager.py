
# Own libs
from constants import Meta
from constants import Args
from constants import Error

# Std libs
import re
import argparse

class ArgsManager:

    args = []

    def __init__(self):
        self.parser = argparse.ArgumentParser(description = Meta.description)
    
    '''
    It loads the args configuration
    '''
    def load_args(self):
        opt_argc = len(Args.opt_args_str)
        argc = len(Args.args_str)

        for i in range(opt_argc):
            self.parser.add_argument(Args.opt_args_str[i], help = Args.opt_args_help[i])
        
        for i in range(argc):
            self.parser.add_argument(Args.args_str[i], help = Args.args_help[i])
        

    '''
    It parses the arguments to easily check if they are correct
    '''
    def parse(self):
        ArgsManager.args = self.parser.parse_args()

    '''
    It checks if args are correctly used
    '''
    def check(self):
        if (isinstance(ArgsManager.args, argparse.Namespace) == False):
            return Error.error_args_type

        return Meta.ok_code