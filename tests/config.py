"""Configuration for the autograder."""
import os
import sys


# SELENIUM OPTIONS ##################################
RUN_HEADLESS = True
if sys.platform == 'darwin':
    # Automatically finds binary on OSX
    CHROME_BIN = None
else:
    CHROME_BIN = '/usr/bin/google-chrome-stable'


# TESTING OPTIONS ###################################
TEST_PORT = 8000
# place log file in autograder directory
TEST_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "app-requests.log")
# time (seconds) to wait during slow api requests before returning response
API_WAIT = 0.5
# time (seconds) to wait for api requests to appear in the request log
API_REQUEST_WAIT = 60
# time (seconds) to wait between checks for api requests to appear in the
# request log
API_REQUEST_CHECK_INTERVAL = 0.5
IMPLICIT_WAIT_TIME = 30
SLOW_IMPLICIT_WAIT_TIME = 60

# USER CONSTANTS ####################################
AWDEORIO_USER = 'awdeorio'
AWDEORIO_PASS = 'password'
PIC_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "73ab33bd357c3fd42292487b825880958c595655.jpg")
