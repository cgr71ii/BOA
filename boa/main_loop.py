
"""Main Loop.

This file contains the class MainLoop, which handles the
loop which is executed to analyze the language file.
"""

# Own libs
from constants import Meta, Error
from util import eprint, get_name_from_class_instance
from own_exceptions import BOAModuleException
from pycparser_ast_preorder_visitor import PreorderVisitor

class MainLoop:
    """MainLoop class.

    This class handles the modules intances. Concretely, it
    initializes the instances, iterates the processing
    throught them, and save the report records.

    The steps which are followed depends on the lifecycle being
    used by a concrete module (e.g. *boam_function_match.
    BOAModuleFunctionMatch*).
    """

    def __init__(self, instances, reports, ast):
        """It invokes self.initialize(instances, ast).

        Arguments:
            instances: module instances which will be looped.
            reports: report instances to show the threat records.
            ast: processed AST.
        """
        self.initialize(instances, reports, ast)

    def initialize(self, instances, reports, ast):
        """It initializes all the variables which will be used by
        the other methods.

        Arguments:
            instances: module instances that are going to be saved.
            reports: report instances to show the threat records.
            ast: processed AST that is going to be saved.
        """
        self.instances = instances
        self.reports = reports
        self.instances_names = []
        self.instances_warned = []
        self.ast = ast
        self.rtn_code = Meta.ok_code

        for instance in self.instances:
            self.instances_names.append(get_name_from_class_instance(instance))

        # It needs that self.instances_names is processed
        self.final_report = self.make_final_report()

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

        severity_ok = report.set_severity_enum_mapping(self.instances_names[0], self.reports[0].get_severity_enum_instance())

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

    def handle_loop(self):
        """This method is the one which should be invoked to
        handle the loop.

        It invokes the next phases:

        1. Initialization.\n
        2. Process.\n
        3. Clean.\n
        4. Save report records.\n
        5. Finish.\n

        The way the phases are invoked depends on the lifecycle.

        Returns:
            int: self.rtn_code
        """
        # Initialize
        self.initialize_instances()

        # Process and clean
        visitor = PreorderVisitor(self.process_and_clean_instances)

        visitor.visit(self.ast)

        # Save (report) and finish
        self.save_and_finish_instances(self.final_report)

        return self.rtn_code

    def loop(self, methods_name, error_verbs, args, force_invocation):
        """Method which invokes other methods with its arguments.

        This method it is for internal use and should not be
        called outside this class. This method is used by other
        methods wisely (e.g. initialize_instances). However, it
        is possible to use it if you know the internals of the
        class.

        Arguments:
            methods_name (list): methods (str) which are going to
                be invoked for each *self.instances*.
            error_verbs (list): verbs (str) to error displaying.
            args (list): args to be given to methods to be invoked.
            force_invocation (bool): force a method invokation
                despite something failed in the past (if false, when
                a failure happens, a method will not be invoked).
        """
        if (not isinstance(methods_name, list) or
                not isinstance(error_verbs, list) or
                not isinstance(args, list) or
                not isinstance(force_invocation, list)):
            eprint(f"Error: arguments are not 'list' in main loop.")
            self.rtn_code = Error.error_loop_args_wrong_type
            return

        if (len(methods_name) != len(error_verbs) or
                len(methods_name) != len(args) or
                len(methods_name) != len(force_invocation)):
            eprint(f"Error: length in arguments are not equal in main loop.")
            self.rtn_code = Error.error_loop_args_neq_length
            return

        for instance in self.instances:
            index = 0
            name = get_name_from_class_instance(instance)

            if instance.stop:
                # An instance can take the decision of stopping its own execution
                continue

            while index < len(methods_name):
                # Warn about skipping action if any failure happended in the past
                if (name not in self.instances_names and not force_invocation[index]):
                    instance_method_name = f"{name}.{methods_name[index]}"

                    # Warn only once
                    if instance_method_name not in self.instances_warned:
                        eprint(f"Warning: skipping invocation to {instance_method_name} due to previous errors.")
                        self.instances_warned.append(instance_method_name)

                    index += 1
                    continue

                exception = False

                # Invoke method and handle exceptions
                try:
                    if args[index] is None:
                        getattr(instance, methods_name[index])()
                    else:
                        getattr(instance, methods_name[index])(args[index])
                except BOAModuleException as e:
                    eprint(f"Error: {e.message}.")
                    exception = True
                except Exception as e:
                    eprint(f"Error: {e}.")
                    exception = True
                except:
                    eprint(f"Error: could not {error_verbs[index]} the instance '{get_name_from_class_instance(instance)}'.")
                    exception = True

                # Something failed. Warn about this in the future
                if exception:
                    if name in self.instances_names:
                        self.instances_names.remove(name)
                        self.rtn_code = Error.error_loop_module_exception

                index += 1

    def initialize_instances(self):
        """It invokes self.initialize method.
        """
        self.loop(['initialize'], ['initialize'], [None], [False])

    def process_and_clean_instances(self, node):
        """It invokes self.process and self.clean methods.

        Arguments:
            node: AST token which will be given to process().
        """
        self.loop(['process', 'clean'], ['process', 'clean'], [node, None], [False, False])

    def save_and_finish_instances(self, report):
        """It invokes self.save and self.finish methods.

        Arguments:
            report: report instance which will be used to save
                the threat records.
        """
        # Force invocation to "finish" for resource releasing purposes
        self.loop(['save', 'finish'], ['save (report)', 'finish'], [report, None], [False, True])
