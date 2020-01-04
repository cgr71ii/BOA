
# Own libs
from constants import Meta
from constants import Error
from util import eprint

# Std libs
import os

# 3rd libs
import xmltodict

class RulesManager:

    def __init__(self, rules_file):
        self.rules_file_path = rules_file
        self.file = None

    def open(self):
        if (not os.path.exists(self.rules_file_path)):
            eprint(f"Error: file '{self.rules_file_path}' does not exist.")
            return Error.error_file_not_found

        try:
            self.file = open(self.rules_file_path, "r")
        except Exception as e:
            eprint(f"Error: {e}.")
            return Error.error_unknown

        return Meta.ok_code
        