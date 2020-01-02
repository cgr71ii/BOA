
# Own libs
from constants import Meta
from constants import Error
from util import eprint
from exceptions import BOAM_exception
from pycparser_ast_preorder_visitor import PreorderVisitor
from util import get_name_from_class_instance

# Pycparser libs
from pycparser.c_ast import NodeVisitor

class MainLoop:
    def __init__(self, instances, ast):
        self.initialize(instances, ast)

    def initialize(self, instances, ast):
        self.instances = instances
        self.instances_names = []
        self.instances_warned = []
        self.ast = ast
        self.rtn_code = Meta.ok_code

        for instance in self.instances:
            self.instances_names.append(get_name_from_class_instance(instance))

    def handle_loop(self):
        # Initialize
        self.initialize_instances()

        # Process and clean
        pv = PreorderVisitor()

        pv.visit(self.ast, self.process_and_clean_instances)

        # Save (report) and finish
        # TODO reports have been not implemented yet
        self.save_and_finish_instances("Not a Report")

        return self.rtn_code

    def loop(self, methods_name, error_verbs, args, force_invocation):
        if (type(methods_name) is not list or
            type(error_verbs) is not list or
            type(args) is not list or
            type(force_invocation) is not list):
            eprint(f"Error: arguments are not lists in main loop.")
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

            while (index < len(methods_name)):
                # Warn about skipping action if any failure happended in the past
                if (name not in self.instances_names and not force_invocation[index]):
                    instance_method_name = f"{name}.{methods_name[index]}"

                    # Warn only once
                    if (instance_method_name not in self.instances_warned):
                        eprint(f"Warning: skipping invocation to {instance_method_name} due to previous errors.")
                        self.instances_warned.append(instance_method_name)

                    index += 1
                    continue

                exception = False

                # Invoke method and handle exceptions
                try:
                    if (args[index] == None):
                        getattr(instance, methods_name[index])()
                    else:
                        getattr(instance, methods_name[index])(args[index])
                except BOAM_exception as e:
                    eprint(f"Error: {e.message}.")
                    exception = True
                except Exception as e:
                    eprint(f"Error: {e}.")
                    exception = True
                except:
                    eprint(f"Error: could not {error_verbs[index]} the instance {get_name_from_class_instance(instance)}.")
                    exception = True
            
                # Something failed. Warn about this in the future
                if (exception):
                    if (name in self.instances_names):
                        self.instances_names.remove(name)
                        self.rtn_code = Error.error_loop_module_exception

                index += 1

    def initialize_instances(self):
        self.loop(['initialize'], ['initialize'], [None], [False])

    def process_and_clean_instances(self, node):
        self.loop(['process', 'clean'], ['process', 'clean'], [node, None], [False, False])

    def save_and_finish_instances(self, report):
        # Force invocation to "finish" for resource releasing purposes
        self.loop(['save', 'finish'], ['save (report)', 'finish'], [report, None], [False, True])