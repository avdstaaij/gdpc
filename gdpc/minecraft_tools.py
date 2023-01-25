"""Provides various Minecraft-related utility functions."""


from typing import Any, Optional, Union, List
from functools import lru_cache

from glm import ivec2

from .vector_tools import Rect
from . import lookup
from .block import Block


# ==================================================================================================
# NBT generation utilities
# ==================================================================================================


def signData(
    line1: str = "",
    line2: str = "",
    line3: str = "",
    line4: str = "",
    color: str = "",
    isGlowing: bool = False,
):
    """Returns a JSON-like structure of Python objects with sign data"""
    data = {}

    for i, line in enumerate([line1, line2, line3, line4]):
        if line:
            data[f"Text{i+1}"] = f'{{"text":"{line}"}}'

    if color:
        data["Color"] = color

    if isGlowing:
        data["GlowingText"] = "true"

    return data


def lecternData(bookData: Any, page: int = 0):
    """Returns a JSON-like structure of Python objects with lectern data"""
    if bookData is None:
        return None
    return {"Book": {"id": "minecraft:written_book", "Count": 1, "tag": bookData}, "Page": page}


def bookData(
    text: str,
    title       = "Chronicle",
    author      = "Anonymous",
    description = "I wonder what\\'s inside?",
    desccolor   = "gold"
):
    r"""Returns a JSON-like structure of Python objects with written book data

    The following special characters are used for formatting the book:
    - `\n`: New line
    - `\f`: Form/page break

    - `§0`: Black text
    - '§1': Dark blue text
    - '§2': Dark green text
    - '§3': Dark aqua text
    - '§4': Dark red text
    - '§5': Dark purple text
    - '§6': Gold text
    - '§7': Gray text
    - '§8': Dark gray text
    - '§9': Blue text
    - `§a`: Green text
    - `§b`: Aqua text
    - `§c`: Red text
    - `§d`: Light purple text
    - `§e`: Yellow text
    - `§f`: White text

    - `§k`: Obfuscated text
    - `§l`: **Bold** text
    - `§m`: ~~Strikethrough~~ text
    - `§n`: __Underline__ text
    - `§o`: *Italic* text
    - `§r`: Reset text formatting

    - `\\\\s`: When at start of page, print page as string directly
    - `\\c`: When at start of line, align text to center
    - `\\r`: When at start of line, align text to right side

    NOTE: For supported special characters see
    https://minecraft.fandom.com/wiki/Language#Font

    IMPORTANT: When using `\\s` text is directly interpreted by Minecraft,
    so all line breaks must be `\\\\n` to function
    """
    pages_left      = lookup.BOOK_PAGES_PER_BOOK
    characters_left = lookup.BOOK_CHARACTERS_PER_PAGE
    lines_left      = lookup.BOOK_LINES_PER_PAGE
    pixels_left     = lookup.BOOK_PIXELS_PER_LINE
    toprint = ''

    @lru_cache()
    def fontwidth(word):
        """Return the length of a word based on character width.

        If a letter is not found, a width of 9 is assumed
        A character spacing of 1 is automatically integrated
        """
        return sum([lookup.ASCII_CHAR_TO_WIDTH.get(letter, 9) + 1 for letter in word]) - 1

    def printline():
        nonlocal pageData, toprint
        formatting = toprint[:2]
        spaces_left = pixels_left // 4 + 3
        if formatting == '\\c':      # centered text
            pageData[-1] += spaces_left // 2 * ' ' + toprint[2:-1] + spaces_left // 2 * ' '
        elif formatting == '\\r':    # right-aligned text
            pageData[-1] += spaces_left * ' ' + toprint[2:-1]
        else:
            pageData[-1] += toprint
        toprint = ''

    def newline():
        nonlocal characters_left, lines_left, pixels_left, pageData
        printline()
        if characters_left < 2 or lines_left < 1:
            newpage()
            return
        characters_left -= 2
        lines_left -= 1
        pixels_left = lookup.BOOK_PIXELS_PER_LINE
        pageData[-1] += "\\n"

    def newpage():
        nonlocal characters_left, lines_left, pixels_left, pageData
        printline()
        characters_left = lookup.BOOK_CHARACTERS_PER_PAGE
        lines_left      = lookup.BOOK_LINES_PER_PAGE
        pixels_left     = lookup.BOOK_PIXELS_PER_LINE
        pageData.append("") # end page and start new page

    pages = [page for page in text.split('\f')]

    pageData: List[str] = [""] # start first page

    for page in pages:
        if pages_left < 1:
            break
        if page[:3] == '\\\\s':
            pageData[-1] += page[3:]
            newpage()
            continue
        else:
            page = [[word for word in line.split()] for line in page.split('\n')]
        for line in page:
            toprint = ""
            for word in line:
                width = fontwidth(word + ' ')
                if width > pixels_left:
                    if width > lookup.BOOK_PIXELS_PER_LINE:  # cut word to fit
                        original = word
                        for letter in original:
                            charwidth = fontwidth(letter) + 1
                            if charwidth > pixels_left:
                                newline()
                            toprint += letter
                            width -= charwidth
                            word = word[1:]
                            characters_left -= 1
                            pixels_left -= charwidth
                            if not width > pixels_left:
                                break
                    else:
                        newline()
                if len(word) > characters_left:
                    newpage()
                toprint += word + ' '
                characters_left -= len(word) + 1
                pixels_left -= width
            newline()           # finish line
        newpage()               # finish page
    del pageData[-1] # end last page (book is complete)

    return {
        "title": title,
        "author": author,
        "display": {"Lore": [f'[{{"text":"{description}","color":"{desccolor}"}}]']},
        "pages": [f'{{"text":"{page}"}}' for page in pageData]
    }


# ==================================================================================================
# Block generating utilities
# ==================================================================================================


def signBlock(
    wood="oak", wall=False,
    facing: str = "north", rotation: Union[str,int] = "0",
    text1="", text2="", text3="", text4="", color="", isGlowing=False
):
    """Returns a sign Block with the specified properties."""
    blockId = f"minecraft:{wood}_{'wall_' if wall else ''}sign"
    states = {"facing": facing} if wall else {"rotation": str(rotation)}
    return Block(blockId, states, data=signData(text1, text2, text3, text4, color, isGlowing))


def lecternBlock(facing: str = "north", bookData: Optional[str] = None, page: int = 0):
    """Returns a lectern Block with the specified properties."""
    return Block(
        "minecraft:lectern",
        {"facing": facing, "has_book": ("false" if bookData is None else "true")},
        data=lecternData(bookData, page)
    )


# ==================================================================================================
# Misc. utilities
# ==================================================================================================


def positionToInventoryIndex(position: ivec2, inventorySize: ivec2):
    """Returns the flat index of the slot at <position> in an inventory of size <inventorySize>."""
    if not Rect(size=inventorySize).contains(position):
        raise ValueError(f"{position} is not between (0, 0) and {inventorySize}!")
    return position.x + position.y * inventorySize.x


def getObtrusiveness(block: Block):
    """Returns the percieved obtrusiveness of the given <block>.\n
    Returns a numeric weight from 0 (invisible) to 4 (opaque)."""
    if not isinstance(block.id, str):
        raise ValueError("Cannot determine the obtrusiveness of a block palette!")
    if block.id in lookup.INVISIBLE:
        return 0
    if block.id in lookup.FILTERING:
        return 1
    if block.id in lookup.UNOBTRUSIVE:
        return 2
    if block.id in lookup.OBTRUSIVE:
        return 3
    return 4
