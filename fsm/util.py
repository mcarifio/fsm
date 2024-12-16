"""
Module util dispatches an "action" verb such as `main` or `test` to a function in that module with a stylized name,
e.g. `on_main(argv:list[str])` `or `on_test(argv:list[str])`. This is a smaller and self-contained version of the google-fire python package.

The benefits of a dispatcher are: 1) it makes single file python modules invocable at the command line, e.g.
`python -m some_module some_action arg0 arg1` for example `python -m graph test` and 2) it provides a simple kind of
protocol each module can follow (actions `main`, `test`, `about` and so forth). There are a few drawbacks: 1) the implementation
depends on the global bindings of a module (e.g. `globals()`), 2) the implementation creates a dispatcher function which is closure
and dispatching usage, although stylized, can initially confuse: `if __name__ == '__main__': mkdispatcher(globals())(sys.argv)`
"""

import logging
logger = logging.getLogger(__name__)
import sys
import inspect
import types


def caller():
    """
    Return the name of the function that calls `caller()`, e.g. `def my_calling(): return caller(); my_calling()` returns `my_calling`.
    This is helpful for logging, diagnosis and debugging in more dynamic situations (and frankly cut-and-paste programming).
    :return:
    """
    return inspect.currentframe().f_back.f_code.co_name


def actors(bindings, prefix: str = "on_") -> dict[str, types.FunctionType]:
    """
    Return all top level functions in a module that match a prefix, e.g. all `on_` functions.
    :param bindings: module bindings as returned by `globals()`
    :param prefix: how to match the functions
    :return: a dictionary of function names to functions, suitable for later dispatching.
    """
    return { a[len(prefix):]: bindings[a] for a in bindings.keys() if a.startswith(prefix) and isinstance(bindings[a], types.FunctionType) }

def mkdispatch(bindings):
    """
    Make and return a closure that will dispatch `action` to `on_action()`, for example `main` to `on_main()` based on the global
    function definitions of `bindings`. The typical usage will look like:

    ```python
    # say.py
    import sys; import dispatcher
    def on_say(args): print(caller(), *args)
    if __name__ == '__main__': dispatcher.mkdispatch(globals())(sys.argv)  ## python -m say something right now |> on_say right now
    ```

    :param bindings: module bindings as returned by `globals()`
    :return: closure over all functions matching a prefix.
    """

    # actions, all the actions I can dispatch to (all functions named on_{action})
    actions: dict[str, types.FunctionType] = actors(bindings)

    def _dispatch(argv):
        action = argv[0] if len(argv) > 0 else "main"
        rest: list[str] = argv[1:] if len(argv) > 1 else []

        match action:
            case "actions":
                print(action, *actions, file=sys.stderr)
            case a if a in actions.keys():
                return actions[a](rest)
            case _:
                print(f"Unknown action: {action}", file=sys.stderr)

    return _dispatch
