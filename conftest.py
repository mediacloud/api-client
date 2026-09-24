"""
define global --fast option; needs to be in top-level conftest.py
"""

import pytest

# environment variable definitions, private to test directory.
from mediacloud.test.opts import Opts

def pytest_addoption(parser, *args):
    parser.addoption("--fast", action="store_true",
                     default=Opts.is_set(Opts.MC_API_TEST_FAST),
                     help="Run tests faster (using admin token)")

def pytest_configure(config):
    """
    called after command line options parsed to copy result back out
    to environment for global access using Opts.is_set(Opts.XXX)
    """
    Opts.set_bool(Opts.MC_API_TEST_FAST, config.getoption("--fast"))
