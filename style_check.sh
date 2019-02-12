#!/bin/bash
pycodestyle setup.py insta485
pylint --reports=n setup.py insta485
pydocstyle setup.py insta485
