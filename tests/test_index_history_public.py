"""Unit tests for the index page when user is logged in."""
from test_base_many_posts import TestBaseManyPosts


class TestIndexHistoryPublic(TestBaseManyPosts):
    """Unit tests for index page."""

    def test_history_posts(self):
        """Test that same 10 posts appear when returning to main page.

        Go to index page, go to explore, return to main page
        using back button, assert that the same 10 posts exist on main page.
        """
        # pylint: disable=redundant-unittest-assert
        self.assertPostsOnPage([x for x in range(95, 105)])

        self.navigate_to_explore_page()

        # return to main page and check that like is still on main page
        self.driver.back()
        self.assertPostsOnPage([x for x in range(95, 105)])
        self.assertNoJSExceptions()
