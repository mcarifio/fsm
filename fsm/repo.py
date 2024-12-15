#!/usr/bin/env python
"""
Module repo captures the set union of all packages (pkg.Package) available for installation.
"""

# Forward referencing of types, e.g. typehints in class Node below.
from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Mike Carifio <mike@carif.io>"

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
from . import resolver


class Repo:
    def __init__(self, packages: t.List[pkg.Package] = None) -> None:
        if packages:
            self.index = {p.name: p for p in packages}
        else:
            self.index = {}

    def __contains__(self, package: pkg.Package) -> bool:
        return self.index.get(package.name)

    @staticmethod
    def fetch(url: str):
        pass

    @staticmethod
    def make(packages: t.List[pkg.Package] = None) -> Repo:
        if packages:
            return Repo(packages)
        else:
            return Repo()


class Everything:
    """
    All packages from all repos available for installation.
    """

    pass


class TestCase(unittest.TestCase):
    def setUp(self):
        self.nothing = Repo()
        self.smallest = Repo()
        self.smallest_make = Repo.make()
        # emacs depends on emacs-lisp and emacs-core and emacs-gtk
        # emacs-lisp could be installed without emacs itself and depends on emacs-core
        self.emacs_core = pkg.Package(name="emacs-core")
        self.emacs_gtk = pkg.Package(name="emacs-gtk")
        self.emacs_lisp = pkg.Package(name="emacs-lisp", dependencies=[self.emacs_core])
        self.emacs = pkg.Package(
            name="emacs",
            dependencies=[self.emacs_lisp, self.emacs_core, self.emacs_gtk],
        )
        self.emacs_repo = Repo(packages=[self.emacs, self.emacs_lisp, self.emacs_core, self.emacs_gtk])
        self.instances = [
            self.nothing,
            self.smallest,
            self.emacs,
            self.emacs_core,
            self.emacs_gtk,
            self.emacs_lisp,
            self.emacs_repo,
        ]

    def test_always_passes(self):
        self.assertTrue(True)

    def test_repo_present(self):
        self.assertTrue(self.emacs in self.emacs_repo)

    def test_repo_absent(self):
        self.assertFalse(pkg.Package(name="not-there") in self.emacs_repo)

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


def on_install(rest: list[str]) -> t.List[json]:
    print(dispatcher.caller(), *rest)


def main():
    dispatcher.mkdispatch(globals())(sys.argv)


if __name__ == "__main__":
    main()
