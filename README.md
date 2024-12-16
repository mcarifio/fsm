# fsm, the Federated Software Manager

## Summary

The Federated Software Manager (fsm, lowercase because I think I'm e.e. cummings), is a linux command line tool to install/remove software
that abstracts away the particular formats (rpm, apt, pip, npm, flatpak, snap, asdf and whatever other ones are needed).

It's also a learning vehicle for me to try some design, programming and dev techniques. I'm a old dog learning the new tricks; that can
be a little ruff.

The rest of this README is divided into two parts: 1) the fsm tool motivation and design and 2) the mechanics of hacking it.
The first is what the tool does for _you_ (the why and the how(s)) and the second is what you can do (and improve) for the tool,
including how and where to extend it and how to confirm (i.e. test) that your additions work _without_ breaking the rest.
Pretty standard software engineering stuff.

## fsm Motivation and Design

### Why? (Motivation)

### What


## Hacking Mechanics

### Project Layout

```bash
tbs
```

### Walkthrough


```bash
python -m pip install -U pip
python -m pip install -U setuptools wheel pipx
python -m pipx install poetry
type -P poetry # ~/.local/bin/poetry
poetry --version # 1.8.5 or later
```

Next, establish your development environment:

```bash
export repo=https://github.com/mcarifio/fsm
export name=$(basename ${repo})
git clone ${repo} ~/src/${name} && cd ~/src/${name}
poetry install
poetry run sanitycheck  ## run a sanity check to make sure your dev environment works
```

### Lore

Note this is similar to activating the poetry venv manually with these commands:
```bash
source $(poetry env info --path)/bin/activate # for bash
python -m pip list | grep homework
python -m pkg version
```
`poetry run` just activates and deactivates the venv on your behalf.

```bash
python -c 'import sys; assert sys.version_info.major >= 3; assert system.version_info.minor >= 10'
python -m pip install --user -U pylint pytest
```
Installing these packages (more) globally makes them more convenient and takes poetry and package installing out of the picture. It's one
less moving part, especially initially as you find your "poetry legs".

If you embrace the danger, you can run all the unittests directly with `pytest` or `unittest`:
```bash
pytest fpm/*.py ## colorized output
python -m unittest --verbose *.py ## utilitarian
```


### Workflows and Diagrams

Every fsm module has a TestCase with test methods that exercise that module. The test suite can be invoked with
`python -m ${module} test`. Or you can run all of them with `pytest` or `python -m unittest --verbose *.py`:

```bash
mcarifio@butkis:~/src/geico/homework$ pytest *.py
================================================================= test session starts ==================================================================
platform linux -- Python 3.13.0, pytest-8.3.3, pluggy-1.5.0
rootdir: /home/mcarifio/src/geico/homework
configfile: pyproject.toml
plugins: hypothesis-6.115.6, anyio-4.6.2.post1
collected 23 items

client.py .                                                                                                                                      [  4%]
graph.py .........                                                                                                                               [ 43%]
pkg.py ........                                                                                                                                  [ 78%]
pkgrepo.py ...                                                                                                                                      [ 91%]
resolver.py ..                                                                                                                                   [100%]

================================================================== 23 passed in 0.43s ==================================================================
```

There aren't nearly enough tests and there are no mock objects to test objects with "mockable" endpoints such as `repo.Repo`.

## Global TODO

## History and References

No idea is an island (except perhaps for Einstein's 1905 paper of the special theory of relativity). This one isn't either and, in fact,
it seems like every programming language has it's own package manager. Except perhaps for javascript/typescript, which loads software directly and
immediately before use. Well, not node of course, which motivated deno in part. We've come a long way from the days when a program had a
shell script to install it -- oh the luxury! -- which sometimes actually ran to completion without error. Maybe even worked!

fsm started life as a take-home programming assignment for a job. I used it to review various python programming approaches, some old and
some new(er) and, of course, to demonstrate my tech chops (ahem). But this also dovetailed with another little hacking exercise [bashenv](https://github.com/mcarifio/bashenv/), which follows in the vein of [oh-my-bash](https://github.com/ohmybash/oh-my-bash) without either the completeness or polish.
Besides flexing my bash scripting skills, especially bash functions, `bashenv` generates an installation script for a command once you
select the format you want (e.g. `dnf`, `pip`, `asdf` and so on). If you've installed something, `bashenv` will create functions to wrap
the relevant command with _your_ preferred default arguments. If the command provides completions, there's a convention to load them.
It makes commands just a little more consistent by overlaying
a set of bash functions with a naming convention over the installed commands provided by various package managers. But the best part
is that I can git clone the repository on a machine, `run-part` the installation directory and then source all the command "guards" and
I'm good-to-go. I can even pick and chose what I install and the "guards" handle the rest. fsm does something similar, but in python,
a much better programming language than bash.





