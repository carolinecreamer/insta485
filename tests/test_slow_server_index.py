"""
Check if website renders without errors even with a very slow REST API server.

- slow posts
- slow likes
- slow comments
- slow everything
"""
import selenium
from selenium.webdriver.common.keys import Keys

import config
from test_base_live import TestBaseLive


class TestSlowServerIndex(TestBaseLive):
    """Unit tests for main React/JS page connected to slow REST API server."""

    def setUp(self):
        # pylint: disable=redundant-unittest-assert
        """Override parent class implicit wait to be longer for slow tests."""
        super(TestSlowServerIndex, self).setUp()
        super(TestSlowServerIndex, self).try_login()
        # seconds waiting for DOM elements
        self.driver.implicitly_wait(config.SLOW_IMPLICIT_WAIT_TIME)

    def create_app(self):
        """
        Create an instance of the student solution Flask app.

        Use the app version with slow api calls.

        NOTE: this overrides the create_app method in TestBaseLive
        intentionally.
        """
        from insta485_logging_slow import app
        app.config["TESTING"] = True
        app.config["LIVESERVER_PORT"] = config.TEST_PORT
        return app

    def test_feed_load(self):
        # pylint: disable=redundant-unittest-assert
        """Test that post feed loads when visiting index."""
        self.assertPostsOnPage([1, 2, 3])
        self.assertNoJSExceptions()

    def test_comment(self):
        # pylint: disable=redundant-unittest-assert
        """Test that comment on post appears on index without refresh."""
        self.assertPostsOnPage([1, 2, 3])
        # Make a comment on post 1
        comment = "test comment"
        # the last comment form on the page which is post 1
        comment_box_xpath = ("//form[@id='comment-form']"
                             "//input[@type='text']")
        try:
            comment_box = self.driver.find_element_by_xpath(comment_box_xpath)
        except selenium.common.exceptions.NoSuchElementException:
            self.assertTrue(False, ("Could not locate comment form on main "
                                    "page."))
        comment_box.send_keys(comment)
        comment_box.send_keys(Keys.RETURN)

        # Check that comment exists
        comment_xpath = "//*[text()[contains(.,'{}')]]".format(comment)
        try:
            self.driver.find_element_by_xpath(comment_xpath)
        except selenium.common.exceptions.NoSuchElementException:
            self.assertTrue(False, ("Failed to find newly posted comment on "
                                    "main page without reload"))

        expected_requests = ["POST /api/v1/p/3/comments/", ]
        self.assertAPIRequestsExist(expected_requests)

        self.assertNoJSExceptions()

    def test_like_unlike(self):
        # pylint: disable=redundant-unittest-assert
        """Test post like/unlike appears on index without refresh."""
        self.assertPostsOnPage([1, 2, 3])
        # currently liked before click
        self.assertPostsOnPage([1, 2, 3])
        self.click_first_like_button()

        # Check that like has propogated to DOM
        # first post started with 1 like by awdeorio, now it has 0
        like_text = "0 likes"
        like_xpath = "//*[normalize-space() = '{}']".format(like_text)
        try:
            self.driver.find_element_by_xpath(like_xpath)
        except selenium.common.exceptions.NoSuchElementException:
            self.assertTrue(False, ("Unlike does not appear on main page "
                                    "without reload"))

        # currently 0 likes before click
        self.click_first_like_button()

        like_text = "1 like"
        like_xpath = "//*[normalize-space() = '{}']".format(like_text)
        try:
            self.driver.find_element_by_xpath(like_xpath)
        except selenium.common.exceptions.NoSuchElementException:
            self.assertTrue(False, ("Like does not appear on main page "
                                    "without reload"))

        expected_requests = ["DELETE /api/v1/p/3/likes/",
                             "POST /api/v1/p/3/likes/"]
        self.assertAPIRequestsExist(expected_requests)
        self.assertNoJSExceptions()

    def test_refresh(self):
        """Test refresh on main page with new content.

        Go to main page, make a post from background, refresh the page,
        make sure 10 most recent posts appear including the previously made,
        new post.
        """
        # pylint: disable=redundant-unittest-assert
        self.assertPostsOnPage([1, 2, 3])
        self.create_post(config.AWDEORIO_USER)  # user

        self.driver.get(self.driver.current_url)
        self.assertPostsOnPage([1, 2, 3, 5])
        self.assertNoJSExceptions()
