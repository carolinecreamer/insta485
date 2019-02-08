"""
Student solution wrapper to add request logging to file.

A thin wrapper around the student solution Flask app to add request logging
to a file.
"""
import logging
import time

import flask
from flask import request

from insta485 import app
import config


def get_logger():
    """Create and return a logger object."""
    handler = logging.FileHandler(config.TEST_LOG, mode='w')
    logger = logging.getLogger(config.TEST_LOG)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


@app.after_request
def log_request(response):
    """
    Log the request to the LOGGER.

    A trigger function which is called after each flask request to log
    the request to LOGGER.
    """
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.commit()
    timestamp = time.strftime('[%d/%b/%Y %H:%M:%S]')
    LOGGER.info('%s - - %s "%s %s %s" %s -', request.remote_addr, timestamp,
                request.method, request.full_path, request.scheme,
                response.status)
    return response


LOGGER = get_logger()


def reset_log():
    """Clear the log by reseting the logger."""
    # pylint: disable=global-statement
    global LOGGER
    LOGGER = get_logger()
