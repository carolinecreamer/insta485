"""Unit tests for REST API."""
import json
import sh

import util
from test_base_rest_api import TestBaseRestAPI


class TestRestAPIResponse(TestBaseRestAPI):
    # pylint: disable=redundant-unittest-assert
    """Unit tests for REST API responses."""

    def test_404_array(self):
        """Checks javascript infinite scroll."""
        # intially checks that "next" is empty
        response = self.app.get(self.get_server_url() + util.V_1P)
        json_value = json.loads(response.get_data().decode('utf8'))

        if 'next' in json_value:
            self.assertEqual(json_value["next"], "",
                             "Error: next url was not empty on db reset")
        else:
            self.assertTrue(False, "Error: incorrect json object")

        # fill the database with random values
        try:
            insta485db = sh.Command("./bin/insta485db")
            insta485db("random")
        except sh.ErrorReturnCode as error:
            self.assertTrue(False, ("Failed to generate random posts using "
                                    "insta485db random, error: "
                                    "{}.").format(error))
        # check that next gives a url
        response = self.app.get(self.get_server_url() + util.V_1P)
        json_value = json.loads(response.get_data().decode('utf8'))
        if 'next' in json_value:
            self.assertTrue(json_value['next'],
                            "Error: incorrect url for next page of posts")
        else:
            self.assertTrue(False, "Error: incorrect json object")


    def test_correct_responses(self):
        """Checks correct response for POST and DELETE Requests."""
        response = self.app.post(util.posts_comment_like(3, 'comments'),
                                 data=json.dumps(dict(text='autograder test')),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201,
                         "Error: incorrect response when POST request sent")
        # send delete request to like
        response = self.app.delete(util.posts_comment_like(3, 'likes'),
                                   data=json.dumps({}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 204,
                         "Error: incorrect response when DELETE request sent")

        # send a post request to like
        response = self.app.post(util.posts_comment_like(3, 'likes'),
                                 data=json.dumps({}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 201,
                         "Error: incorrect response when POST request sent")

        # send same like check that it is a 409
        response = self.app.post(util.posts_comment_like(3, 'likes'),
                                 data=json.dumps({}),
                                 content_type='application/json')
        # check json description
        json_value = json.loads(response.get_data().decode('utf8'))
        if 'message' not in json_value:
            self.assertTrue(False, "Error: no message \
                            response after incorrect POST")

        self.assertEqual(response.status_code, 409,
                         "Error: incorrect response when POST request sent")


    def test_logout_403(self):
        """Logs user out, and tests all api routes for 403 response."""
        response = self.logout()
        self.assertEqual(response.status_code, 302,
                         "Incorrect response code, when logging out")
        response = self.app.get(self.get_server_url() +
                                util.posts_size_page("page", 1))
        self.assertEqual(response.status_code, 403,
                         "Incorrect response code, when user not authorized")
        response = self.app.get(self.get_server_url() +
                                util.posts_size_page("size", 1))
        self.assertEqual(response.status_code, 403,
                         "Incorrect response code, when user not authorized")
        response = self.app.get(self.get_server_url() +
                                util.V_1)
        self.assertEqual(response.status_code, 403,
                         "Incorrect response code, when user not authorized")
        response = self.app.get(self.get_server_url() +
                                util.V_1P)
        self.assertEqual(response.status_code, 403,
                         "Incorrect response code, when user not authorized")
