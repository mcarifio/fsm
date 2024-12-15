#!/usr/bin/env python
"""
Module resolver.Resolver.resolve() resolves questions about graphs (graph.Node) of packages (pkg.Package) available in repositories (repo.Repository).
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
from . import graph
from . import repo


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


class TestCase(unittest.TestCase):

    def setUp(self):
        self.nothing: graph.Node = graph.Node()
        self.smallest: graph.Node = graph.Node()
        self.smallest_make: graph.Node = graph.Node.make()

        # emacs depends on emacs-lisp and emacs-core and emacs-gtk
        # emacs-lisp could be installed without emacs itself and depends on emacs-core
        self.emacs_core = pkg.Package(name="emacs-core")
        self.emacs_gtk = pkg.Package(name="emacs-gtk")
        self.emacs_lisp = pkg.Package(name="emacs-lisp", dependencies=[self.emacs_core])
        self.emacs = pkg.Package(
            name="emacs",
            dependencies=[self.emacs_lisp, self.emacs_core, self.emacs_gtk],
        )
        self.emacs_gtk_graph = graph.Node(contents=self.emacs_gtk)  # windows ui
        self.emacs_core_graph = graph.Node(contents=self.emacs_core)  # no window ui
        self.emacs_lisp_graph = graph.Node(contents=self.emacs_lisp, outgoing=set([self.emacs_core_graph]))
        self.emacs_graph: graph.Node = graph.Node(
            contents=self.emacs,
            outgoing=set([self.emacs_lisp_graph, self.emacs_core_graph, self.emacs_gtk_graph]),
        )
        self.instances = [
            self.nothing,
            self.smallest,
            self.emacs,
            self.emacs_core,
            self.emacs_lisp,
            self.emacs_gtk,
        ]

    def test_always_passes(self):
        self.assertTrue(True)

    def test_emacs(self):
        traversal = Resolver.resolve(self.emacs_graph)
        self.assertEqual(len(traversal), 4)
        print(*[p.name for p in traversal], file=sys.stderr)  ## italian debugging
        self.assertListEqual(traversal, [self.emacs_gtk, self.emacs_core, self.emacs_lisp, self.emacs])

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
