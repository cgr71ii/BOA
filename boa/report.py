
"""Report file.

This file contains the Report class, which main goal
is allocate the found threats and display a record
report after all the modeles has been executed.
"""

# Std libs
import re
from enum import Enum

# Own libs
from constants import Meta, Error, Regex
from enumerations.severity.severity_base import SeverityBase
from util import is_key_in_dict
from own_exceptions import BOAReportWhoNotFound, BOAReportEnumTypeNotExpected

class Report:
    """Report class.

    It implements the necessary methods to initialize,
    fill and display the threats report after the analysis.
    """

    def __init__(self, severity_enum):
        """It initializes the class with the necessary variables.

        Arguments:
            severity_enum (type): enumeration which will be used
                for the threats severity. It has to inherit from
                SeverityBase but not be SeverityBase.

        Raises:
            BOAReportEnumTypeNotExpected: when *severity_enum* is
                not a type of *SeverityBase* or is *SeverityBase*.
            TypeError: when *severity_enum* is not a type or at
                least not an expected instance.
        """
        self.who = []
        self.description = []
        self.severity = []
        self.advice = []
        self.rows = []
        self.cols = []
        self.summary = {}
        self.severity_enum = severity_enum

        if (not issubclass(severity_enum, SeverityBase) or
                severity_enum is SeverityBase):
            raise BOAReportEnumTypeNotExpected()

    def add(self, who, description, severity, advice=None, row=None, col=None, sort_by_severity=True):
        """It adds a new record to the main report.

        Arguments:
            who (str): "module_name.class_name" (without quotes)
                format to identify who raised the threat.
            description (str): description about the found threat.
            severity (SeverityBase): threat severity.
            advice (str): advice to solve the threat. It is optional.
            row (int): threat row. It is optional.
            col (int): threat col. It is optional.
            sort_by_severity (bool): if *True*, the threats will be
                added sorting by severity (higher values will be
                added first). The default value is *True*.

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
                not isinstance(severity, self.severity_enum) or
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
        self.severity.append(severity)
        self.advice.append(advice)
        self.rows.append(row)
        self.cols.append(col)

        if not is_key_in_dict(self.summary, who):
            # If it is the first threat found by the module, create a list to iterate after
            self.summary[who] = []

        added = False
        threat_tuple = (self.who[-1],
                        self.description[-1],
                        self.severity[-1],
                        self.advice[-1],
                        self.rows[-1],
                        self.cols[-1])

        if sort_by_severity:
            index = 0

            # Iterate to find the first element whose severity is lesser than current
            while index < len(self.summary[who]):
                threat = self.summary[who][index]

                if threat[2] < self.severity[-1]:
                    self.summary[who].insert(index, threat_tuple)
                    added = True
                    break

                index += 1

        if (not sort_by_severity or not added):
            # Append the tuple with all the threat information
            self.summary[who].append(threat_tuple)

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
        4. str (optional): advice for solving the threat. If it
           is not provided, the string "not specified" will be
           displayed.\n
        5. int (optional): threat row. If it is not provided,
           the value -1 will be displayed.\n
        6. int (optional): threat col. If it is not provided,
           the value -1 will be displayed.

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
        print(f"   Severity: {self.severity_enum(severity).name}.")
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

    def display_all(self, print_summary=True):
        """It displays all the threats from all the modules.
        Moreover, it prints a summary at the end optionally.

        Arguments:
            print_summary (bool): if *True*, it prints a
                summary with statistics about all the found
                threats.
        """
        total_threats = 0
        who = list(self.summary.keys())
        index = 0

        while index < len(who):
            self.display(who[index])

            if (print_summary or index + 1 != len(who)):
                print("")

            total_threats += len(self.summary[who[index]])
            index += 1

        if print_summary:
            print("~~~~~~~~~~~")
            print("~ Summary ~")
            print("~~~~~~~~~~~")
            print(f" - Total threats (all modules): {total_threats}")
