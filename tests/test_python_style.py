"""
Check Python style with pycodestyle, pydocstyle and pylint.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import unittest

import sh


class TestPythonStyle(unittest.TestCase):
    """Unit tests for Python code style."""

    @classmethod
    def setUpClass(cls):
        # pylint: disable=no-member
        """Display tool versions."""
        print("Dumping tool versions")
        output = sh.pycodestyle("--version")
        version = output.stdout.decode('utf-8').strip()
        print("pycodestyle {}".format(version))
        output = sh.pydocstyle("--version")
        version = output.stdout.decode('utf-8').strip()
        print("pydocstyle {}".format(version))
        output = sh.pylint("--version")
        version = output.stdout.decode('utf-8').strip()
        print(version)  # pylint already announces it's own name

    def test_pycodestyle(self):
        # pylint: disable=no-member
        """Run `pycodestyle setup.py insta485`."""
        output = sh.pycodestyle("setup.py", "insta485")
        self.assertEqual(output.exit_code, 0, output.stdout.decode('utf-8'))

    def test_pydocstyle(self):
        """Run `pydocstyle setup.py insta485`."""
        output = sh.pydocstyle("setup.py", "insta485")
        self.assertEqual(output.exit_code, 0, output.stdout.decode('utf-8'))

    def test_pylint(self):
        # pylint: disable=no-member
        """Run `pylint --reports=n --disable=cyclic-import insta485`."""
        output = sh.pylint(
            "--reports=n",
            "--disable=cyclic-import",
            "--disable=no-member",
            "insta485"
        )
        check = "Locally disabling" in output
        has_single_disable = output.count('Locally disabling') == 1
        alwd_disable = "Locally disabling no-value-for-parameter" in output
        if has_single_disable and alwd_disable:
            check = False
        self.assertFalse(check,
                         "You are not allowed to disable pylint checks!")
        self.assertEqual(output.exit_code, 0, output.stdout.decode('utf-8'))
