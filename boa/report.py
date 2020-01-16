
"""Report file.

This file contains the Report class, which main goal
is allocate the found threats and display a record
report after all the modeles has been executed.
"""

# Std libs
import re

# Own libs
from constants import Meta, Error, Regex
from enumerations.severity.severity_base import SeverityBase
from util import is_key_in_dict
from own_exceptions import BOAReportWhoNotFound

class Report:
    """Report class.

    It implements the necessary methods to initialize,
    fill and display the threats report after the analysis.
    """

    def __init__(self):
        self.who = []
        self.description = []
        self.severity = []
        self.advice = []
        self.rows = []
        self.cols = []
        self.summary = {}

    def add(self, who, description, severity, advice=None, row=None, col=None):
        """It adds a new record to the main report.

        Arguments:
            who (str): "module_name.class_name" (without quotes)
                format to identify who raised the threat.
            description (str): description about the found threat.
            severity (SeverityBase): threat severity.
            advice (str): advice to solve the threat. It is optional.

        Returns:
            int: status code
        """
        # Checking mandatory args
        if (who is None or
                description is None or
                severity is None):
            return Error.error_report_args_not_optional
        # Type checking
        if (not isinstance(who, str) or
                not isinstance(description, str) or
                not isinstance(severity, SeverityBase) or
                (advice is not None and
                 not isinstance(advice, str)) or
                (row is not None and
                 not isinstance(row, int)) or
                (col is not None and
                 not isinstance(col, int))):
            return Error.error_report_args_not_expected_type

        who_regex_result = re.match(Regex.regex_report_module_class_name, who)

        if who_regex_result is None:
            return Error.error_report_who_regex_fail

        self.who.append(who)
        self.description.append(description)
        self.severity.append(severity.name)
        self.advice.append(advice)
        self.rows.append(row)
        self.cols.append(col)

        if not is_key_in_dict(self.summary, who):
            # If it is the first threat found by the module, create a list to iterate after
            self.summary[who] = []

        # Create a tuple with all the record information
        self.summary[who].append((self.who[-1],
                                  self.description[-1],
                                  self.severity[-1],
                                  self.advice[-1],
                                  self.rows[-1],
                                  self.cols[-1]))

        return Meta.ok_code

    def get_summary(self):
        """It returns a summary of all the threat records.

        Returns:
            dict: summary of threat records. Its key format
            is (without quotes) "module_name.class_name" and
            the value is a list of tuples.
        """
        return self.summary

    def pretty_print_tuple(self, t, first_time=False, reported_by=False):
        """It prints a pretty line about a found threat record.

        The expected format for the tuple is next:\n
        1. str: module who raised the threat.\n
        2. str: threat description.\n
        3. SeverityBase: threat severity.\n
        4. str (optional): advice for solving the threat.\n
        5. int (optional): threat row.\n
        6. int (optional): threat col.

        Arguments:
            t (tuple): threat record.
            first_time (bool): if you want to display a pretty
                box around the module name who raised the threat,
                this value must be *True*. The default value is
                *False*.
            reported_by (bool): if you want to display the module
                who raised the threat, this value must be *True*.
                This arg should be used when you want to avoid
                the arg *first_time*. The default value is *False*.

        Note:
            If you want to show orderly the threats, you should
            use *first_time=True* for the first record and
            *first_time=False* for the rest. If you do not want
            to show it orderly, you should use *reported_by=True*.
        """
        row = t[4]
        col = t[5]
        who = t[0]
        desc = t[1]
        severity = t[2]
        advice = t[3]

        if first_time:
            first_time_row = f"~~~~{'~' * len(who)}~~~~"

            print(first_time_row)
            print(first_time_row)
            print(f"~~~ {who} ~~~")
            print(first_time_row)
            print(first_time_row)

        if not reported_by:
            who = "Threat"
        if row is None:
            row = -1
        if col is None:
            col = -1
        if advice is None:
            advice = "not specified"

        print(f" + {who} ({row}, {col}): {desc}.")
        print(f"   Severity: {severity}.")
        print(f"   Advice: {advice}.")

    def display(self, who):
        """It displays all the threats from a concrete module.

        Arguments:
            who (str): the module which found the threat.

        Raises:
            BOAReportWhoNotFound: if the given module is not found.
        """
        if who not in self.who:
            raise BOAReportWhoNotFound()

        first_time = True

        for threat in self.summary[who]:
            self.pretty_print_tuple(threat, first_time)
            first_time = False
            print("")

        print(f"   Total threats: {len(self.summary[who])}")
        print("")

    def display_all(self):
        """It displays all the threats from all the modules.
        Moreover, it prints a summary at the end.
        """
        total_threats = 0

        for who in list(self.summary.keys()):
            self.display(who)
            total_threats += len(self.summary[who])

        print("~~~~~~~~~~~")
        print("~ Summary ~")
        print("~~~~~~~~~~~")
        print(f" - Total threats (all modules): {total_threats}")
