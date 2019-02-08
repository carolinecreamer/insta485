"""Unit tests for REST API."""
import util
from test_base_rest_api import TestBaseRestAPI


class TestRestAPIQuery(TestBaseRestAPI):
    # pylint: disable=redundant-unittest-assert
    """Unit tests for REST API query."""

    def test_check_query(self):
        """Checks for 404 if query string parameters incorrect."""
        response = self.app.get(self.get_server_url() +
                                util.posts_size_page("page", -1))
        self.assertEqual(response.status_code, 400,
                         "Incorrect response code,\
                          when trying incorrect querystring parameter")
        response = self.app.get(self.get_server_url() +
                                util.posts_size_page("size", -1))
        self.assertEqual(response.status_code, 400,
                         "Incorrect response code,\
                          when trying incorrect querystring parameter")

    def test_1000_errors(self):
        """Tests out of postid range errors."""
        # checks p/1000/
        response = self.app.get(self.get_server_url() +
                                util.posts_comment_like(1000))
        self.assertEqual(response.status_code, 404,
                         "PostId out of range did not return 404")
        # checks p/1000/comments/
        response = self.app.get(self.get_server_url() +
                                util.posts_comment_like(1000, 'comments'))
        self.assertEqual(response.status_code, 404,
                         "PostId out of range did not return 404")
        # checks p/1000/likes/
        response = self.app.get(self.get_server_url() +
                                util.posts_comment_like(1000, 'likes'))
        self.assertEqual(response.status_code, 404,
                         "PostId out of range did not return 404")
