
# Std libs
import os
import re
import unittest
import subprocess

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

class BOADynamicBasicFuzzing(unittest.TestCase):

    def test_basic_fuzzing_1(self):
        self.maxDiff = None
        target = "/usr/bin/false"
        rules_file = f"{get_script_dir()}/../../../boa/rules/rules-dynamic-basic_fuzzing.xml"

        actual = subprocess.run([f"{get_script_dir()}/../../../boa/boa.py", target, rules_file], check=False, capture_output=True, text=True)
        actual_stdout_grep = subprocess.run(["egrep", "\\s*\\+ Threat|\\s*Severity:|\\s*Advice:"], input=actual.stdout, capture_output=True, check=False, text=True)

        expected_stdout = \
"""\
 + Threat (-1, -1): the input '' returned the status code 1.
   Severity: FAILED.
   Advice: check if the fail is not a false positive.
 + Threat (-1, -1): the input '' returned the status code 1.
   Severity: FAILED.
   Advice: check if the fail is not a false positive.
"""

        # Remove the dynamic input
        actual_stdout_grep_stdout = actual_stdout_grep.stdout
        actual_stdout_grep_stdout_after = re.sub(r'the input \'[^\']*\' returned', 'the input \'\' returned', actual_stdout_grep_stdout)

        self.assertEqual(expected_stdout, actual_stdout_grep_stdout_after)

if __name__ == "__main__":
    unittest.main()
