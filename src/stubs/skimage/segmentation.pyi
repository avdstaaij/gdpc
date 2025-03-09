from typing import Union, Optional, Tuple, Any

import numpy.typing as npt


def flood_fill(
    image: npt.NDArray[Any],
    seed_point: Union[int, Tuple[int, ...]],
    new_value: Any,
    *,
    footprint: Optional[npt.NDArray[Any]] = None,
    connectivity: Optional[int] = None,
    tolerance: Optional[Union[int, float]] = None,
    in_place: bool = False
) -> npt.NDArray[Any]: ...
