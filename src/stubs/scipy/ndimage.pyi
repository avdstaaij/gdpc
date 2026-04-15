from typing import Any

import numpy as np
import numpy.typing as npt

def binary_dilation(
    input: npt.NDArray[Any],
    structure: npt.NDArray[Any] | None = None,
    iterations: int = 1,
    mask: npt.NDArray[Any] | None = None,
    output: npt.NDArray[Any] | None = None,
    border_value: int = 0,
    origin: int | tuple[int, ...] =0,
    brute_force: bool = False,
) -> npt.NDArray[np.bool_]: ...
