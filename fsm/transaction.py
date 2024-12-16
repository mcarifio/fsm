#!/usr/bin/env python
"""
Module transaction creates a generalized transaction manager Transaction that can be used like:
```bash
import transaction as t
# o
with t.Transaction(o) as tm:
    o.do()
    raise Exception("rollback needed")
```
"""

# Forward referencing of types, e.g. typehints in class Node below.
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)  # logger.setLevel(logging.DEBUG)

__version__ = "0.1.0"
__author__ = "Mike Carifio <mike@carif.io>"

import copy
import io
import json
import sys
import os

import fire
import box
import pytest
import typing as t
from fsm import util
from fsm import pkg


class Transaction:
    def __init__(self, o: t.Any) -> None:
        if o:
            self.o = o
        else:
            raise ValueError("Cannot wrap None")

    def __enter__(self):
        # don't make a copy until you enter
        self.before = copy.copy(self.o)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type:
            self.o.rollback()
            self.o = copy.copy(self.before)
        return False

@pytest.fixture(scope="module")
def testcases():
    """
    Create test cases for methods of class Tests
    :return: a box (dict) of keys:values, each key is a test case name and each value is the value.
    """
    result = box.Box(key="a value", action=lambda o: print(o))
    result.around_action = Transaction(result.action)
    return result


class Tests:

    def test_always_passes(self, testcases):
        assert True

    def test_bad_transaction(self, testcases):
        with pytest.raises(ValueError):
            return Transaction(None)

    # TODO mike@carif.io: need a lot more tests


def version(*rest: tuple[str]):
    """
    Report the version of this module a.k.a. `__version__` (if it's supplied)
    :param rest: ignored
    :return: None
    """
    return globals().get("__version__", "unknown")


def about(*rest: tuple[str]):
    """
    Describe this module in some way, tbs.
    :param rest:
    :return:
    """
    print(__doc__)

def pt(*rest: tuple[str]):
    """
    Run all pytests in class Tests in this module. Keeps implementation and testcases together in a single file.
    :param *rest: additional arguments to pytest.main(), not actually used yet
    :return: 0 if all tests pass, >0 otherwise (whatever pytest.main() returns)
    """
    return pytest.main([ "--verbose", *sys.argv[2:], __file__ ])


def install(rest: tuple[str]) -> t.List[json]:
    """
    fetch a set of packages described by rest in a transactional fashion
    """
    print(f"{util.caller()} tbs", rest, file=sys.stderr)


def main():
    return fire.Fire()

if __name__ == "__main__":
    main()
