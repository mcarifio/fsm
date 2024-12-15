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

__version__ = "0.1.0"
__author__ = "Mike Carifio <mike@carif.io>"

import copy
import io
import json
import logging

logger = logging.getLogger(__name__)  # logger.setLevel(logging.DEBUG)

import sys
import os

import unittest
import typing as t
from . import dispatcher
from . import pkg


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


class TestCase(unittest.TestCase):
    def setUp(self):
        self.o = 1
        self.nothing = Transaction(self.o)
        self.instances = [self.nothing]

    def test_always_passes(self):
        self.assertTrue(True)

    def test_bad_transaction(self):
        with self.assertRaises(ValueError):
            return Transaction(None)

    # TODO mike@carif.io: need a lot more tests


def on_version(rest: list[str]):
    """
    Report the version of this module a.k.a. `__version__` (if it's supplied)
    :param rest: ignored
    :return: None
    """
    print(globals().get("__version__", "tbs"))


def on_about(rest: list[str]):
    """
    Describe this module in some way, tbs.
    :param rest:
    :return:
    """
    print(*rest)


def on_runner(rest: list[str]):
    """
    A more manual and explicit `on_test()` stubbed out for later refinement.
    :param rest: ignored
    :return: bool, True means the suite succeeded, False otherwise.
    """
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestCase))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


def on_test(rest: list[str]):
    """
    Run all classes derived from unittest.TestCase in this module. Keeps implementation and testcases together in
    a single file.
    :param rest: additional arguments to unittest.main()
    :return:
    """
    unittest.main(module=sys.modules[__name__], verbosity=2, argv=["test"], *rest)


def on_install(rest: list[str]) -> t.List[pkg.Package]:
    print(dispatcher.caller(), *rest)


def main():
    dispatcher.mkdispatch(globals())((sys.argv[1:] or ["test"]))


if __name__ == "__main__":
    main()
