
# Std libs
import unittest
import os
import subprocess

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

class BOAStaticPycparserC(unittest.TestCase):

    def get_env(self, force=False):
        env = os.environ.copy()

        if ("PYCPARSER_FAKE_LIBC_INCLUDE_PATH" not in os.environ or force):
            env["PYCPARSER_FAKE_LIBC_INCLUDE_PATH"] = f"{get_script_dir()}/../pycparser-2.20/utils/fake_libc_include"

        return env

    def test_functions_basic_overflow_1(self):
        c_file = f"{get_script_dir()}/../../C/synthetic/test_basic_buffer_overflow.c"
        rules_file = f"{get_script_dir()}/../../../boa/rules/rules_static_function_match_pycparser.xml"
        env = self.get_env()

        actual = subprocess.run([f"{get_script_dir()}/../../../boa/boa.py", c_file, rules_file], check=False, capture_output=True, text=True, env=env)
        actual_stdout_grep = subprocess.run(["egrep", "\\s*\\+ Threat|\\s*Severity:|\\s*Advice:"], input=actual.stdout, capture_output=True, check=False, text=True)

        expected_stdout = \
"""\
 + Threat (10, 9): strcpy: destination pointer (first argument) length has to be greater or equal than origin (second argument) to avoid buffer overflow threats.
   Severity: FREQUENTLY MISUSED.
   Advice: You can use 'strcpy', but be sure about the length problem (check boundaries) and set correctly the end character. If you want a safer function, check 'strncpy', which is safer but not safe or 'strlcpy'.
 + Threat (14, 9): strcpy: destination pointer (first argument) length has to be greater or equal than origin (second argument) to avoid buffer overflow threats.
   Severity: FREQUENTLY MISUSED.
   Advice: You can use 'strcpy', but be sure about the length problem (check boundaries) and set correctly the end character. If you want a safer function, check 'strncpy', which is safer but not safe or 'strlcpy'.
 + Threat (17, 5): printf: first argument has to be constant and not an user controlled input to avoid buffer overflow and data leakage.
   Severity: MISUSED.
   Advice: Use a constant value as first parameter.
"""

        self.assertEqual(expected_stdout, actual_stdout_grep.stdout)

if __name__ == "__main__":
    unittest.main()
