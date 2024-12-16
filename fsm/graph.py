"""
Module `graph` does just enough discrete math to represent a graph of pkgs. It will be replaced by
networkX. Some of the packages are installed.
Some are candidates for installation. The graph can be cyclic. A node may have incoming edges from different nodes. Two different
nodes can indirectly have outgoing edges from different nodes. The cycles can cause infinite loops when traversing the graph, therefore
we must ensure we stop traversing when encountering seen nodes.

Nodes consist of contents (a single thing), a set of outgoing edges and a set of incoming edges
(mostly to reverse all the incoming edges from elsewhere). We assume (and don't check) that the graph is _wellformed_,
meaning that if `node0` -> `node1` then `node0.outgoing` contains `node1` and `node1.incoming` contains `node0`.
Incoming and outgoing edges for each node are assumed "to be right".

See module resolver and class resolver.Resolver for a consumer of a graph.Graph() instance.

cli usage: `python -m graph ${action} # use python -m pkg actions for a list of actions, the default action is 'test'`

python usage:
  import logging
  import graph; graph.logger.setLevel(logging.DEBUG) # default is logging.INFO
"""

# TODO mike@carif.io: redo later using python package networkx

# Forward referencing of types, e.g. typehints in class Node below.
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)  # logger.setLevel(logging.DEBUG)

__version__ = "0.1.0"
__author__ = "Mike Carifio <mike@carif.io>"

import io
import json
import random
import sys
import os

# import unittest
import pytest
import box
import typing as t
import fire
from fsm import util


class RecursionLimit:
    """
    RecursionLimit implements a context manager for recursive function calls.
    It ups the value if it's greater than the current threshold and returns
    to the previous setting on __exit__.
    """

    def __init__(self, limit: int = -1):
        self.limit = limit
        self.revert = None

    def __enter__(self):
        if sys.getrecursionlimit() < self.limit:
            self.revert = sys.getrecursionlimit()
            sys.setrecursionlimit(self.limit)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self.revert:
            sys.setrecursionlimit(self.revert)
        # if exc_type: print(f"An error occurred: {exc_value}")
        return False  # Suppresses exceptions if True


class Node:
    """
    class Node consists of `contents`, incoming edges and outgoing edges.
    """

    def __init__(self, contents=None, incoming: set[Node] = None, outgoing: set[Node] = None) -> None:
        # TODO mike@carif.io: you can make a Node without contents. Is that wise?
        self._contents = contents
        self._incoming = incoming or set()
        self._outgoing = outgoing or set()

    @staticmethod
    def make(contents=None, incoming: set[Node] = None, outgoing: set[Node] = None) -> Node:
        """
        @staticmethod make() allows for a fluent style, e.g. len(n := Node.make(contents="contents").incoming(other.incoming).outgoing(other.outgoing))
        (if you like that sort of thing).
        :param contents:
        :param incoming:
        :param outgoing:
        :return:
        """
        return Node(contents, incoming, outgoing)

    # contents
    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, value: t.Any) -> None:
        self._contents = value

    # incoming
    # TODO mike@carif.io: might not need incoming for resolver.Resolver.resolve()
    @property
    # usages:
    # add an incoming node: g = graph.Node(dict(id=0, value=0)); g.incoming.add(dict(id=1, value=1)); g.incoming.update(dict(id=2, value=2), dict(id=3, value=3))
    def incoming(self) -> set[Node]:
        return self._incoming

    # from
    @property
    def outgoing(self) -> set[Node]:
        return self._outgoing

    # recursively generate a representation of the graph.
    # see preorder() and postorder()
    def __repr__(self):
        """
        Traverse the graph preorder on *outgoing* edges, generating a representation of the contents and then incoming and outgoing edges recursively.
        Since the signiture of `__repr__()` is fixed, create a helper function `_repr()` that tracks seen nodes as well as calling `_repr()`
        recursively on incoming and outgoing edges. This is a little different from `Node.preorder()` and `Node.postorder()` which
        look at the contents for equality (via `in` with needs `__eq__()` and `__hash()` implemented for `contents`.
        :return: str
        """

        def _repr(s, seen):
            # If I haven't seen Node s
            if not s in seen:
                # ... then I've seen it now.
                seen.append(s)
                # Any outgoing edges?
                if s.outgoing:
                    # Recurse on them
                    return f"{self.__class__.__name__}(contents={repr(s.contents)}, incoming={[repr(n.contents) for n in s.incoming]}, outgoing={[_repr(n,seen) for n in s.outgoing]})"
                else:
                    # otherwise repr() the node's contents
                    return f"{self.__class__.__name__}(contents={repr(s.contents)}, incoming={[repr(n.contents) for n in s.incoming]})"

        return _repr(self, list())

    #
    def same(self, other):
        """
        Two nodes are the same if their contents are the same, edges don't matter.
        This method is meant to be overloaded by subclasses.
        :param other:
        :return:
        """
        return self.contents == other.contents

    def preorder(self, visitor=id, limit: int = -1):
        """
        preorder(visitor) will apply the function visitor(c: type(n.contents))->typing.Any for each unseen node in a graph of nodes in "outgoing" order under the
        assumption that outgoing edges will not miss any nodes. Since python is *not* tail recursive there is a maximum number of stack frames `sys.getrecursionlimit()`
        which the traversal can do. This value can be upped with limit=size.

        :param visitor: t.Function(type(n.contents))->t.Any, in order words it applies vistor to each Node's contents
        :param limit: resets the recursion limit for this call only iff limit > sys.getrecursionlimit(), usually 1000
        :return: list of application results in traversal order.
        """

        def _preorder(s, visitor, seen, results):
            if not s.contents in seen:
                seen.append(s.contents)
                # apply visitor first
                results.append(visitor(s.contents))
                for o in s.outgoing:
                    _preorder(o, visitor, seen, results)
                return results

        # TODO mike@carif.io: wrap with a try
        with RecursionLimit(limit=limit) as rl:
            return _preorder(self, visitor, list(), list())

    def postorder(self, visitor=id, limit: int = -1, seen: list[Node] = None):
        """
        postorder(visitor) will apply the function visitor(c: type(c.contents))->typing.Any for each unseen node in a graph of nodes in reverse "outgoing" order under the
        assumption that outgoing edges will not miss any nodes.
        :param visitor:
        :return: list of application results in traversal order.
        """

        def _postorder(s, visitor, seen, results):
            if not s.contents in seen:
                seen.append(s.contents)
                for o in s.outgoing:
                    _postorder(o, visitor, seen, results)
                # apply visitor last
                results.append(visitor(s.contents))
            return results

        # TODO mike@carif.io: wrap with a try
        with RecursionLimit(limit=limit) as rl:
            result = _postorder(self, visitor, seen or list(), list())
            return result

    def postorder_yield(self, visitor=id, limit: int = -1, seen: list[Node] = None):
        """
        postorder_yield(visitor) will apply the function visitor(c: type(c.contents))->typing.Any for each unseen node in a graph of nodes in reverse "outgoing" order under the
        assumption that outgoing edges will not miss any nodes.
        :param visitor:
        :return: list of application results in traversal order.
        """

        def _postorder(s, visitor, seen):
            if not s.contents in seen:
                seen.append(s.contents)
                # yield (_postorder(o, visitor, see) for o in s.outgoing())
                for o in s.outgoing:
                    _postorder(o, visitor, seen)
                # apply visitor last
                return visitor(s.contents)

        # TODO mike@carif.io: wrap with a try?
        with RecursionLimit(limit=limit) as rl:
            yield _postorder(self, visitor, seen or list())

    def __len__(self):
        """
        Returns the count of unique Nodes n in the graph.
        :return: int
        """
        # TODO mike@carif.io: mostly used for testing. Do (discrete math) graphs have a length?
        return len(self.preorder(id))


@pytest.fixture(scope="module")
def testcases():
    """
    Create test cases for methods of class Tests
    :return: a box (dict) of keys:values, each key is a test case name and each value is the value.
    """
    return box.Box(key="a value", nothing=Node(), smallest=Node(), smallest_make=Node.make())


class Tests:
    class Content:
        def __init__(self, _id: str | int, value: str | int = random.random()):
            self._id = _id
            self._value = value

        @property
        def id(self):
            return self._id

        @property
        def value(self):
            return self._value

        # TODO mike@carif.io: brittle. Graph probably fails without a contents specific __eq__()
        def __eq__(self, other):
            return self.id == other.id and self.value == other.value

        def __hash__(self):
            return self.id

        def __repr__(self):
            return f"${self.__class__.__name__}(id={self.id}, value={self.value})"

        # self.top_child1: Node = Node(
        #     contents=dict(id="top", value=0),
        #     outgoing=set([Node(dict(id="child0", value=1))]),
        # )
        # self.top_child2: Node = Node(
        #     contents=dict(id="top", value=0),
        #     outgoing=set([Node(dict(id="child0", value=1)), Node(dict(id="child1", value=1))]),
        # )
        # self.bottom: Node = Node(contents=dict(id="bottom", value=-1))
        # self.diamond: Node = Node(
        #     contents=dict(id="top", value=0),
        #     outgoing=set(
        #         [
        #             Node(dict(id="left", value=1), outgoing=set([self.bottom])),
        #             Node(dict(id="right", value=2), outgoing=set([self.bottom])),
        #         ]
        #     ),
        # )
        #
        # self.cbottom = Node(contents=self.Content("cbottom", "bottom"))
        # self.cleft = Node(contents=self.Content("cleft", "left"), outgoing=set([self.cbottom]))
        # self.cright = Node(contents=self.Content("cright", "right"), outgoing=set([self.cbottom]))
        # self.ctop = Node(
        #     contents=self.Content("ctop", "top"),
        #     outgoing=set([self.cleft, self.cright]),
        # )
        #
        # self.instances = [
        #     self.smallest,
        #     self.smallest_make,
        #     self.top_child1,
        #     self.top_child2,
        #     self.bottom,
        #     self.diamond,
        #     self.cbottom,
        #     self.cleft,
        #     self.cright,
        #     self.ctop,
        # ]

    def test_always_passes(self, testcases):
        assert True;

    def test_testcases(self, testcases):
        assert testcases.key == "a value"

    def test_smallest_node(self, testcases):
        smallest = testcases.smallest
        assert not smallest.contents
        assert len(smallest) == 1

    # def test_make_smallest_node(self):
    #     n = Node.make()
    #     self.assertFalse(n.contents)
    #     self.assertEqual(len(n), 1)
    #
    # def test_node_no_links(self):
    #     value0 = dict(id=0, value=0)
    #     n = Node(value0)
    #     self.assertEqual(n.contents, value0)
    #     self.assertEqual(n.incoming, set())
    #     self.assertEqual(n.outgoing, set())
    #     self.assertEqual(len(n), 1)
    #
    # def test_make_node_no_links(self):
    #     value0 = dict(id=0, value=0)
    #     n = Node.make(value0)
    #     self.assertEqual(n.contents, value0)
    #     self.assertEqual(n.incoming, set())
    #     self.assertEqual(n.outgoing, set())
    #     self.assertEqual(len(n), 1)
    #
    # def test_node_1_outgoing(self):
    #     value0 = dict(id=0, value=0)
    #     top = Node(value0)
    #     self.assertEqual(top.contents, value0)
    #     self.assertEqual(top.incoming, set())
    #     self.assertEqual(top.outgoing, set())
    #     self.assertEqual(len(top), 1)
    #
    #     value1 = dict(id=1, value=1)
    #     child = Node(value1)
    #     self.assertEqual(top.contents, value0)
    #     self.assertEqual(top.incoming, set())
    #     self.assertEqual(top.outgoing, set())
    #     self.assertEqual(len(top), 1)
    #
    #     top.outgoing.add(child)
    #     self.assertEqual(top.contents, value0)
    #     self.assertEqual(top.incoming, set())
    #     self.assertEqual(top.outgoing, set([child]))
    #     self.assertEqual(len(top), 2)
    #
    #     self.assertSetEqual(top.outgoing, set([child]))
    #     self.assertSetEqual(top.incoming, set())
    #
    # def test_repr(self):
    #     # print(f'test_repr: {self.nothing}')
    #     # print(f'test_repr: {self.smallest}')
    #     # print(f'test_repr: {self.smallest_make}')
    #     # print(f'test_repr: {self.top_child1}')
    #     # print(f'test_repr: {self.top_child2}')
    #     print("test_repr: ", self.instances)
    #     self.assertTrue(True)
    #
    # def test_preorder(self):
    #     for i, n in enumerate(self.instances):
    #         results = n.preorder(repr)
    #         print(f"test_preorder results for {i}: {results}")
    #     self.assertTrue(True)
    #
    # def test_postorder(self):
    #     for i, n in enumerate(self.instances):
    #         results = n.postorder(repr)
    #         print(f"test_postorder results for {i}: {results}", file=sys.stderr)
    #     self.assertTrue(True)
    #
    # def test_postorder_yield(self):
    #     for i, n in enumerate(self.instances):
    #         result = list(n.postorder_yield(repr))
    #         print(f"test_postorder_yield results for {i}: {result}", file=sys.stderr)
    #     self.assertTrue(True)
    #
    # def test_postorder_yield_iter(self):
    #     for i, n in enumerate(self.instances):
    #         for visit in n.postorder_yield(repr):
    #             print(f"test_postorder_yield_iter for {n}: {visit}", file=sys.stderr)
    #     self.assertTrue(True)


# cli actions


def version(*rest: list[str]):
    print(globals()["__version__"] or "unknown")


def about(*rest: list[str]):
    print(__doc__)


def pt(*rest: list[str]):
    exit(pytest.main(["--verbose", *sys.argv[2:], __file__]))


def main():
    fire.Fire()


if __name__ == "__main__":
    main()
