#!/usr/bin/env python

import sys
from os import PathLike
import pprint

import toml


def section(pathname: str | PathLike, sectionpath: str):
    with open(pathname, "r") as f:
        s = toml.load(f)
    for part in sectionpath.split("."):
        s = s[part]
    return s.items()


def start(argv: list[str]) -> None:
    argvd: dict[int, str] = {i: v for i, v in enumerate(argv[1:])}
    pathname: str = argvd.get(0, "pyproject.toml")
    sectionpath: str = argvd.get(1, "tool.poetry.scripts")
    for name, command in section(pathname, sectionpath):
        print(name, end=" ")
        pprint.pprint(command)


def main():
    return start(sys.argv)


if __name__ == "__main__":
    main()
