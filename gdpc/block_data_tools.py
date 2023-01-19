"""Block entity data-generating utility functions"""


from typing import List, Optional


def signData(
    line1: str = "",
    line2: str = "",
    line3: str = "",
    line4: str = "",
    color: str = "",
):
    """Returns an SNBT string with sign data"""
    nbtFields: List[str] = []

    for i, line in enumerate([line1, line2, line3, line4]):
        if line:
            nbtFields.append(f"Text{i+1}: '{{\"text\":\"{line}\"}}'")

    if color:
        nbtFields.append(f"Color: \"{color}\"")

    return ",".join(nbtFields)


def lecternData(bookData: Optional[str] = None, page: int = 0):
    """Returns an SNBT string with lectern data"""
    if bookData is None:
        return ""
    return f'Book: {{id: "minecraft:written_book", Count: 1b, tag: {bookData}}}, Page: {page}'
