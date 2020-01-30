
"""Utilities.

This file contains diverse functions which will
may be used from all BOA's files.

This file does not have a concrete goal.
"""

# Std libs
from __future__ import print_function
import sys
import os

def eprint(*args, **kwargs):
    """It prints to the error output (i.e. stderr).

    Arguments:
        \*args (variadic list): list to be given to *print* function.
        \*\*kwargs (variadic dict): dict to be given to *print* function.
    """
    print(*args, file=sys.stderr, **kwargs)

def get_current_path(path=__file__):
    """It returns the path where this current script is.

    This script should be in the same path that BOA is,
    and using realpath method, symbolic links are followed
    if the os support them.

    Arguments:
        path (str): start point; the default is the current script.

    Returns:
        str: real path (it does not finish with '/')
    """
    real_path_to_script = os.path.realpath(path)
    real_path = os.path.split(real_path_to_script)[0]

    return real_path

def file_exists(file):
    """It checks if the given file exists.

    Arguments:
        file (str): absolute or relative path to file.

    Returns:
        bool: true if the file exists; false otherwise
    """
    return os.path.isfile(file)

def get_name_from_class_instance(instance):
    """It returns a concrete format for a class instance.

    The format is (without quotes): "module_name.class_name".

    Arguments:
        instance: instance from where we will get the information.

    returns:
        str: name for the given instance with a concrete format.
        *None* if something wrong happened.
    """
    try:
        return f"{instance.__class__.__module__}.{instance.__class__.__name__}"
    except Exception as e:
        eprint(f"Warning: could not return the correct format (is it a class instance?): {e}.")

    return None

def is_key_in_dict(dictionary, key):
    """It checks if a given dictionary contains
    a concrete value. A try-except is used to perform
    this checking (EAFP) instead of other methods to
    avoid a false positive when a dict key is defined
    with a value of *None*.

    Arguments:
        dictionary (dict): dictionary to check.
        key (str): key which will be checked if it is
            in the dictionary.

    Returns:
        bool: true if the dictionary contains the key;
        false otherwise
    """
    try:
        dictionary[key]

        return True
    except KeyError:
        return False
    except Exception as e:
        eprint(f"Error: not expected error while checking if key is in dict: {e}.")
        return False

def do_nothing(*args, rtn_sth=False, rtn_value=None):
    """Just what the name suggests: it does nothing.

    This function is useful when a callback is needed
    and no callback is provided, so this function is
    used as default behaviour.

    Arguments:
        \*args (variadict list): indefinite number of args to be provided.
        rtn_sth (bool): if want something to be returned, use *True*.
        rtn_value: value to be returned.
    """
    if rtn_sth:
        return rtn_value

def get_index_if_match_element_in_tuples(tuples, value, key_position=0, check_all_elements=False):
    """It returns the index when a concrete value is
    found in a list of given tuples.

    Arguments:
        tuples (list of tuples): list of tuples. If a only
            a tuple is given, it will be wrapped in a list.
        value: value to be found in a tuple.
        key_position (int): position in the tuples to look
            for the value. The default value is 0.
        check_all_elements (bool): ignore *key_position* and
            look for the value in all positions of the tuples.
            The default value is *False*.

    Returns:
        int: index of the **first** tuple which contains
        the value; *None* if the value it is not found.
    """
    index = 0

    if not isinstance(tuples, list):
        tuples = [tuples]

    for tupl in tuples:
        if check_all_elements:
            for element in tupl:
                if element == value:
                    return index
        elif tupl[key_position] == value:
            return index

        index += 1

    return None

def get_environment_varibles(env_var_list):
    """It returns the values of the given environment variable names.

    Arguments:
        env_var_list (list): list with all the environment variables.
            If a single string is given, it is inserted into a list.

    Returns:
        dict: it contains the environment variables which exist with
        the name as key
    """
    env_var_dict = {}

    if (env_var_list and isinstance(env_var_list, str)):
        env_var_list = [env_var_list]
    if (not env_var_list or not isinstance(env_var_list, list)):
        return env_var_dict

    for env_var in env_var_list:
        if (isinstance(env_var, str) and env_var in os.environ):
            env_var_dict[env_var] = os.environ[env_var]

    return env_var_dict
