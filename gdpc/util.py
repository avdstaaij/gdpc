"""Generic utilities"""


from typing import TypeVar, Callable
import time
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


def withRetries(
    function: Callable[[], T],
    retries:  int                              = 1,
    onRetry:  Callable[[Exception, int], None] = lambda *_: time.sleep(1)
):
    """Retries <function> up to <retries> times if an exception occurs.\n
    Before retrying, calls <onRetry>(last exception, remaining retries).
    The default callback sleeps for one second.\n
    If the retries have ran out, re-raises the last exception."""
    retriesLeft = retries
    while True:
        try:
            return function()
        # TODO: is it possible to take the type of the exception to catch here as a parameter?
        except Exception as e: # pylint: disable=broad-except
            if retriesLeft == 0:
                raise e
            onRetry(e, retriesLeft)
            retriesLeft -= 1
