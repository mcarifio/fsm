#!/usr/bin/env python
"""
Module resolver.Resolver.resolve() resolves questions about graphs (graph.Node) of packages (pkg.Package) available in repositories (repo.Repository).
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
from fsm import graph
from fsm import repo


class Resolver:
    check_versions = False

    def __init__(self, check_versions=False) -> None:
        self.check_versions = check_versions

    @staticmethod
    def resolve(root: graph.Node) -> t.List[pkg.Package]:
        def identity(c):
            return c

        result: t.List[pkg.Package] = root.postorder(visitor=identity)
        # post process the result here, looking for problems
        return result

    @staticmethod
    def available(root: graph.Node, r: repo.Repo) -> t.List[pkg.Package]:
        all(p in r for p in Resolver.resolve(root))

class Tests:

    def test_always_passes(self, testcases):
        assert True

    def test_a_value(self, testcases):
        assert testcases.key == "a value"

    def test_emacs(self, testcases):
        traversal = Resolver.resolve(self.emacs_graph)
        assert len(traversal) == 4
        print(*[p.name for p in traversal], file=sys.stderr)  ## italian debugging
        assert traversal == [testcases.emacs_gtk, testcases.emacs_core, testcases.emacs_lisp, testcases.emacs]

    # TODO mike@carif.io: need a lot more tests


def version(*rest: tuple[str]):
    """
    Report the version of this module a.k.a. `__version__` (if it's supplied)
    :param rest: ignored
    :return: str
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
