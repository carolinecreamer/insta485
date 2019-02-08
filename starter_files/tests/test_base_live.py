"""Flask base test class for running solution."""
import time
from datetime import datetime

import sh
from flask_testing import LiveServerTestCase
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import insta485_logging
from insta485_logging import app
import config
import util


class TestBaseLive(LiveServerTestCase):
    # pylint: disable=duplicate-code
    """Base class to create selenium driver and start live insta485 server."""

    def create_app(self):
        """Create an instance of the student solution Flask app."""
        app.config["TESTING"] = True
        app.config["LIVESERVER_PORT"] = config.TEST_PORT
        return app

    def setUp(self):
        """Set up the test driver and create test users."""
        # pylint: disable=redundant-unittest-assert
        options = Options()
        # Run headless
        if config.RUN_HEADLESS:
            options.add_argument("--headless")  # optional
        # Set the chrome binary location
        if config.CHROME_BIN:
            options.binary_location = config.CHROME_BIN

        # required for running in docker container
        options.add_argument("--no-sandbox")

        # Currently no documentation exists for accessing chrome console logs
        # from webdriver. See: https://stackoverflow.com/questions/44991009/
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'browser': 'SEVERE'}
        self.driver = webdriver.Chrome(
            options=options,
            desired_capabilities=capabilities,
        )
        # seconds waiting for DOM elements
        self.driver.implicitly_wait(config.IMPLICIT_WAIT_TIME)
        self.app = app.test_client()
        self.app_context = app.app_context()

        # Reset test state
        self.driver.delete_all_cookies()
        try:
            self.insta485db = sh.Command("./bin/insta485db")
            running_command = self.insta485db("reset")
            running_command.wait()
        except sh.ErrorReturnCode as error:
            err_str = ("Error occured while running student insta485db. "
                       "Output: {}").format((error.stderr).decode('ascii'))
            self.assertTrue(False, err_str)

    def tearDown(self):
        """Reset state for selenium driver and database."""
        # pylint: disable=redundant-unittest-assert
        insta485_logging.reset_log()
        # Shutdown chrome driver
        self.driver.quit()

    def assertNoJSExceptions(self):
        """
        Check the web driver for any Javascript exceptions in the console logs.

        Raises a unittest assertTrue exception if JS exceptions exist.
        """
        # pylint: disable=redundant-unittest-assert
        # pylint: disable=invalid-name
        js_exceptions = self.driver.get_log('browser')
        js_exceptions = \
            [x for x in js_exceptions if x['source'] == 'javascript']
        if js_exceptions:
            self.assertTrue(False, ("Found JS exceptions on page: "
                                    "{}".format(js_exceptions)))

    def assertPostsOnPage(self, post_ids):
        """
        Check the current page for the chosen posts.

        TODO: add checks for comment box, like button, and image on each post

        Searches for the specified posts on the page by checking for their
        links. Raises a unittest assertTrue exception if posts do not exist on
        page.
        """
        # pylint: disable=redundant-unittest-assert
        # pylint: disable=invalid-name
        for post_id in post_ids:
            try:
                post_url = "/p/{}/".format(post_id)
                self.driver.find_element_by_xpath(
                    "//a[@href='{}']".format(post_url))
            except selenium.common.exceptions.NoSuchElementException:
                self.assertTrue(False, ("Could not find post {} on "
                                        "page.").format(post_id))

            expected_requests = ["GET /api/v1/p/",
                                 "GET /api/v1/p/{}/likes/".format(post_id),
                                 "GET /api/v1/p/{}/comments/".format(post_id),
                                 "GET /api/v1/p/{}/".format(post_id)]
            self.assertAPIRequestsExist(expected_requests)

    def assertAPIRequestsExist(self, requests):
        """
        Assert that API requests exist in the request log.

        Raises unttest assertTrue if any one of the requests cannot be found in
        the request log after config.API_REQUEST_WAIT seconds
        """
        # pylint: disable=redundant-unittest-assert
        # pylint: disable=invalid-name
        for request in requests:
            start_time = datetime.now()
            request_found = False
            while ((datetime.now() - start_time).seconds <
                   config.API_REQUEST_WAIT and not request_found):
                with open(config.TEST_LOG, 'r') as ifh:
                    log_content = ifh.read()
                request_found = request in log_content
                if not request_found:
                    time.sleep(config.API_REQUEST_CHECK_INTERVAL)
            self.assertTrue(request_found,
                            ("API request {} expected to have been made but "
                             "was not found").format(request))

    def click_first_like_button(self):
        """
        Click the first like button on the current page.

        Raises unittest assertTrue if the like button cannot be located.
        """
        # pylint: disable=redundant-unittest-assert
        like_button_xpath = "//button[@id='like-unlike-button']"
        try:
            like_button = self.driver.find_element_by_xpath(like_button_xpath)
        except selenium.common.exceptions.NoSuchElementException:
            self.assertTrue(False, ("Could not locate like button on main "
                                    "page."))
        like_button.click()

    def navigate_to_explore_page(self):
        """
        Navigate the driver to the explore page using on-page link.

        Raise unittest assertTrue if explore link is not found.
        """
        # pylint: disable=redundant-unittest-assert
        explore_link_xpath = "//a[@href='/explore/']"
        try:
            explore_link = \
                self.driver.find_element_by_xpath(explore_link_xpath)
        except selenium.common.exceptions.NoSuchElementException:
            self.assertTrue(False, ("Could not locate explore button on main "
                                    "page."))
        explore_link.click()

    def create_post(self, user):
        """
        Create a post with user awdeorio using requests (not webdriver).

        Assumes that awdeorio is already logged in.
        """
        # login
        self.app.post(self.get_server_url() + '/accounts/login/',
                      data=dict(username=config.AWDEORIO_USER,
                                password=config.AWDEORIO_PASS))

        post_url = "{}/u/{}/".format(self.get_server_url(), user)
        data = {"create_post": "upload new post",
                'file': open(config.PIC_FILENAME, 'rb')}
        self.app.post(post_url, data=data)

    def scroll_to_bottom_of_page(self, ):
        """Scroll to bottom of the page by finding the tallest DOM element."""
        get_largest_height_script = r"""
            let elements = document.getElementsByTagName("*");
            let current_max = 0;
            for (let i = 0; i < elements.length; i++) {
                if (elements[i].scrollHeight > current_max) {
                    current_max = elements[i].scrollHeight;
                }
            }
            return current_max;
        """
        largest_height = self.driver.execute_script(get_largest_height_script)

        scroll_script = "window.scrollTo(0, {});".format(largest_height)
        self.driver.execute_script(scroll_script)

    def try_login(self):
        """Trys to log in."""
        # pylint: disable=redundant-unittest-assert
        try:
            util.log_in_user(self.driver, self.get_server_url())
        except selenium.common.exceptions.WebDriverException:
            self.assertTrue(False, ("Failed to login to insta485 with "
                                    "user {}").format(config.AWDEORIO_USER))
