"""Various generic utilities."""

from typing import Protocol, Any, Generator, Sequence, TypeVar, Generic, Callable, Iterable, OrderedDict, Union, Type
import time
from pathlib import Path

from deprecated import deprecated
import numpy as np
import numpy.typing as npt
import cv2
from matplotlib import pyplot as plt


T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")

class _Comparable(Protocol):
    """Protocol for types that can be compared.\n
    The requirements are very loose."""
    def __eq__(self, *args: Any, **kwargs: Any) -> bool:
        ...

    def __lt__(self, *args: Any, **kwargs: Any) -> bool:
        ...

ComparableT = TypeVar("ComparableT", bound=_Comparable)


def sign(x: Any) -> int:
    """Returns the sign of ``x``"""
    return (x > 0) - (x < 0)


def nonZeroSign(x: Any) -> int:
    """Returns the sign of ``x``, except that ``nonZeroSign(0) == 1``"""
    return 1 if x >= 0 else -1


def clamp(x: ComparableT, minimum: ComparableT, maximum: ComparableT) -> ComparableT:
    """Clamps ``x`` to the range [``minimum``, ``maximum``]"""
    return max(minimum, min(maximum, x))


def eagerAll(iterable: Iterable[Any]) -> bool:
    """Like ``all()``, but always evaluates every element"""
    results = list(iterable)
    return all(results)

def eagerAny(iterable: Iterable[Any]) -> bool:
    """Like ``any()``, but always evaluates every element"""
    results = list(iterable)
    return any(results)


# Based on https://stackoverflow.com/a/21032099
def normalized(a: npt.NDArray[Any], order: int = 2, axis: int = -1):
    """Normalizes ``a`` using the L<order> norm.\n
    If ``axis`` is specified, normalizes along that axis."""
    norm = np.atleast_1d(np.linalg.norm(a, order, axis)) # pyright: ignore [reportUnknownVariableType]
    norm[norm==0] = 1
    return a / np.expand_dims(norm, axis) # pyright: ignore [reportUnknownArgumentType]


def withRetries(
    function:      Callable[[], T],
    exceptionType: Type[Exception]                  = Exception,
    retries:       int                              = 1,
    onRetry:       Callable[[Exception, int], None] = lambda _1,_2: time.sleep(1),
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


def isIterable(value: Any) -> bool:
    """Determine whether ``value`` is iterable."""
    try:
        _ = iter(value)
        return True
    except TypeError:
        return False


def isSequence(value: Any) -> bool:
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

    def __init__(self, maxSize: int, *args: Any, **kwargs: Any):
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


@deprecated
def visualizeMaps(*arrays: npt.NDArray[Any], title: str = "", normalize: bool = True) -> None:
    """
    .. warning::
        :title: Deprecated

        This function is deprecated and will be removed in a future version of GDPC.

        It was only used by the now-removed ``visualize_map.py`` example, and its
        removal will allow us to remove the OpenCV dependency.

    Visualizes one or multiple 2D numpy arrays.
    """
    for array in arrays:
        if normalize:
            array = ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8) # pyright: ignore [reportUnknownMemberType]

        plt.figure() # type: ignore
        if title:
            plt.title(title) # type: ignore
        plt_image = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        plt.imshow(plt_image) # type: ignore
    plt.show() # type: ignore


def readFileBytes(
    filePath: Union[Path, str]
) -> bytes:
    """Opens stored file and returns it a string of bytes."""
    if isinstance(filePath, str):
        filePath = Path(filePath)
    with open(filePath, 'rb') as fileObject:
        rawBytes = fileObject.read()
    return rawBytes


def rotateSequence(sequence: Sequence[T], n: int = 1) -> Generator[T, None, None]:
    """Rotates a sequence of elements by n positions.

    Args:
        sequence (Sequence): The sequence of elements to rotate.
        n (int, optional):   The number of positions to rotate the sequence by. Defaults to 1.

    Yields:
        Generator[Any, Any, None]: The rotated sequence of elements.
    """
    if not sequence:
        return
    yield from sequence[n:]
    yield from sequence[:n]
