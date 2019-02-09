"""Rest API Tests inherit from this class."""

import config
from test_base_live import TestBaseLive


class TestBaseRestAPI(TestBaseLive):
    """Base Class for Rest API Tests."""

    def setUp(self):
        """Setup."""
        super(TestBaseRestAPI, self).setUp()
        self.app_context.push()
        self.login(config.AWDEORIO_USER, config.AWDEORIO_PASS)

    def tearDown(self):
        """Call superTear Down, and logout."""
        self.app_context.pop()
        super(TestBaseRestAPI, self).tearDown()
        self.logout()

    def login(self, username, password):
        """Login Flask."""
        return self.app.post(self.get_server_url() +
                             '/accounts/login/', data=dict(
                                 username=username,
                                 password=password))

    def logout(self):
        """Logout Flask."""
        return self.app.get(self.get_server_url() + '/accounts/logout/')
