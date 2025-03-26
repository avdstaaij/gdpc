from typing import Union, Optional, Tuple, Any

import numpy as np
import numpy.typing as npt


def binary_dilation(
    input: npt.NDArray[Any],
    structure: Optional[npt.NDArray[Any]] = None,
    iterations: int = 1,
    mask: Optional[npt.NDArray[Any]] = None,
    output: Optional[npt.NDArray[Any]] = None,
    border_value: int = 0,
    origin: Union[int, Tuple[int, ...]] =0,
    brute_force: bool = False
) -> npt.NDArray[np.bool_]: ...
