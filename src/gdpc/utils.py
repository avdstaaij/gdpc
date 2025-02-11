"""Various generic utilities."""

from typing import Any, Generator, Sequence, TypeVar, Generic, Callable, Iterable, OrderedDict, Union
import time
from pathlib import Path

import numpy as np
import cv2
from matplotlib import pyplot as plt


T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")


def sign(x) -> int:
    """Returns the sign of ``x``"""
    return (x > 0) - (x < 0)


def nonZeroSign(x) -> int:
    """Returns the sign of ``x``, except that ``nonZeroSign(0) == 1``"""
    return 1 if x >= 0 else -1


def clamp(x: T, minimum: T, maximum: T) -> T:
    """Clamps ``x`` to the range [``minimum``, ``maximum``]"""
    return max(minimum, min(maximum, x))


def eagerAll(iterable: Iterable) -> bool:
    """Like ``all()``, but always evaluates every element"""
    results = list(iterable)
    return all(results)

def eagerAny(iterable: Iterable) -> bool:
    """Like ``any()``, but always evaluates every element"""
    results = list(iterable)
    return any(results)


# Based on https://stackoverflow.com/a/21032099
def normalized(a, order=2, axis=-1):
    """Normalizes ``a`` using the L<order> norm.\n
    If ``axis`` is specified, normalizes along that axis."""
    norm = np.atleast_1d(np.linalg.norm(a, order, axis))
    norm[norm==0] = 1
    return a / np.expand_dims(norm, axis)


def withRetries(
    function:      Callable[[], T],
    exceptionType: type                             = Exception,
    retries:       int                              = 1,
    onRetry:       Callable[[Exception, int], None] = lambda *_: time.sleep(1),
    reRaise:       bool                             = True
) -> Union[T, None]:
    """Retries ``function`` up to ``retries`` times if an exception occurs.\n
    Before retrying, calls ``onRetry(<last exception>, <remaining retries>)``.
    The default callback sleeps for one second.\n
    If the retries have ran out and ``reRaise`` is ``True``, the last exception is re-raised."""
    while True:
        try:
            return function()
        except exceptionType as e: # pylint: disable=broad-except
            if retries == 0:
                if reRaise:
                    raise e
                return None
            onRetry(e, retries)
            retries -= 1


def isIterable(value) -> bool:
    """Determine whether ``value`` is iterable."""
    try:
        _ = iter(value)
        return True
    except TypeError:
        return False


def isSequence(value) -> bool:
    """Determine whether ``value`` is a sequence."""
    try:
        _ = value[0]
        return True
    except TypeError:
        return False


class OrderedByLookupDict(OrderedDict[KT, VT], Generic[KT, VT]):
    """Dict ordered from least to most recently looked-up key\n

    Unless ``maxSize`` is 0, the dict size is limited to ``maxSize`` by evicting the least recently
    looked-up key when full.
    """
    # Based on
    # https://docs.python.org/3/library/collections.html?highlight=ordereddict#collections.OrderedDict

    def __init__(self, maxSize: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._maxSize = maxSize

    # inherited __repr__ from OrderedDict is sufficient

    @property
    def maxSize(self) -> int:
        return self._maxSize

    @maxSize.setter
    def maxSize(self, value: int) -> None:
        self._maxSize = value
        if self._maxSize > 0:
            while len(self) > self.maxSize:
                oldest = next(iter(self))
                del self[oldest]

    def __getitem__(self, key: KT) -> VT:
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key: KT, value: VT) -> None:
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if self._maxSize > 0 and len(self) > self._maxSize:
            oldest = next(iter(self))
            del self[oldest]


def visualizeMaps(*arrays, title="", normalize=True) -> None:
    """Visualizes one or multiple 2D numpy arrays."""
    for array in arrays:
        if normalize:
            array = ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8)

        plt.figure()
        if title:
            plt.title(title)
        plt_image = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        plt.imshow(plt_image)
    plt.show()


def readFileBytes(
    filePath: Union[Path, str]
) -> bytes:
    """Opens stored file and returns it a string of bytes."""
    if isinstance(filePath, str):
        filePath = Path(filePath)
    with open(filePath, 'rb') as fileObject:
        rawBytes = fileObject.read()
    return rawBytes


def rotateSequence(sequence: Sequence, n: int = 1) -> Generator[Any, Any, None]:
    """Rotates a sequence of elements by n positions.

    Args:
        sequence (Sequence): The sequence of elements to rotate.
        n (int, optional):   The number of positions to rotate the sequence by. Defaults to 1.

    Yields:
        Generator[Any, Any, None]: The rotated sequence of elements.
    """
    if not sequence:
        return
    yield from (*sequence[n:], *sequence[:n])
