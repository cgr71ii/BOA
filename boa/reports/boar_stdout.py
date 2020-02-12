
"""Report file.

This file contains the Report class, which main goal
is allocate the found threats and display a record
report after all the modeles has been executed.
"""

# Std libs
from reports.boar_abstract import BOAReportAbstract

# Own libs
from own_exceptions import BOAReportWhoNotFound

class BOARStdout(BOAReportAbstract):
    """Report class.

    It implements the necessary methods to initialize,
    fill and display the threats report after the analysis.
    """

    def pretty_print_tuple(self, t, first_time=False, reported_by=False, display=True):
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
        row = t[4]
        col = t[5]
        who = t[0]
        desc = t[1]
        severity = t[2]
        advice = t[3]
        severity_enum = t[6]
        text = ""

        if first_time:
            first_time_row = f"~~~~{'~' * len(who)}~~~~"

            text += f"{first_time_row}\n{first_time_row}\n"
            text += f"~~~ {who} ~~~\n"
            text += f"{first_time_row}\n{first_time_row}\n"

        if not reported_by:
            who = "Threat"
        if row is None:
            row = -1
        if col is None:
            col = -1
        if advice is None:
            advice = "not specified"

        text += f" + {who} ({row}, {col}): {desc}.\n"
        text += f"   Severity: {severity_enum(severity).name}.\n"
        text += f"   Advice: {advice}.\n"

        if display:
            print(text)

        return text

    def display(self, who, display=True):
        """It displays all the threats from a concrete module.

        Arguments:
            who (str): the module which found the threat.
            display (bool): if *True*, it displays the threat.

        Raises:
            BOAReportWhoNotFound: if the given module is not found.

        Returns:
            str: text to be displayed
        """
        if who not in self.who:
            raise BOAReportWhoNotFound()

        first_time = True
        text = ""

        for threat in self.summary[who]:
            text += self.pretty_print_tuple(threat, first_time, display=False)
            first_time = False
            text += "\n"

        text += f"   Total threats: {len(self.summary[who])}\n"

        if display:
            print(text)

        return text

    def display_all(self, print_summary=True, display=True):
        """It displays all the threats from all the modules.
        Moreover, it prints a summary at the end optionally.

        Arguments:
            print_summary (bool): if *True*, it prints a
                summary with statistics about all the found
                threats.
            display (bool): if *True*, it displays the threat.

        Returns:
            str: text to be displayed
        """
        total_threats = 0
        who = list(self.summary.keys())
        index = 0
        text = ""

        while index < len(who):
            text += self.display(who[index], False)

            if (print_summary or index + 1 != len(who)):
                text += "\n"

            total_threats += len(self.summary[who[index]])
            index += 1

        if print_summary:
            text += "~~~~~~~~~~~\n"
            text += "~ Summary ~\n"
            text += "~~~~~~~~~~~\n"
            text += f" - Total threats (all modules): {total_threats}"

        if display:
            print(text)

        return text
