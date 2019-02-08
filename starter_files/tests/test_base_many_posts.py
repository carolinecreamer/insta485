"""Base class for logging in user and generating random posts during tests."""
import sh
import selenium

import util
from test_base_live import TestBaseLive
import config


class TestBaseManyPosts(TestBaseLive):
    """Base class for unit tests to generate posts."""

    def setUp(self):
        # pylint: disable=redundant-unittest-assert
        """Generate posts in the DB. Login awdeorio."""
        # Call test base setup method to initialize the driver and
        # other class members
        super(TestBaseManyPosts, self).setUp()
        # Generate random posts in DB
        try:
            insta485db = sh.Command("./bin/insta485db")
            running_command = insta485db("random")
            running_command.wait()
        except sh.ErrorReturnCode as error:
            self.assertTrue(False, ("Failed to generate random posts using "
                                    "insta485db random, error: "
                                    "{}.").format(error))
        try:
            util.log_in_user(self.driver, self.get_server_url())
        except selenium.common.exceptions.WebDriverException:
            self.assertTrue(False, ("Failed to login to insta485 with "
                                    "user {}").format(config.AWDEORIO_USER))
