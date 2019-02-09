"""Unit tests for infinite scroll on index page."""
import config
from test_base_many_posts import TestBaseManyPosts


class TestIndexScroll(TestBaseManyPosts):
    """Unit tests for index page."""

    def test_infinite_scroll(self):
        # pylint: disable=redundant-unittest-assert
        """Test infinite scroll."""
        # NOTE: do not load index page here because it will have already been
        #       loaded from redirect during login in setUp
        self.assertPostsOnPage([x for x in range(95, 105)])

        self.scroll_to_bottom_of_page()

        self.assertPostsOnPage([x for x in range(85, 105)])
        # expected_requests = ["GET /api/v1/p/?size=10&page=1"]
        # self.assertAPIRequestsExist(expected_requests)
        self.assertNoJSExceptions()

    def test_infinite_scroll_many(self):
        # pylint: disable=redundant-unittest-assert
        """Test many infinite scrolls."""
        # NOTE: do not load index page here because it will have already been
        #       loaded from redirect during login in setUp
        self.assertPostsOnPage([x for x in range(95, 105)])

        self.scroll_to_bottom_of_page()

        self.assertPostsOnPage([x for x in range(85, 105)])
        # expected_requests = ["GET /api/v1/p/?size=10&page=1"]
        # self.assertAPIRequestsExist(expected_requests)
        self.scroll_to_bottom_of_page()
        self.assertPostsOnPage([x for x in range(75, 105)])
        # expected_requests = ["GET /api/v1/p/?size=10&page=2"]
        # self.assertAPIRequestsExist(expected_requests)
        self.assertNoJSExceptions()

    def test_scroll_refresh(self):
        """Test infinite scroll with refresh afterward.

        Go to main page, scroll to trigger infinite scroll, make a post from
        background, refresh the page, make sure only 10 posts appear including
        the previously made, new post.
        """
        # pylint: disable=redundant-unittest-assert
        self.assertPostsOnPage([x for x in range(95, 105)])

        self.scroll_to_bottom_of_page()

        self.assertPostsOnPage([x for x in range(85, 105)])
        # expected_requests = ["GET /api/v1/p/?size=10&page=1"]
        # self.assertAPIRequestsExist(expected_requests)
        self.create_post(config.AWDEORIO_USER)  # user
        self.driver.get(self.driver.current_url)
        self.assertPostsOnPage([x for x in range(96, 106)])
        self.assertNoJSExceptions()
