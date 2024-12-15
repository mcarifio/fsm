import warnings


def check(expression: bool, message: str, warn: bool = False) -> bool:
    if warn and not expression:
        warnings.warn(message, stacklevel=2)
    else:
        assert expression, message
    return expression
