"""
Logging solution wrapper to make api requests slow.

A thin wrapper around the student solution Flask app to add request logging
and slow down API calls.
"""
import time

from flask import request

from insta485_logging import app
import config


@app.before_request
def slow_apis():
    """Slow down the API requests to student solution."""
    if "/api/v1/" in request.path:
        time.sleep(config.API_WAIT)
