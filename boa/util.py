from __future__ import print_function
import sys
import os

'''
Print to stderr
'''
def eprint(*args, **kwargs):
    print(*args, file = sys.stderr, **kwargs)

'''
It returns the path where this current script is

This script should be in the same path that BOA is,
and using realpath method, symbolic links are followed
if the os support them

We can give other start point through path argument

IMPORTANT: it does not finish with slash
'''
def get_current_path(path = __file__):
    real_path_to_script = os.path.realpath(path)
    real_path = os.path.split(real_path_to_script)[0]

    return real_path

def file_exists(file):
    return os.path.isfile(file)

def value_exists_in_array(array, value):
    try:
        array[value]

        return True
    except:
        return False