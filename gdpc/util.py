"""Generic utilities"""


from typing import TypeVar
from contextlib import contextmanager
import sys
import numpy as np


T = TypeVar("T")


def sign(x) -> int:
    """Returns the sign of [x]"""
    return (x > 0) - (x < 0)


def non_zero_sign(x) -> int:
    """Returns the sign of [x], except that non_zero_sign(0) == 1"""
    return 1 if x >= 0 else -1


def clamp(x: T, minimum: T, maximum: T) -> T:
    """Clamps [x] to the range [minimum, maximum]"""
    return max(minimum, min(maximum, x))


def eprint(*args, **kwargs):
    """print(), but to stderr"""
    print(*args, file=sys.stderr, **kwargs)


# Based on https://stackoverflow.com/a/21032099
def normalized(a, order=2, axis=-1):
    """Normalizes [a] using the L[order] norm.\n
    If [axis] is specified, normalizes along that axis."""
    norm = np.atleast_1d(np.linalg.norm(a, order, axis))
    norm[norm==0] = 1
    return a / np.expand_dims(norm, axis)


# Based on https://stackoverflow.com/q/2125702
@contextmanager
def stdoutToStderr():
    """ Redirects stdout to stderr within its scope """
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout
