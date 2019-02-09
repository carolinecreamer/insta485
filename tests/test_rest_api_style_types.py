"""Unit tests for REST API."""
import os
import json
import sh

import util
from test_base_rest_api import TestBaseRestAPI


class TestRestAPIStyleTypes(TestBaseRestAPI):
    # pylint: disable=redundant-unittest-assert
    """Unit tests for REST API style and types."""

    def test_json_style(self):
        """Checks json style of GET api route."""
        # define jsonlint command
        jsonlint = sh.Command(os.path.join(util.NODE_MODULES_BIN, "jsonlint"))

        # list of api_route url strings to test on
        test_list = [util.V_1, util.V_1P,
                     util.posts_size_page('size', 1),
                     util.posts_size_page('page', 1),
                     util.posts_comment_like(1),
                     util.posts_comment_like(1, 'comments'),
                     util.posts_comment_like(1, 'likes')]

        # gets json, sends it to jsonlint through stdin
        for api_route in test_list:
            response = self.app.get(self.get_server_url() + api_route)
            try:
                output = jsonlint(_in=response.get_data().decode('utf8'))
                self.assertEqual(output.exit_code, 0,
                                 output.stdout.decode('utf-8'))
            except sh.ErrorReturnCode as error:
                self.assertTrue(False, error)

    def test_check_types(self):
        """Test json data types."""
        # post id should be int
        response = self.app.get(self.get_server_url() +
                                util.V_1P)
        self.assertEqual(response.status_code, 200,
                         "Incorrect response from /api/vi/p/")
        json_value = json.loads(response.get_data().decode('utf8'))
        if 'results' not in json_value:
            self.assertTrue(False, "Error: incorrect json object")
        if 'postid' not in json_value['results'][0]:
            self.assertTrue(False, "Error: incorrect json object")
        self.assertTrue(isinstance(json_value["results"][0]["postid"], int),
                        "Postid is not type INT")

        # comment id should be an int
        response = self.app.get(self.get_server_url() +
                                util.posts_comment_like(1, "comments"))
        self.assertEqual(response.status_code, 200,
                         "Incorrect response from /api/vi/p/1/comments")
        json_value = json.loads(response.get_data().decode('utf8'))
        if 'comments' not in json_value:
            self.assertTrue(False, "Error: incorrect json object")
        if 'commentid' not in json_value['comments'][0]:
            self.assertTrue(False, "Error: incorrect json object")
        self.assertTrue(isinstance(json_value["comments"][0]["commentid"],
                                   int), "Commentid is not type INT")
