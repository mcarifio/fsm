#!/usr/bin/env python
"""
Module repo captures the set union of all packages (pkg.Package) available for installation.
"""

# Forward referencing of types, e.g. typehints in class Node below.
from __future__ import annotations
import logging

logger = logging.getLogger(__name__)  # logger.setLevel(logging.DEBUG)

__version__ = "0.1.0"
__author__ = "Mike Carifio <mike@carif.io>"


import json
import sys
import unittest
import typing as t
from . import dispatcher
from . import pkg
from . import graph
from . import repo
from . import resolver

class TestCase(unittest.TestCase):
    def test_always_passes(self):
        self.assertTrue(True)


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


def on_main(rest: list[str]) -> t.List[json]:
    """
    The main entry point
    """
    print(dispatcher.caller(), *rest)


def on_install(rest: list[str]):
    """
    install a set of packages described by rest in a transactional fashion
    """

    print("tbs", dispatcher.caller(), *rest, file=sys.stderr)


def main():
    dispatcher.mkdispatch(globals())(sys.argv)


if __name__ == "__main__":
    main()
