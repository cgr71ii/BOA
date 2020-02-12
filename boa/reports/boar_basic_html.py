"""
"""

# Std libs
from datetime import datetime

# Own libs
from own_exceptions import BOAReportWhoNotFound
from util import is_key_in_dict, eprint
from reports.boar_abstract import BOAReportAbstract

# TODO finish
class BOARBasicHTML(BOAReportAbstract):
    """
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
        inner_html = ""

        if first_time:
            inner_html += f"<h3>{self.who}</h3>\n"

        if not reported_by:
            who = "Threat"

        inner_html +=\
"""<table>

</table>"""


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
        inner_html =\
f"""<html>
    <head>
        <title>BOA - Report</title>
        <meta charset="utf-8" />
    </head>
    <body>
        <h1>BOA - Report</h1>

"""

        inner_html +=\
"""    </body>
</html>
        """

        self.save_html(inner_html)

    def save_html(self, inner_html):
        try:
            path = None

            if is_key_in_dict(self.args, "prefix_time"):
                if self.args["prefix_time"].lower() == "true":
                    now = datetime.now().strftime('%d-%m-%Y_%H:%M:%S')

                    path = f"{self.args['absolute_path']}/{now}{self.args['filename']}"

            if path is None:
                path = f"{self.args['absolute_path']}/{self.args['filename']}"

            file = open(path, "w")

            file.write(inner_html)

            print(f"HTML generated at '{path}'.")
        except Exception as e:
            eprint(f"Error: BOARBasicHTML: {e}.")
