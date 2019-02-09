"""
Test /u/<user_url_slug/ URLs.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import util
from test_base_rest_api import TestBaseRestAPI


class TestUserPublic(TestBaseRestAPI):
    """Unit tests for /u/<user_url_slug>/ URLs."""

    def test_awdeorio(self):
        """Check default content at /u/awdeorio/ URL."""
        # pylint: disable=redundant-unittest-assert
        response = self.app.post(
            "/accounts/login/",
            data={"username": "awdeorio", "password": "password"},
        )
        self.assertEqual(response.status_code, 302,
                         "POST /accounts/login/ did not return 302.")
        response = self.app.get("/u/awdeorio/")
        self.assertEqual(response.status_code, 200,
                         "GET /u/awdeorio/ did not return 200.")

        soup_dict = util.get_soup_dict(response.data)
        links = soup_dict["links"]
        srcs_a = soup_dict["srcs_a"]
        text = soup_dict["text"]
        buttons = soup_dict["buttons"]
        # Every page should have these
        self.assertTrue(util.check_header(links),
                        "Can't find an element in the header.")
        # Links specific to /u/awdeorio/followers/
        in_cont = ["/u/awdeorio/followers/", "/u/awdeorio/following/",
                   "/p/1/", "/p/3/"]
        out_cont = ["/u/jflinn/followers/", "/u/jflinn/following/",
                    "/u/michjc/followers/",
                    "/u/michjc/following/", "/u/jag/followers/",
                    "/u/jag/following/", "/p/2/", "/p/4/"]
        check = util.check_for_content(in_cont, out_cont, links)
        self.assertTrue(check, "Issue encountered with the expected links.")

        # Check for images
        in_cont = [util.POST_1, util.POST_3]
        out_cont = [util.POST_2, util.POST_4]
        check = util.check_for_content(in_cont, out_cont, srcs_a)
        self.assertTrue(check, "Issue encountered with the expected images.")

        # Check for text
        in_cont = ["2 posts", "2 followers", "2 following", "Andrew DeOrio",
                   "Edit profile", "logout"]
        out_cont = ["not following", "login"]
        check = util.check_for_content(in_cont, out_cont, text)
        self.assertTrue(check,
                        "Issue encountered with text or proper English.")

        self.assertEqual(2, text.count("awdeorio"),
                         "Issue encountered with the expected text.")
        self.assertEqual(1, text.count("following"),
                         "Issue encountered with the expected text.")

        # Check for buttons
        in_cont = ["file", "create_post"]
        out_cont = ["delete_post", "delete"]
        check = util.check_for_content(in_cont, out_cont, buttons)
        self.assertTrue(check,
                        "Could not find buttons on /u/awdeorio/")
