"""Block data-generating utility functions"""


from typing import List, Optional


def signData(
    line1:   Optional[str] = None,
    line2:   Optional[str] = None,
    line3:   Optional[str] = None,
    line4:   Optional[str] = None,
    color:   Optional[str] = None,
):
    """Returns an SNBT string with sign contents"""
    nbtFields: List[str] = []

    for i, line in enumerate([line1, line2, line3, line4]):
        if line is not None:
            nbtFields.append(f"Text{i+1}: '{{\"text\":\"{line}\"}}'")

    if color is not None:
        nbtFields.append(f"Color: \"{color}\"")

    return ",".join(nbtFields)
