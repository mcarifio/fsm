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
import box
from fsm import util
from fsm import pkg
from fsm import graph
from fsm import pkgrepo
from fsm import resolver


@pytest.fixture(scope="module")
def testcases():
    """
    Create test cases for methods of class Tests
    :return: a box (dict) of keys:values, each key is a test case name and each value is the value.
    """
    return box.Box(key="a value")


class Tests:
    """
    Class Tests organizes all pytest unit tests for this module. A named class
    lets us move the tests around as a unit.

    You can run the tests with: `python -m fsm.cli pt` or `pytest fsm/cli.py`
    """
    def test_always_passes(self, testcases):
        assert True

    def test_testcases(self, testcases):
        assert testcases.key == "a value"





def version(*rest: tuple[str])->str:
    """
    Report the version of this module a.k.a. `__version__` (if it's supplied)
    :param rest: ignored
    :return: None
    """
    return globals().get("__version__", "unknown")



def about(*rest: tuple[str]):
    """
    Describe this module using the module docstring.
    :param *rest: ignored
    :return:
    """
    print(__doc__)

def pt(*rest: tuple[str])->int:
    """
    Run all pytests in class Tests in this module. Keeps implementation and testcases together in a single file.
    :param *rest: additional arguments to pytest.main(), not actually used yet
    :return: 0 if all tests pass, >0 otherwise (whatever pytest.main() returns)
    """
    return pytest.main([ "--verbose", *sys.argv[2:], __file__ ])

def install(*rest: tuple[str]):
    """
    install a set of packages described by rest in a transactional fashion
    """
    print(f"{util.caller()} tbs", rest, file=sys.stderr)

def remove(*rest: tuple[str]):
    """
    remote a set of packages described by rest in a transactional fashion
    """
    print(f"{util.caller()} tbs", rest, file=sys.stderr)

def fetch(*rest: tuple[str]):
    """
    fetch a set of packages described by rest in a transactional fashion
    """
    print(f"{util.caller()} tbs", rest, file=sys.stderr)

def find(*rest: tuple[str]):
    """
    find a set of packages described by rest in a transactional fashion
    """
    print(f"{util.caller()} tbs", rest, file=sys.stderr)




def main():
    """
    The main entry point for the command line interface, run directly via setuptools.
    :return:
    """
    # fire dispatches by verb == function name, e.g. 'pt' => pt()
    return fire.Fire()

# from the command line:
#  directly: chmod a+x fsm/cli.py; PYTHONPATH=. ./fsm/cli.py version
#  indirectly as a module: python -m fsm.cli version or optionally PYTHONPATH=. python -m fsm.cli version
#  indirectly as a script: PYTHONPATH=.
if __name__ == "__main__":
    main()

