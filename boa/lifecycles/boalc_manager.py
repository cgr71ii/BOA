
"""Lifecycle manager.

This file contains the class BOALifeCycleManager, which
handles the loop which is executed to analyze the language
file.
"""

# Own libs
from constants import Meta, Error
from util import eprint, get_name_from_class_instance, is_key_in_dict
from own_exceptions import BOAModuleException, BOALCException

class BOALifeCycleManager:
    """BOALifeCycleManager class.

    This class handles the modules intances. Concretely, it
    initializes the instances, iterates the processing
    throught them, and save the report records.

    The steps which are followed depends on the lifecycle being
    used by a concrete module.
    """

    def __init__(self, instances, reports, lifecycle_args, lifecycle_instances):
        """It initializes all the variables which will be used by
        the other methods.

        Arguments:
            instances: module instances that are going to be saved.
            reports (list): list of Report instances.
            lifecycle_args (dict): processed AST that is going to be saved.
            lifecycle_instances (list): instances of lifecycles to
                be used by the *instances*.
        """
        self.instances = instances
        self.reports = reports
        self.instances_names = []
        self.instances_warned = []
        self.lifecycle_args = lifecycle_args
        self.rtn_code = Meta.ok_code
        self.lifecycle_instances = lifecycle_instances

        if len(self.instances) != len(self.reports):
            raise BOALCException("len(instances) is not equal to len(reports)")
        if len(self.instances) != len(self.lifecycle_instances):
            raise BOALCException("len(instances) is not equal to len(lifecycle_instances)")

        for instance in self.instances:
            self.instances_names.append(get_name_from_class_instance(instance))

        # It needs that self.instances_names is processed
        self.final_report = self.make_final_report()

        # Initialize the lifecycle instances
        index = 0

        while index < len(self.lifecycle_instances):
            self.lifecycle_instances[index] = self.lifecycle_instances[index](
                self.instances[index],
                self.final_report,
                self.lifecycle_args,
                self.execute_instance_method
            )

            index += 1

    def get_final_report(self):
        """It returns the final report.

        Returns:
            Report: the final report
        """
        return self.final_report

    def make_final_report(self):
        """It makes a report which contains all the threat records
        contained in all the other reports.

        Returns:
            Report: the final report or *None*
        """
        if (not self.reports or
                not isinstance(self.reports, list) or
                len(self.reports) == 0):
            return None

        report = self.reports[0]
        index = 1

        severity_ok = report.set_severity_enum_mapping(
            self.instances_names[0],
            self.reports[0].get_severity_enum_instance())

        if not severity_ok:
            eprint("Error: could not append the threat reports.")
            return None

        while index < len(self.reports):
            rtn_code = report.append(self.reports[index], who=self.instances_names[index])

            if rtn_code != Meta.ok_code:
                eprint("Error: could not append the threat reports.")
                return None

            index += 1

        return report

    def handle_lifecycle(self):
        """This method is the one which should be invoked to
        handle the lifecycle.

        The way the phases are invoked depends on the lifecycle.

        The method that will be invoked is *execute_lifecycle*,
        which is defined in *BOALifeCycleAbstract* class. In that
        method should be defined the phases that are going to be
        called.

        Returns:
            int: self.rtn_code
        """
        for lifecycle in self.lifecycle_instances:
            try:
                # This method may change self.rtn_code value
                lifecycle.execute_lifecycle()
            except BOALCException as e:
                eprint(f"Error: {lifecycle.get_name()}: {e}.")
            except Exception as e:
                eprint(f"Error: {lifecycle.get_name()}: {e}.")

        return self.rtn_code

    def execute_instance_method(self, instance, method_name, error_verb, args, force_invocation):
        """It attempts to execute a method of a concrete instance.

        Arguments:
            instance: initialized instance which a method is going
                to be invoked if possible.
            method_name (str): method which is going to be invoked.
            error_verb (str): verb to error displaying.
            args: args to be given to the invoked method.
            force_invocation (bool): force a method invokation
                despite something failed in the past (if *False*, when
                a failure happens, a method will not be invoked).

        Returns:
            bool: it will return *False* if: the instance is not in
            *self.instances*, the property *stop* is *True*, ...
            It will return *True* only if the execution of the given
            method could be executed without any exception.
        """
        if not instance:
            return False

        instance_name = get_name_from_class_instance(instance)
        instance_method_name = f"{instance_name}.{method_name}"
        concrete_instance = None

        try:
            concrete_instance = self.instances.index(instance)
        except ValueError:
            eprint(f"Warning: instance '{instance_name}' not found.")
            return False

        concrete_instance = instance

        if concrete_instance.stop:
            # An instance can take the decision of stopping its own execution
            return False

        # Warn about skipping action if any failure happended in the past
        if (instance_name not in self.instances_names and not force_invocation):
            # Warn only once
            if instance_method_name not in self.instances_warned:
                eprint(f"Warning: skipping invocation to '{instance_method_name}'"
                       " due to previous errors.")
                self.instances_warned.append(instance_method_name)

            return False

        exception = False

        # Invoke method and handle exceptions
        try:
            if args is None:
                getattr(instance, method_name)()
            else:
                getattr(instance, method_name)(args)
        except BOAModuleException as e:
            eprint(f"Error: {e.message}.")
            exception = True
        except Exception as e:
            eprint(f"Error: {e}.")
            exception = True
        except:
            eprint(f"Error: could not {error_verb} the instance '{instance_name}'.")
            exception = True

        # Something failed. Warn about this in the future
        if (exception and instance_name in self.instances_names):
            self.instances_names.remove(instance_name)
            self.rtn_code = Error.error_lifecycle_module_exception
            return False

        return True
