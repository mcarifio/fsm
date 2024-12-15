#!/usr/bin/env python
"""
Module fsm.cli provides the command line interface for the fsm package.
"""

# Forward referencing of types, e.g. typehints in class Node below.
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)  # logger.setLevel(logging.DEBUG)

__version__ = "0.1.0"
__author__ = "Mike Carifio <mike@carif.io>"

import json
import sys
# import unittest
import pytest
import typing as t
import fire
# from . import dispatcher
from . import pkg
from . import graph
from . import repo
from . import resolver

class Tests:
    """
    Class Tests organizes all pytest unit tests for this module. A named class
    lets us move the tests around as a unit.

    You can run the tests with: `python -m fsm.cli pt` or `pytest fsm/cli.py`
    """
    def test_always_passes(self):
        assert True


def version(*rest: list[str]):
    """
    Report the version of this module a.k.a. `__version__` (if it's supplied)
    :param rest: ignored
    :return: None
    """
    print(globals().get("__version__", "tbs"))


def about(*rest: list[str]):
    """
    Describe this module in some way, tbs.
    :param rest:
    :return:
    """
    print(__doc__)

def pt(*rest: list[str])->int:
    """
    Run all tests in class Tests in this module. Keeps implementation and testcases together in
    a single file.
    :param rest: additional arguments to pytest.main(), not actually used yet
    :return: 0 if all tests pass, >0 otherwise
    """
    exit(pytest.main([ "--verbose", *sys.argv[2:], __file__ ]))


def install(*rest: list[str]):
    """
    install a set of packages described by rest in a transactional fashion
    """
    print("install tbs", rest, file=sys.stderr)


def main():
    # fire dispatches by verb == function name, e.g. 'pt' => pt()
    fire.Fire()

# dispatched via setuptools
if __name__ == "__main__":
    main()
