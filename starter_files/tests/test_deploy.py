"""Unit tests for code deployment."""

import unittest


class TestDeploy(unittest.TestCase):
    """Unit tests for REST API."""

    def test_deploy(self):
        """Tests the student curl output for their deployed site."""
        html_output = ""
        stderr_output = ""
        with open("deployed_index.html") as infile:
            for line in infile:
                html_output += line
        with open("deployed_index.log") as infile:
            for line in infile:
                stderr_output += line
        print("stderr out")
        print(stderr_output)
        passes = "localhost" not in stderr_output and "amazonaws.com" \
            in stderr_output and \
            "200 OK" in stderr_output and \
            "nginx" in stderr_output \
            and "404 NOT FOUND" not in stderr_output and \
            "Connection refused" not in stderr_output and \
            "<script" in html_output and \
            "bundle.js" in html_output

        # pylint: disable=redundant-unittest-assert
        self.assertTrue(passes, "Curl dump incorrect")
