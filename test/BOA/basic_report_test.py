
# Std libs
import unittest
import importlib.util
import sys
import os
import copy

class BOAReportMethods(unittest.TestCase):

    def get_module(self, module, path):
        # Your PYTHONPATH has to have the directory to BOA
        #  code (i.e. boa.py visible; /path/to/BOA/modules/..)

        self.assertFalse(module in sys.modules)

        spec = importlib.util.spec_from_file_location(module, path)

        self.assertIsNotNone(spec)

        loaded_module = importlib.util.module_from_spec(spec)

        sys.modules[module] = loaded_module
        spec.loader.exec_module(loaded_module)

        return loaded_module

    def get_instance(self, module, class_name):
        return getattr(sys.modules[module], class_name)

    def setUp(self):
        try:
            self.severity_syslog = self.get_module(
                "SeveritySyslog",
                f"{os.path.dirname(os.path.realpath(__file__))}/../../boa/enumerations/severity/severity_syslog.py")
            self.severity_function_match = self.get_module(
                "SeverityFunctionMatch",
                f"{os.path.dirname(os.path.realpath(__file__))}/../../boa/enumerations/severity/severity_function_match.py")
            self.report = self.get_module(
                "Report",
                f"{os.path.dirname(os.path.realpath(__file__))}/../../boa/report.py")
        except:
            pass

    def test_report_display_all(self):
        #syslog_report = self.report(self.severity_syslog)
        syslog_enum = self.get_instance("SeveritySyslog", "SeveritySyslog")
        syslog_report = self.get_instance("Report", "Report")(syslog_enum)

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
        #syslog_report = self.report(self.severity_syslog)
        syslog_enum = self.get_instance("SeveritySyslog", "SeveritySyslog")
        syslog_report = self.get_instance("Report", "Report")(syslog_enum)
        fm_enum = self.get_instance("SeverityFunctionMatch", "SeverityFunctionMatch")
        fm_report = self.get_instance("Report", "Report")(fm_enum)

        # who, description, severity, advice=None, row=None, col=None, sort_by_severity=True, severity_enum=None
        syslog_report.add("mod1.class1", "description1", syslog_enum.WARNING, "advice1", 1, 1)
        syslog_report.add("mod1.class1", "description2", syslog_enum.INFORMATIONAL, "advice2", 2, 2)
        syslog_report.add("mod1.class1", "description3", syslog_enum.CRITICAL, "advice3", 3, 3)

        fm_report.add("mod2.class2", "description1", fm_enum.HIGH, "advice1", 1, 1)
        fm_report.add("mod2.class2", "description2", fm_enum.NORMAL, "advice2", 2, 2)
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
   Severity: NORMAL.
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
   Severity: NORMAL.
   Advice: advice2.

   Total threats: 3

~~~~~~~~~~~
~ Summary ~
~~~~~~~~~~~
 - Total threats (all modules): 6"""

        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
