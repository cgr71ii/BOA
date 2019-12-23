
# Std libs
from abc import ABCMeta, abstractmethod

class BOAM:

    @abstractmethod
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def process(self, token):
        pass

    @abstractmethod
    def save(self, report):
        pass

    @abstractmethod
    def clean(self):
        pass

    @abstractmethod
    def finish(self):
        pass