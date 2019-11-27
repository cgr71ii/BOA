from __future__ import print_function
import sys

'''
print to stderr
'''
def eprint(*args, **kwargs):
    print(*args, file = sys.stderr, **kwargs)