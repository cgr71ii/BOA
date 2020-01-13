
# Own libs
from boam_abstract import BOAModuleAbstract
from own_exceptions import BOAModuleException

class BOAModuleFunctionMatch(BOAModuleAbstract):

    def initialize(self):
        self.all_methods_name = []
        self.all_methods_reference = []

        for method in self.args["methods"]:
            method_name = method["method"]

            if method_name in self.all_methods_name:
                raise BOAModuleException(f"method '{method_name}' duplicated in rules", self)

            self.all_methods_name.append(method_name)
            self.all_methods_reference.append(method)

    def process(self, token):
        if str(type(token)) == "<class 'pycparser.c_ast.FuncCall'>":
            function_name = token.name.name

            if function_name in self.all_methods_name:
                index = self.all_methods_name.index(function_name)
                row = str(token.coord).split(':')[-2]
                col = str(token.coord).split(':')[-1]
                severity = self.all_methods_reference[index]["severity"]
                description = self.all_methods_reference[index]["description"]

                print(f"{self.__class__.__name__}: {function_name}:{row}:{col} -> {severity} -> {description}")

    def clean(self):
        pass

    def save(self, report):
        pass

    def finish(self):
        pass
