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
from fsm import resolver


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

@pytest.fixture(scope="module")
def testcases():
    """
    Create test cases for methods of class Tests
    :return: a box (dict) of keys:values, each key is a test case name and each value is the value.
    """
    result = box.Box(key="a value", nothing=Repo(), smallest=Repo(), smallest_make=Repo.make(),
                   emacs_core=pkg.Package(name="emacs-core"), emacs_gtk=pkg.Package(name="emacs-gtk"),
                   emacs_lisp=pkg.Package(name="emacs-lisp", dependencies=[pkg.Package(name="emacs-core")]),
                   emacs=pkg.Package(name="emacs", dependencies=[pkg.Package(name="emacs-lisp"),]))
    result.emacs_repo = Repo(packages=[result.emacs, result.emacs_lisp, result.emacs_core, result.emacs_gtk])
    return result

class Tests:

    def test_always_passes(self, testcases):
        assert True

    def test_testcases(self, testcases):
        assert testcases.key == "a value"

    def test_repo_present(self, testcases):
        assert (testcases.emacs in testcases.emacs_repo)

    def test_repo_absent(self, testcases):
        assert not (pkg.Package(name="not-there") in testcases.emacs_repo)

    # TODO mike@carif.io: need a lot more tests


def version(*rest: tuple[str]):
    """
    Report the version of this module a.k.a. `__version__` (if it's supplied)
    :param *rest: ignored
    :return: None
    """
    return globals().get("__version__", "unknown")


def about(*rest: tuple[str]):
    """
    Describe this module in some way, tbs.
    :param *rest:
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
