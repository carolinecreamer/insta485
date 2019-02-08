"""
Check JavaScript style with eslint.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import os
import unittest
import sh
import util


class TestJavaScriptStyle(unittest.TestCase):
    """Unit tests for Python code style."""

    @classmethod
    def setUpClass(cls):
        """Display tool versions."""
        print("Dumping tool versions")
        cls.eslint = sh.Command(os.path.join(util.NODE_MODULES_BIN, "eslint"))
        output = cls.eslint("--version")
        version = output.stdout.decode('utf-8').strip()
        print("eslint {}".format(version))

    def test_eslint(self):
        """Run `./node_modules/.bin/eslint --ext js,jsx insta485/js/`."""
        output = self.eslint("--ext", "js,jsx", "insta485/js/")
        self.assertEqual(output.exit_code, 0, output.stdout.decode('utf-8'))
