
# Std libs
import unittest
import importlib.util
import sys
import os
import copy

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

class BOAReportMethods(unittest.TestCase):

    def get_module(self, module, path):
        # Your PYTHONPATH has to have the directory to BOA
        #  code (i.e. boa.py visible; /path/to/BOA/modules/..)

        if module in sys.modules:
            return sys.modules[module]

        self.assertFalse(module in sys.modules, f"module '{module}' found in sys.modules")

        spec = importlib.util.spec_from_file_location(module, path)

        self.assertIsNotNone(spec, f"could lot load specification from file (module '{module}' with path '{path}')")

        loaded_module = importlib.util.module_from_spec(spec)

        sys.modules[module] = loaded_module

        spec.loader.exec_module(loaded_module)

        return loaded_module

    def setUp(self):
        try:
            self.severity_syslog = self.get_module(
                "SeveritySyslog",
                f"{get_script_dir()}/../../../boa/enumerations/severity/severity_syslog.py").SeveritySyslog
            self.severity_function_match = self.get_module(
                "SeverityFunctionMatch",
                f"{get_script_dir()}/../../../boa/enumerations/severity/severity_function_match.py").SeverityFunctionMatch
            self.report = self.get_module(
                "BOARStdout",
                f"{get_script_dir()}/../../../boa/reports/boar_stdout.py").BOARStdout
        except Exception as e:
            sys.stderr.write(f"{e}\n")

    def test_report_display_all(self):
        syslog_enum = self.severity_syslog
        syslog_report = self.report(syslog_enum, None)

        # who, description, severity, advice=None, row=None, col=None, sort_by_severity=True, severity_enum=None
        syslog_report.add("mod.class", "description1", syslog_enum.WARNING, "advice1", 1, 1)
        syslog_report.add("mod.class", "description2", syslog_enum.INFORMATIONAL, "advice2", 2, 2)
        syslog_report.add("mod.class", "description3", syslog_enum.CRITICAL, "advice3", 3, 3)

        actual = syslog_report.display_all(display=False)

        expected = \
"""~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~ mod.class ~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
 + Threat (3, 3): description3.
   Severity: CRITICAL.
   Advice: advice3.

 + Threat (1, 1): description1.
   Severity: WARNING.
   Advice: advice1.

 + Threat (2, 2): description2.
   Severity: INFORMATIONAL.
   Advice: advice2.

   Total threats: 3

~~~~~~~~~~~
~ Summary ~
~~~~~~~~~~~
 - Total threats (all modules): 3"""

        self.assertEqual(expected, actual)

    def test_report_join(self):
        syslog_enum = self.severity_syslog
        syslog_report = self.report(syslog_enum, None)
        fm_enum = self.severity_function_match
        fm_report = self.report(fm_enum, None)

        # who, description, severity, advice=None, row=None, col=None, sort_by_severity=True, severity_enum=None
        syslog_report.add("mod1.class1", "description1", syslog_enum.WARNING, "advice1", 1, 1)
        syslog_report.add("mod1.class1", "description2", syslog_enum.INFORMATIONAL, "advice2", 2, 2)
        syslog_report.add("mod1.class1", "description3", syslog_enum.CRITICAL, "advice3", 3, 3)

        fm_report.add("mod2.class2", "description1", fm_enum.HIGH, "advice1", 1, 1)
        fm_report.add("mod2.class2", "description2", fm_enum.LOW, "advice2", 2, 2)
        fm_report.add("mod2.class2", "description3", fm_enum.CRITICAL, "advice3", 3, 3)

        actual = syslog_report.display_all(display=False)

        expected = \
"""~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
~~~ mod1.class1 ~~~
~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
 + Threat (3, 3): description3.
   Severity: CRITICAL.
   Advice: advice3.

 + Threat (1, 1): description1.
   Severity: WARNING.
   Advice: advice1.

 + Threat (2, 2): description2.
   Severity: INFORMATIONAL.
   Advice: advice2.

   Total threats: 3

~~~~~~~~~~~
~ Summary ~
~~~~~~~~~~~
 - Total threats (all modules): 3"""

        self.assertEqual(expected, actual)

        actual = fm_report.display_all(display=False)

        expected = \
"""~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
~~~ mod2.class2 ~~~
~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
 + Threat (3, 3): description3.
   Severity: CRITICAL.
   Advice: advice3.

 + Threat (1, 1): description1.
   Severity: HIGH.
   Advice: advice1.

 + Threat (2, 2): description2.
   Severity: LOW.
   Advice: advice2.

   Total threats: 3

~~~~~~~~~~~
~ Summary ~
~~~~~~~~~~~
 - Total threats (all modules): 3"""

        self.assertEqual(expected, actual)

        full_report = copy.deepcopy(syslog_report)

        full_report.append(fm_report)

        actual = full_report.display_all(display=False)

        expected = \
"""~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
~~~ mod1.class1 ~~~
~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
 + Threat (3, 3): description3.
   Severity: CRITICAL.
   Advice: advice3.

 + Threat (1, 1): description1.
   Severity: WARNING.
   Advice: advice1.

 + Threat (2, 2): description2.
   Severity: INFORMATIONAL.
   Advice: advice2.

   Total threats: 3

~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
~~~ mod2.class2 ~~~
~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~
 + Threat (3, 3): description3.
   Severity: CRITICAL.
   Advice: advice3.

 + Threat (1, 1): description1.
   Severity: HIGH.
   Advice: advice1.

 + Threat (2, 2): description2.
   Severity: LOW.
   Advice: advice2.

   Total threats: 3

~~~~~~~~~~~
~ Summary ~
~~~~~~~~~~~
 - Total threats (all modules): 6"""

        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
