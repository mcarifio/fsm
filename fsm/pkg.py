"""
Module `pkg` manipulates software packages (without specific grounding in their types, e.g. python packages).

cli usage: python -m pkg ${action} # use python -m pkg actions for a list of actions

python usage:
  import logging
  import pkg
  pkg.logger.setLevel(logging.DEBUG) # default is logging.INFO
"""

# Forward reference types so you can use class names in the class definitions themselves.
from __future__ import annotations

# Each module has it's own logger which will (eventually) get it's configuration from a root logger.
import logging

logger = logging.getLogger(__name__)  # logger.setLevel(logging.DEBUG)

__version__ = "0.1.0"
__author__ = "Mike Carifio <mike@carif.io>"

import io
import json
import sys
import pathlib
import subprocess
import re

import fire
import box
import pytest
import inspect
import typing as t
import enum  # for Package.Kind
from fsm import util
from fsm.checker import check

class Version:
    # TODO mike@carif.io deferred: the semantics of a package version really depend on the package type, e.g. `rpm`, `apt` and so forth.
    """
    Package.Version is a version specifier for a Package. It has a semantic version format without implying
    that major versions only change on breaking api changes. So it has semantic version syntax but not
    semantics.

    Status: this class is incomplete and currently unused; it's stubbed it out for future use. No unittests yet provided.
    """

    # regular expression refined from https://regex101.com/r/vkijKf/1/
    # It uses regular expression groups to capture parts of a string and lookahead capture to give those
    # parts names. The names match the properties of the Version class so that they can be sliced into
    # a Version constructor. Unfortunately, none of this can be checked until runtime via unittests.
    version_re = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(-((?P<prerelease>0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(\+(?P<build>([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)))?$"

    versionless = None

    def __init__(self, major=0, minor=0, patch=0, prerelease=None, build=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

    @staticmethod
    def make(major=0, minor=0, patch=0, prerelease=None, build=None):
        return Version(major, minor, patch, prerelease, build)

    def __str__(self):
        """
        Returns a version string in semantic version (like) format.
        :return: major.minor.patch[-prerelease[+build]]
        """
        suffix = "-" + self.prerelease if self.prerelease else ""
        suffix += "+" + self.build if self.build else ""
        return f"{self.major}.{self.minor}.{self.patch}{suffix}"

    @staticmethod
    def parse(version):
        if match := re.match(Version.version_re, version):
            return Version(**match.groupdict())

    def __eq__(self, other):
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prepublished == other.prepublished
            and self.build == other.build
        )

    def __hash__(self):
        return id(self)

    def __lt__(self, other):
        return self.major < other.major or self.minor < other.minor or self.patch < other.patch

    def __gt__(self, other):
        return self.major > other.major or self.minor > other.minor or self.patch > other.patch

    def __repr__(self):
        # Returns the class name and member contents
        return f"{self.__class__.__name__}(**{self.__dict__})"


# TODO mike@carif.io: assign Version.versionless inside the class definition itself? future annotations doesn't seem
# to be enough.
Version.versionless = Version(0, 0, 0)





# TODO mike@carif.io: Here's the perfect place for a set of "plugins", one per package kind.
# TODO mike@carif.io: Overly tricky here? Subclass Package by type instead?
class Package:
    """
    class Package represents a package. Packages are (currently) _manifest_ or _tagged_ with kind Package.Kind, one of
    several enums from class Kind. Each enum has an associated package type, for example Package.Kind.rpm will (eventually) map
    to class Package.rpm (yes, lowercase, not pythonic, but using the package's file extension to indicate it's Kind). A
    package is reference to some kind of bundle with enough metadata from that bundle to resolve installation. The reference
    is a url. The url can be None, which means that it's resolved just before installation so that mirrors and "internal only"
    repositories can be handled (this could be a mistake, we'll see).

    Package provides an __eq__ and __hash__ to participate in collections, specifically graphs.
    """

    # Default values for __init__(), these values are splatted in first.
    defaults = dict(
        warn=True,  # how conforms() announces problems with wellformedness, with warnings or raising AssertionnError
        version=Version.versionless,  # generate a "no version" marker
        url="",  # package's url
        dependencies=list(),
    )

    def __init__(self, **kwargs):
        """
        Represents a software package. The kwargs are usually taken from a dictionary (which can be taken from json).
        :param kwargs:
          * key `name` is required and is not defaulted
          * key `dependencies` is assigned [] if not present
          * key `version` is assigned Version.versionless if not present
          * key `url` is assigned None if not present. `url` can be later resolved.
        """
        # Splat the dictionary values into this instance with **kwargs overriding **defaults.
        # TODO mike@carif.io: although this little oneliner has some elegance, it necessitates
        #   some after construction testing with conforms() to catch problems early. This has
        #   some "code smell" and triggers my spidy sense.
        self.__dict__ = {**self.defaults, **kwargs}
        # Confirm self conforms to some "wellformedness" policy.
        self.conforms()

    @staticmethod
    def make(**kwargs):
        """
        make(**kwargs) supports a fluent style, for example: version = Package.make(warn=True, name='carif').version
        :param kwargs: see __init__()
        :return: a new Package instance
        """
        return Package(**kwargs)

    def conforms(self):
        """
        conforms() asserts certain things are true about self. Version
        :return:
        """
        check(len(self.name) > 0, "no name?", self.warn)  # every package has a name
        check(len(self.dependencies) >= 0, "no dependencies?", self.warn)
        check(self.version is not None, "no version?", warn=self.warn)
        check(self.url is not None, "no url?", warn=self.warn)
        return self



class Kind(enum.Enum): # (enum.EnumDict):
    """
    The type tag for a package. Each enumeration value maps to a class above. The bundle
    extension serves as the indicator for the kind, similar to a mime type.

    Status: this class is incomplete and little used. It will serve as a pattern for future work.
    """

    # TODO mike@carif.io: use mime type tags instead?
    generic = ""
    rpm = "rpm"
    rpm_src = "src.rpm"
    apt = "apt"
    apt_src = "dsc"  ## more complicated
    python_pip = "tar.gz"
    python_wheel = "whl"
    python_zip = "zip"
    crate = "crate"  ## a .tar.gz file underneath
    js = "js"  ## javascript "package" or "bundle"
    mjs = "mjs"  ## javascript ES module indicated explicitly via the file extension
    # ... add more kinds here

# For each enum value in Kind, define a class of the same name. For example Kind.rpm = "rpm"
# and there's a Package.rpm class. Currently incomplete and stubbed out for future extension.
# TODO mike@carif.io: would benefit from python's ABC (absract base class) pattern? This feels like
#   a solved problem who's pattern I just don't know about yet.
class generic(Package):
    """
    Package.generic represents a generic package. There's no install method.
    """

    @classmethod
    def extension(cls):
        return cls.__name__


class rpm(Package):
    """
    Package.rpm represents an rpm package.
    Status: this class is incomplete and currently unused but provides a stub for extension and thinking.
    """

    @classmethod
    def extension(cls):
        return cls.__name__

    @classmethod
    def install(cls, name):
        """
        Installs an rpm package using dnf.
        :param name: the name of the package, e.g. "emacs"
        :return: int using os status code conventions, e.g. 0 for success, != 0 for failure
        """
        result = subprocess.run("dnf install -y {name}".split(), check=True, capture_output=True)
        if result.returncode != 0:
            logger.error(result.stderr)
        return result.returncode


# TODO mike@carif.io: Move these helper functions into a util module.
type Content = pathlib.Path | io.StringIO


def jsonify1(contents: Content) -> json:
    """
    Return the json from the contents of a file named as a pathlib.Path or a io.StringIO.
    :param contents: the content to json.load()
    :return: json
    """

    # Bjarne Stroustrup hates selection by type because new types necessitate code changes.
    # TODO mike@carif.io: is this pattern suitably robust? I dunno.
    match ct := type(contents):
        case ct if issubclass(ct, io.StringIO):
            return json.loads(contents.read())
        case ct if issubclass(ct, pathlib.Path):
            with open(contents, "r") as f:
                return json.load(f)
        case _:
            raise TypeError(f"{type(contents)} is not of type Contents")


def jsonify(rest: list[Content]) -> t.List[json]:
    """
    Jsonify a list of Content
    :param rest: content to jsonify1
    :return: a list of json objects
    """
    return [jsonify1(c) for c in rest]


def packagify(rest: t.List[json]) -> t.List[Package]:
    """
    Packagify a list of json objects
    :param rest: a list of json objects
    :return: a list of Package objects
    """
    return [Package(**p) for p in rest]

@pytest.fixture(scope="module")
def testcases():
    """
    Create test cases for methods of class Tests
    :return: a box (dict) of keys:values, each key is a test case name and each value is the value.
    """
    return box.Box(key="a value")

class Tests:
    def test_always_passes(self, testcases):
        assert True

    def test_testcases(self, testcases):
        assert testcases.key == "a value"

    def test_missing_pathname(self, testcases):
        with pytest.raises(FileNotFoundError):
            jsonify([pathlib.Path("missing file")])

    def test_string2empty(self):
        with pytest.raises(json.JSONDecodeError):
            result = jsonify([io.StringIO("")])

    def test_justbrackets(self):
        result = jsonify([io.StringIO("{}")])
        assert result == [{}]

    def test_string2json(self):
        result = jsonify1(io.StringIO("{}"))
        assert result == {}
        result = jsonify([io.StringIO('{"x": 1}')])
        assert result == [{"x": 1}]

    def test_package_json(self):
        result = jsonify([io.StringIO('{"name": "emacs", "dependencies": [ "emacs-core", "emacs-other" ]}')])
        assert result == [{"name": "emacs", "dependencies": ["emacs-core", "emacs-other"]}]

    def test_json2package_nodependencies(self):
        # note **p is splatting in the dictionary into Package's constructor __init__. Hacky.
        result = packagify(jsonify([io.StringIO('{"name": "emacs"}')]))
        assert len(result) == 1
        first = result[0]
        assert first.name == "emacs"
        assert first.dependencies == []

    def test_json2package(self):
        # note **p is splatting in the dictionary into Package's constructor __init__. Hacky.
        result = packagify(jsonify([io.StringIO('{"name": "emacs", "dependencies": [ "emacs-core", "emacs-other" ]}')]))
        assert len(result) == 1
        first = result[0]
        assert first.name == "emacs"
        assert first.dependencies == ["emacs-core", "emacs-other"]

    # TODO mike@carif.io: need a lot more tests


# The possible actions that dispatcher dispatches to, e.g. `'version'` calls `on_version(list[str])`
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


def main():
    return fire.Fire()


if __name__ == "__main__":
    main()
