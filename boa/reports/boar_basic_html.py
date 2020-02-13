"""
"""

# Std libs
from datetime import datetime

# Own libs
from own_exceptions import BOAReportWhoNotFound, BOAReportException
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
        inner_html = ""

        if not reported_by:
            who = "Threat"

        # Add column values
        inner_html +=\
f"""                    <td>{who}</td>
                    <td>{row}</td>
                    <td>{col}</td>
                    <td>{severity_enum(severity).name}</td>
                    <td>{desc}</td>
                    <td>{advice}</td>"""

        return inner_html


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
        # Add HTML table header
        inner_html = \
f"""        <h3>{who}</h3>
        <table>
            <thead>
                <tr>
                    <th>Who</th>
                    <th>Row</th>
                    <th>Column</th>
                    <th>Severity</th>
                    <th>Description</th>
                    <th>Advice</th>
                </tr>
            </thead>
            <tbody>
"""

        for threat in self.summary[who]:
            inner_html +=\
f"""                <tr>
{self.pretty_print_tuple(threat, first_time, display=False)}
                </tr>"""
            first_time = False
            inner_html += "\n"

        # Close HTML tags and append footer with found threats
        inner_html += \
f"""            </tbody>
            <tfoot>
                <tr>
                    <td colspan="5">Total threats:</td>
                    <td>{len(self.summary[who])}</td>
                </tr>
            </tfoot>
        </table>"""

        return inner_html

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
        # Initial HTML tags and style
        inner_html =\
f"""<!DOCTYPE html>
<html lang="en">
    <head>
        <title>BOA - Report</title>
        <meta charset="utf-8" />
        <style>
            table, th, td{{
                border: 1px solid black;
            }}

            td{{
                padding: 5px;
            }}

            tfoot{{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h1>BOA - Report</h1>

"""

        while index < len(who):
            inner_html += self.display(who[index], False)
            total_threats += len(self.summary[who[index]])
            index += 1

        # Print summary
        if print_summary:
            inner_html +=\
f"""
        <h2>Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Total threats</td>
                    <td>{total_threats}</td>
                </tr>
            </tbody>
        </table>"""

        # Close HTML tags
        inner_html +=\
f"""
    </body>
</html>"""

        # Save inner HTML in a file
        self.save_html(inner_html)

    def save_html(self, inner_html):
        try:
            path = None

            if (not is_key_in_dict(self.args, "absolute_path") or
                    not is_key_in_dict(self.args, "filename")):
                raise BOAReportException("'absolute_path' and 'filename' has to be defined as args")

            if is_key_in_dict(self.args, "prefix_time"):
                if self.args["prefix_time"].lower() == "true":
                    now = datetime.now().strftime('%d-%m-%Y_%H:%M:%S')

                    path = f"{self.args['absolute_path']}/{now}{self.args['filename']}"

            if path is None:
                path = f"{self.args['absolute_path']}/{self.args['filename']}"

            file = open(path, "w")

            file.write(inner_html)

            print(f"Report: HTML report generated at '{path}'.")
        except Exception as e:
            eprint(f"Error: BOARBasicHTML: {e}.")
