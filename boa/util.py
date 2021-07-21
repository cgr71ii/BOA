
"""Utilities.

This file contains diverse functions which will
may be used from all BOA's files.

This file does not have a concrete goal.
"""

# Std libs
from __future__ import print_function
import sys
import os
import re
import logging

# Own libs
from constants import Other

def eprint(*args, **kwargs):
    """It prints to the error output (i.e. stderr).

    Arguments:
        \\*args (variadic list): list to be given to *print* function.
        \\*\\*kwargs (variadic dict): dict to be given to *print* function.
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
        logging.warning("could not return the correct format (is it a class instance?): %s", str(e))

    return None

def is_key_in_dict(dictionary, key, split_by_point=False,
                   message=None, raise_exception=None, exception_args=None):
    """It checks if a given dictionary contains
    a concrete value. A try-except is used to perform
    this checking (EAFP) instead of other methods to
    avoid a false positive when a dict key is defined
    with a value of *None*.

    Arguments:
        dictionary (dict): dictionary to check.
        key (str): key which will be checked if it is
            in the dictionary.
        split_by_point (bool): it will split *key* by '.'
            if *True* and it will check for all the keys.
            The default value is *False*.
        message (str): message to be displayed if the key
            is not contained. The default value is *False*.
        raise_exception (Exception): exception to be raised.
            The default value is *None*, which it means raise
            nothing.
        exception_args: args to be given to the exception
            which is going to be raised if *raise_exception*
            is not *None*. The default value is *None*.

    Raises:
        Exception: if *key* is not in the *dictionary* and
            *raise_exception* is not None, *raise_exception* will
            be raised with *exception_args* as args.

    Returns:
        bool: *True* if the dictionary contains the key;
        *False* otherwise
    """
    try:
        if split_by_point:
            keys = key.split(".")

            if (keys and len(keys) > 0):
                value = dictionary

                for k in keys:
                    if value is None:
                        raise KeyError()
                    value = value[k]
            else:
                raise KeyError()
        else:
            dictionary[key]

        return True
    except KeyError:
        if message is not None:
            logging.warning(message)
    except Exception as e:
        logging.error("not expected error while checking if key is in dict: %s", str(e))

    if raise_exception is not None:
        raise raise_exception(exception_args)

    return False

def do_nothing(*args, rtn_sth=False, rtn_value=None):
    """Just what the name suggests: it does nothing.

    This function is useful when a callback is needed
    and no callback is provided, so this function is
    used as default behaviour.

    Arguments:
        \\*args (variadict list): indefinite number of args to be provided.
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

def get_environment_varibles(env_var_list, verbose_on_failure=False, failure_message=None):
    """It returns the values of the given environment variable names.

    Arguments:
        env_var_list (list): list with all the environment variables.
            If a single string is given, it is inserted into a list.
        verbose_on_failure (bool): if cannot load an environment
            variable and *True*, an error message will be displayed.
            The default value is *False*, which means no display any
            message on failure.
        failure_message (str): message to be displayed when cannot
            load an environment variable. If is not *None*, which
            is the default value, the format will be:
            f"{failure_message}: '{environment_variable}'.".

    Returns:
        dict: it contains the environment variables which exist with
        the name as key
    """
    env_var_dict = {}

    if (env_var_list and isinstance(env_var_list, str)):
        env_var_list = [env_var_list]
    if (isinstance(env_var_list, list) and len(env_var_list) == 0):
        pass
    elif (not env_var_list or not isinstance(env_var_list, list)):
        logging.error("unexpected type while trying to load environment variables")
        return env_var_dict

    for env_var in env_var_list:
        if (isinstance(env_var, str) and env_var in os.environ):
            env_var_dict[env_var] = os.environ[env_var]
        elif verbose_on_failure:
            if failure_message is not None:
                logging.warning("%s: '%s'", failure_message, env_var)
            else:
                logging.warning("could not load the environment variable '%s'", env_var)

    return env_var_dict

def invoke_by_name(instance, method):
    """It invokes a method of an instance.

    Arguments:
        instance: instance to be used to invoke the *method*.
        method (str): method to be invoked in the *instance*.

    Returns:
        Method invocation result. *Other.util_invoke_by_name_error_return*
        if something did not succeed. The returned value should be compared
        with id() or *is*/*is not* in order to know if something wrong happened.
    """
    if (not instance or not isinstance(method, str)):
        logging.error("invoke by name: 'instance' ('%s') has to have a value"
                      " and 'method' ('%s') has to be a string", instance, method)
        return Other.other_util_invoke_by_name_error_return

    try:
        method = getattr(instance, method)
        result = method()

        return result
    except Exception as e:
        logging.error("invoke by name: %s", str(e))

    return Other.other_util_invoke_by_name_error_return

def is_graph_cyclic(graph, visited_nodes=None, current_connection=None):
    """It checks if a graph is cyclic.

    Arguments:
        graph (dict): this dict has to contain all
            the nodes of the graph and has to contain
            a list for each node with the connections
            among the nodes. If a node has not any
            connection, it is expected an empty list.
            The values of the dict are expected to be strings.
        visited_nodes (list): it is used in order to check
            if we are visiting again a node, and in that case,
            the graph is cyclic. This argument should be *None*
            at begin.
        current_connection (str): the current connection
            which will allow us to check if it is in the
            *visited_nodes* list. This argument should be
            *None* at begin.

    Returns:
        bool: *True* if the graph is cyclic. *False* otherwise
    """
    # Initialization
    if (visited_nodes is None and current_connection is None):
        current_connection = list(graph)[0]
        visited_nodes = [current_connection]
    elif (visited_nodes is None or current_connection is None):
        logging.warning("unexpected behaviour could happen in method 'is_graph_cyclic':"
                        " 'visited_nodes' or 'current_connection' is 'None', but both were expected to"
                        " be 'None'")

    # Base case: check if the node has been visited before
    if current_connection in visited_nodes[0:-1]:
        # The graph is cyclic
        return True

    # Recursive case: visit all the connections for the current node
    for node, connections in graph.items():
        if node == current_connection:
            for connection in connections:
                if is_graph_cyclic(graph, visited_nodes + [connection], connection):
                    return True

    return False

def get_just_type(instance, instance_type=None):
    """It returns just the type of an instance.

    Example:
        type("foo") returns "<class 'str'>"
        get_just_type("foo") returns "str"

    Arguments:
        instance (object): target variable.
        instance_type (type): target variable type.
            It is optional. The default value is
            *None*. If is not *None*, this
            value will be used instead of *instance*.

    Returns:
        str: type of the instance. *None* if
        the regular expression "<class '.+'>"
        does not match
    """
    valid = re.compile("<class '(.+)'>")
    if instance_type is not None:
        str_type = str(instance_type)
    else:
        str_type = str(type(instance))
    match = valid.match(str_type)
    if not match:
        return None
    return match.group(1)

def set_up_logging(filename=None, level=logging.INFO, format_str=Other.other_logging_format):
    """It sets up the logging library

    Arguments:
        filename (str): path to the file where the logging entries will be dumped.
        level (int): logging level (e.g. 20 is logging.INFO, 30 is logging.WARNING)
        format_str (str): format of the logging messages
    """
    handlers = [
        logging.StreamHandler()
    ]

    if filename is not None:
        handlers.append(logging.FileHandler(filename))

    logging.basicConfig(handlers=handlers, level=level, format=format_str)
