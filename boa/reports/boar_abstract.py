"""This file contains the class which is the base for
the Report, which is the class that displays the information
about all the found threats.
"""

# Std libs
import re
from abc import abstractmethod

# Own libs
from constants import Meta, Error, Regex
from enumerations.severity.severity_base import SeverityBase
from util import is_key_in_dict, eprint, get_name_from_class_instance
from own_exceptions import BOAReportWhoNotFound, BOAReportEnumTypeNotExpected

class BOAReportAbstract:
    """BOAReportAbstract class.

    It implements the necessary methods to initialize,
    fill and display the threats report after the analysis.

    If you want to define your own Report class you will have
    to define a new class which inherits from this one.
    """

    def __init__(self, severity_enum, args):
        """It initializes the class with the necessary variables.

        Arguments:
            severity_enum (type): enumeration which will be used
                for the threats severity. It has to inherit from
                *SeverityBase* but not be *SeverityBase*.

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
        self.severity_enum_mapping = {}
        self.args = args
        self.who_i_am = get_name_from_class_instance(self)

        if (not issubclass(severity_enum, SeverityBase) or
                severity_enum is SeverityBase):
            raise BOAReportEnumTypeNotExpected()

    @abstractmethod
    def pretty_print_tuple(self, t, first_time=False, reported_by=False, display=True):
        """It prints a pretty line about a found threat record.

        This method is intended to be invoked by *display*.

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
        7. type: SeverityBase type which will be used to display
            the severity. This value is intented to be able to
            join different Report instances.

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
            display (bool): if *True*, it displays the threat.

        Returns:
            str: text to be displayed

        Note:
            If you want to show orderly the threats, you should
            use *first_time=True* for the first record and
            *first_time=False* for the rest. If you do not want
            to show it orderly, you should use *reported_by=True*.
        """

    @abstractmethod
    def display(self, who, display=True):
        """It displays all the threats from a concrete module.

        This method is intended to be invoked by *display_all*.

        Arguments:
            who (str): the module which found the threat.
            display (bool): if *True*, it displays the threat.

        Raises:
            BOAReportWhoNotFound: if the given module is not found.

        Returns:
            str: text to be displayed
        """

    @abstractmethod
    def display_all(self, print_summary=True, display=True):
        """It displays all the threats from all the modules.
        Moreover, it prints a summary at the end optionally.

        This method should invoke *display* which should
        invoke *pretty_print_tuple*. You can avoid this
        overriding the methods using "pass", but if you do
        this, this method will have to make all the work.

        Arguments:
            print_summary (bool): if *True*, it prints a
                summary with statistics about all the found
                threats.
            display (bool): if *True*, it displays the threat.

        Returns:
            str: text to be displayed
        """

    def get_who(self):
        """It returns the modules which are in the current report.
        Returns:
            list (str): list containing the modules which are in the
            current report
        """
        return self.who

    def add(self, who, description, severity, advice=None, row=None, col=None, sort_by_severity=True, severity_enum=None):
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
            severity_enum (type): enumeration which will be used
                for the threats severity. This arg is intended to
                be able to join different Report instances. Default
                is *None* which means to use *self.severity_enum*.
        Returns:
            int: status code
        """
        # Checking mandatory args
        if (who is None or
                description is None or
                severity is None):
            return Error.error_report_args_not_optional
        # Severity enum checking
        if severity_enum is None:
            if is_key_in_dict(self.severity_enum_mapping, who):
                severity_enum = self.severity_enum_mapping[who]
            else:
                severity_enum = self.severity_enum
        elif (not issubclass(severity_enum, SeverityBase) or
              severity_enum is SeverityBase):
            raise BOAReportEnumTypeNotExpected()
        # Type checking
        if (not isinstance(who, str) or
                not isinstance(description, str) or
                not isinstance(severity, severity_enum) or
                (advice is not None and
                 not isinstance(advice, str)) or
                (row is not None and
                 not isinstance(row, int)) or
                (col is not None and
                 not isinstance(col, int))):
            return Error.error_report_args_not_expected_type

        who_regex_result = re.match(Regex.regex_general_module_class_name, who)

        if who_regex_result is None:
            return Error.error_report_who_regex_fail

        if not is_key_in_dict(self.severity_enum_mapping, who):
            self.severity_enum_mapping[who] = severity_enum
        elif self.severity_enum_mapping[who] != severity_enum:
            return Error.error_report_severity_enum_does_not_match

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
                        self.cols[-1],
                        severity_enum)

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
            the value is a list of tuples
        """
        return self.summary

    def append(self, report_instance, sort_by_severity=True, stop_if_fails=False, who=None):
        """It appends other threats report records to this.

        The goal of this method is to be able to append multiple reports
        which will be created for each module and end up with only a
        report to show to the user.

        Arguments:
            report_instance (Report): the report to be appended to this.
            sort_by_severity (bool): if *True*, the threats will be
                added sorting by severity (higher values will be
                added first). The default value is *True*.
            stop_if_fails (bool): if *True* and any threat record cannot
                be appended, the execution will stop. The default value
                if *False*.
            who (str): the module name which is going to be used to set
                the relation between the module and the report instance.

        Returns:
            int: status code
        """
        rtn_code = Meta.ok_code
        appended = False

        if not isinstance(report_instance, BOAReportAbstract):
            raise TypeError()

        for who_list in report_instance.summary.values():
            for t in who_list:
                tmp_rtn_code = self.add(t[0], t[1], t[2], t[3], t[4], t[5], sort_by_severity, t[6])

                if tmp_rtn_code != Meta.ok_code:
                    eprint(f"Error: could not append the element: {t}.")

                    rtn_code = Error.error_report_append_failed

                    if stop_if_fails:
                        return rtn_code

                appended = True

        if (not appended and rtn_code == Meta.ok_code):
            # Nothing was appended because the report instance is empty surely
            if who is None:
                rtn_code = Error.error_report_append_failed
            else:
                if not self.set_severity_enum_mapping(who, report_instance.get_severity_enum_instance()):
                    rtn_code = Error.error_report_append_failed

        return rtn_code

    def set_severity_enum_mapping(self, who, severity_enum_instance):
        """It sets the relation between a module and a severity enum.

        Arguments:
            who (str): the module name in format "module_name.class_name".
            severity_enum_instance (SeverityBase): severity enum instance.

        Returns:
            bool: it returns *True* if the relation was set. *False* otherwise
        """
        if is_key_in_dict(self.severity_enum_mapping, who):
            eprint("Warning: the severity enumeration is already set in the relation.")
            return False
        if (not issubclass(severity_enum_instance, SeverityBase) or
                severity_enum_instance is SeverityBase):
            eprint("Warning: the severity enumeration instance does not contain a valid class.")
            return False

        who_regex_result = re.match(Regex.regex_general_module_class_name, who)

        if who_regex_result is None:
            print(f"Warning: '{who}' did not pass the regex expression '{Regex.regex_general_module_class_name}'.")
            return False

        self.severity_enum_mapping[who] = severity_enum_instance

        return True

    def get_severity_enum_instance(self):
        """It returns the severity enumeration instance which
        is being used.

        Returns:
            SeverityBase: severity enumeration being used

        Note:
            This is the **GENERAL** severity enum reference, which
            may not be what you are looking for. If you want the
            severity enum instance of a concrete module, use
            *get_severity_enum_instance_by_who()* instead.
        """
        return self.severity_enum

    def get_severity_enum_instance_by_who(self, who):
        """It returns the severity enum instance of a concrete module.

        Arguments:
            who (str): module name in format "module_name.class_name".

        Returns:
            SeverityBase: the severity enum instance which is used for
            the given module. *None* if *who* is not found
        """
        if is_key_in_dict(self.severity_enum_mapping, who):
            return self.severity_enum_mapping[who]

        return None
