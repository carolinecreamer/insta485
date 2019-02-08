"""
Unit tests for the index page when user is logged in.

TODO:
    - test submitting post while on main page, refresh, see if new post is
      included in top ten (make sure no caching)
"""
import selenium
from selenium.webdriver.common.keys import Keys

import config
from test_base_live import TestBaseLive


class TestIndex(TestBaseLive):
    """Unit tests for index page."""

    def setUp(self):
        # pylint: disable=redundant-unittest-assert
        """Login awdeorio."""
        # Call test base setup method to initialize the driver and
        # other class members
        super(TestIndex, self).setUp()
        super(TestIndex, self).try_login()

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
