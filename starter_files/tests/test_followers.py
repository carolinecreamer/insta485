"""
Test /u/<user_url_slug/followers/ URLs.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import unittest
import sh
import insta485
import util


class TestFollowers(unittest.TestCase):
    """Unit tests for /u/<user_url_slug>/followers/ URLs."""

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

    def test_awdeorio_followers(self):
        """Check default content at /u/awdeorio/followers/ URL."""
        # pylint: disable=redundant-unittest-assert

        response = self.app.post(
            "/accounts/login/",
            data={"username": "awdeorio", "password": "password"},
        )
        self.assertEqual(response.status_code, 302,
                         "POST /accounts/login/ did not return 302.")
        response = self.app.get("/u/awdeorio/followers/")
        self.assertEqual(response.status_code, 200,
                         "GET /u/awdeorio/followers/ did not return 200.")

        soup_dict = util.get_soup_dict(response.data)
        links = soup_dict["links"]
        srcs = soup_dict["srcs"]
        text = soup_dict["text"]
        buttons = soup_dict["buttons"]

        # Every page should have these
        self.assertTrue(util.check_header(links),
                        "Can't find an element in the header.")
        # Links specific to /u/awdeorio/followers/
        in_cont = ["/u/jflinn/", "/u/michjc/"]
        out_cont = ["/u/jag/"]
        check = util.check_for_content(in_cont, out_cont, links)
        self.assertTrue(check, "Issue encountered with the expected links.")
        # Check for images
        in_cont = [util.MIKE_PIC, util.JASON_PIC]
        out_cont = [util.JAG_PIC]
        check = util.check_for_content(in_cont, out_cont, srcs)
        self.assertTrue(check,
                        "Issue encountered with the expected user images.")
        # Check for text
        self.assertEqual(2, text.count("following"))
        in_cont = ["jflinn", "following", "michjc", "Followers"]
        out_cont = ["not following"]
        check = util.check_for_content(in_cont, out_cont, text)
        self.assertTrue(check, "Issue encountered with the expected text.")

        # Check for buttons
        in_cont = ["unfollow", "username"]
        out_cont = ["follow", "following"]
        check = util.check_for_content(in_cont, out_cont, buttons)
        self.assertTrue(check,
                        "Could not find buttons on /u/awdeorio/")
