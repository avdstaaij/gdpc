from typing import Any

import numpy.typing as npt

def flood_fill(
    image: npt.NDArray[Any],
    seed_point: int | tuple[int, ...],
    new_value: Any,
    *,
    footprint: npt.NDArray[Any] | None = None,
    connectivity: int | None = None,
    tolerance: float | None = None,
    in_place: bool = False,
) -> npt.NDArray[Any]: ...
