"""
Test /u/<user_url_slug/following/ URLs.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import unittest
import sh
import insta485
import util


class TestFollowing(unittest.TestCase):
    """Unit tests for /u/<user_url_slug>/following/ URLs."""

    def setUp(self):
        """Reset database, start app test client, and log in awdeorio.

        This function runs once before each member function unit test.
        """
        # Reset the database and start a test client.  Disable error catching
        # during request handling so that you get better error reports when
        # performing test requests against the application.
        insta485db = sh.Command("./bin/insta485db")
        insta485db("reset")
        insta485.app.config["TESTING"] = True
        self.app = insta485.app.test_client()

    def test_awdeorio_following(self):
        """Check default content at /u/awdeorio/following/ URL."""
        # Login
        response = self.app.post(
            "/accounts/login/",
            data={"username": "awdeorio", "password": "password"},
        )
        self.assertEqual(response.status_code, 302,
                         "POST /accounts/login/ did not return 302.")
        response = self.app.get("/u/awdeorio/following/")

        self.assertEqual(response.status_code, 200,
                         "GET for /u/awdeorio/following/ did not return 200.")

        soup_dict = util.get_soup_dict(response.data)
        links = soup_dict["links"]
        srcs = soup_dict["srcs"]
        text = soup_dict["text"]
        # Check for text
        self.assertEqual(2, text.count("following"),
                         "Issue encountered with the expected text.")
        in_cont = []
        out_cont = ["not following"]
        check = util.check_for_content(in_cont, out_cont, text)
        self.assertTrue(check, "Issue encountered with the expected text.")

        # Check for images
        in_cont = [util.MIKE_PIC, util.JASON_PIC]
        out_cont = [util.JAG_PIC]
        check = util.check_for_content(in_cont, out_cont, srcs)
        self.assertTrue(check,
                        "Issue encountered with the expected user images.")

        in_cont = ["/u/jflinn/", "/u/michjc/"]
        out_cont = ["/u/jag/"]
        check = util.check_for_content(in_cont, out_cont, links)
        self.assertTrue(check, "Issue encountered with the expected links.")

        # pylint: disable=redundant-unittest-assert
