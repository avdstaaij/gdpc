"""Provides various Minecraft-related utilities that do not require an :class:`.Editor`."""


from typing import Optional, Union, List
from functools import lru_cache
import json
from deprecated import deprecated

from .vector_tools import Vec2iLike, Rect
from .block import Block


# ==================================================================================================
# Constants
# ==================================================================================================


# the width of ASCII characters in pixels
# space between characters is 1
# the widest supported Unicode character is 9 wide
_ASCII_CHAR_TO_WIDTH = {
    "A":  5,
    "a":  5,
    "B":  5,
    "b":  5,
    "C":  5,
    "c":  5,
    "D":  5,
    "d":  5,
    "E":  5,
    "e":  5,
    "F":  5,
    "f":  4,
    "G":  5,
    "g":  5,
    "H":  5,
    "h":  5,
    "I":  3,
    "i":  1,
    "J":  5,
    "j":  5,
    "K":  5,
    "k":  4,
    "L":  5,
    "l":  2,
    "M":  5,
    "m":  5,
    "N":  5,
    "n":  5,
    "O":  5,
    "o":  5,
    "P":  5,
    "p":  5,
    "Q":  5,
    "q":  5,
    "R":  5,
    "r":  5,
    "S":  5,
    "s":  5,
    "T":  5,
    "t":  3,
    "U":  5,
    "u":  5,
    "V":  5,
    "v":  5,
    "W":  5,
    "w":  5,
    "X":  5,
    "x":  5,
    "Y":  5,
    "y":  5,
    "Z":  5,
    "z":  5,
    "1":  5,
    "2":  5,
    "3":  5,
    "4":  5,
    "5":  5,
    "6":  5,
    "7":  5,
    "8":  5,
    "9":  5,
    "0":  5,
    " ":  3,
    "!":  1,
    "@":  6,
    "#":  5,
    "$":  5,
    "£":  5,
    "%":  5,
    "^":  5,
    "&":  5,
    "*":  3,
    "(":  3,
    ")":  3,
    "_":  5,
    "-":  5,
    "+":  5,
    "=":  5,
    "~":  6,
    "[":  3,
    "]":  3,
    "{":  3,
    "}":  3,
    "|":  1,
    "\\": 5,
    ":":  1,
    ";":  1,
    '"':  3,
    "'":  1,
    ",":  1,
    "<":  4,
    ">":  4,
    ".":  1,
    "?":  5,
    "/":  5,
    "`":  2,
}


_BOOK_PAGES_PER_BOOK      = 100
_BOOK_CHARACTERS_PER_PAGE = 255
_BOOK_LINES_PER_PAGE      = 14
_BOOK_PIXELS_PER_LINE     = 114


# ==================================================================================================
# SNBT generation utilities
# ==================================================================================================


def signData(
    frontLine1: str = "",
    frontLine2: str = "",
    frontLine3: str = "",
    frontLine4: str = "",
    frontColor: str = "",
    frontIsGlowing: bool = False,
    backLine1: str = "",
    backLine2: str = "",
    backLine3: str = "",
    backLine4: str = "",
    backColor: str = "",
    backIsGlowing: bool = False,
    isWaxed = False
) -> str:
    """Returns an SNBT string with sign data.\n
    See also: :func:`.signBlock`, :func:`.editor_tools.placeSign`."""

    def sideCompound(line1: str, line2: str, line3: str, line4: str, color: str, isGlowing: bool):
        fields: List[str] = []
        fields.append(f'messages: [{",".join(repr(json.dumps({"text": line})) for line in [line1, line2, line3, line4])}]')
        if color:
            fields.append(f'Color: {repr(color)}')
        if isGlowing:
            fields.append('GlowingText: 1b')
        return "{" + ",".join(fields) + "}"

    fields: List[str] = []
    fields.append(f"front_text: {sideCompound(frontLine1, frontLine2, frontLine3, frontLine4, frontColor, frontIsGlowing)}")
    fields.append( f"back_text: {sideCompound(backLine1,  backLine2,  backLine3,  backLine4,  backColor,  backIsGlowing)}")
    if isWaxed:
        fields.append("is_waxed: 1b")
    return "{" + ",".join(fields) + "}"


def lecternData(bookData: Optional[str], page: int = 0) -> str:
    """Returns an SNBT string with lectern data.\n
    ``bookData`` should be an SNBT string defining a book.
    You can use :func:`.bookData` to create such a string.\n
    See also: :func:`.lecternBlock`, :func:`.editor_tools.placeLectern`."""
    if bookData is None:
        return ""
    return f'{{Book: {{id: "minecraft:written_book", Count: 1b, components: {bookData}, Page: {page}}}}}'


def bookData(
    text: str,
    title       = "Chronicle",
    author      = "Anonymous",
    description = "I wonder what's inside?",
    desccolor   = "gold",
    descIsItalic = True
) -> str:
    r"""Returns an SNBT string with written book data

    The following special characters can be used to format the book:

    - ``\n``: New line
    - ``\f``: Form/page break
    - ``§0``: Black text
    - ``§1``: Dark blue text
    - ``§2``: Dark green text
    - ``§3``: Dark aqua text
    - ``§4``: Dark red text
    - ``§5``: Dark purple text
    - ``§6``: Gold text
    - ``§7``: Gray text
    - ``§8``: Dark gray text
    - ``§9``: Blue text
    - ``§a``: Green text
    - ``§b``: Aqua text
    - ``§c``: Red text
    - ``§d``: Light purple text
    - ``§e``: Yellow text
    - ``§f``: White text
    - ``§k``: Obfuscated text
    - ``§l``: **Bold** text
    - ``§m``: ~~Strikethrough~~ text
    - ``§n``: __Underline__ text
    - ``§o``: *Italic* text
    - ``§r``: Reset text formatting
    - ``\\\\s``: When at start of page, print page as string directly
    - ``\\c``: When at start of line, align text to center
    - ``\\r``: When at start of line, align text to right side

    NOTE: For supported special characters see
    https://minecraft.wiki/Language#Font
    """
    pages_left      = _BOOK_PAGES_PER_BOOK
    characters_left = _BOOK_CHARACTERS_PER_PAGE
    lines_left      = _BOOK_LINES_PER_PAGE
    pixels_left     = _BOOK_PIXELS_PER_LINE
    toprint = ''

    @lru_cache()
    def fontwidth(word):
        """Return the length of a word based on character width.

        If a letter is not found, a width of 9 is assumed
        A character spacing of 1 is automatically integrated
        """
        return sum(_ASCII_CHAR_TO_WIDTH.get(letter, 9) + 1 for letter in word) - 1

    SPACE_WIDTH = fontwidth(' ')

    def printline():
        nonlocal outputPages, toprint
        formatting = toprint[:2]
        spaces_left = pixels_left // 4 + 3
        if formatting == '\\c':      # centered text
            outputPages[-1] += spaces_left // 2 * ' ' + toprint[2:-1] + spaces_left // 2 * ' '
        elif formatting == '\\r':    # right-aligned text
            outputPages[-1] += spaces_left * ' ' + toprint[2:-1]
        else:
            outputPages[-1] += toprint
        toprint = ''

    def newline():
        nonlocal characters_left, lines_left, pixels_left, outputPages
        printline()
        if characters_left < 2 or lines_left < 1:
            newpage()
            return
        characters_left -= 2
        lines_left -= 1
        pixels_left = _BOOK_PIXELS_PER_LINE
        outputPages[-1] += "\n"

    def newpage():
        nonlocal characters_left, lines_left, pixels_left, outputPages
        printline()
        characters_left = _BOOK_CHARACTERS_PER_PAGE
        lines_left      = _BOOK_LINES_PER_PAGE
        pixels_left     = _BOOK_PIXELS_PER_LINE
        outputPages.append("") # end page and start new page

    pages = list(text.split('\f'))

    outputPages: List[str] = [""] # start first page

    for page in pages:
        if pages_left < 1:
            break
        if page[:3] == '\\\\s':
            outputPages[-1] += page[3:]
            newpage()
            continue
        else:
            page = [[word for word in line.split()] for line in page.split('\n')]
        for line in page:
            toprint = ""
            for word in line:
                if pixels_left != _BOOK_PIXELS_PER_LINE:
                    if characters_left < 1:
                        newpage()
                    elif SPACE_WIDTH > pixels_left:
                        newline()
                    else:
                        toprint += ' '
                        characters_left -= 1
                        pixels_left -= SPACE_WIDTH

                width = fontwidth(word)
                if width > pixels_left:
                    if width > _BOOK_PIXELS_PER_LINE:  # cut word to fit
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
                toprint += word
                characters_left -= len(word)
                pixels_left -= width
            newline()           # finish line
        newpage()               # finish page
    del outputPages[-1] # end last page (book is complete)

    loreJSON = json.dumps({"text": description, "color": desccolor, "italic": descIsItalic})
    pageJSON = [json.dumps({"text": p}) for p in outputPages]
    return (
        "{"
            "\"minecraft:written_book_content\": {"
                f'title: {repr(title)}, '
                f'author: {repr(author)}, '
                f'pages: [{",".join(repr(p) for p in pageJSON)}]'
            "},"
            f'"lore": [{repr(loreJSON)}]'
        "}"
    )


# ==================================================================================================
# Block generating utilities
# ==================================================================================================


def signBlock(
    wood="oak", wall=False,
    facing: str = "north", rotation: Union[str,int] = "0",
    frontLine1="", frontLine2="", frontLine3="", frontLine4="", frontColor="", frontIsGlowing=False,
    backLine1="",  backLine2="",  backLine3="",  backLine4="",  backColor="",  backIsGlowing=False,
    isWaxed = False
) -> Block:
    """Returns a sign Block with the specified properties.\n
    See also: :func:`.signData`, :func:`.editor_tools.placeSign`."""
    blockId = f"minecraft:{wood}_{'wall_' if wall else ''}sign"
    states = {"facing": facing} if wall else {"rotation": str(rotation)}
    return Block(
        blockId, states,
        data=signData(
            frontLine1, frontLine2, frontLine3, frontLine4, frontColor, frontIsGlowing,
            backLine1, backLine2, backLine3, backLine4, backColor, backIsGlowing,
            isWaxed
        )
    )


def lecternBlock(facing: str = "north", bookData: Optional[str] = None, page: int = 0) -> Block:
    """Returns a lectern Block with the specified properties.\n
    ``bookData`` should be an SNBT string defining a book.
    You can use :func:`.bookData` to create such a string.\n
    See also: :func:`.lecternData`, :func:`.editor_tools.placeLectern`."""
    return Block(
        "minecraft:lectern",
        {"facing": facing, "has_book": ("false" if bookData is None else "true")},
        data=lecternData(bookData, page)
    )


# ==================================================================================================
# Misc. utilities
# ==================================================================================================


def positionToInventoryIndex(position: Vec2iLike, inventorySize: Vec2iLike) -> int:
    """Returns the flat index of the slot at ``position`` in an inventory of size ``inventorySize``."""
    if not Rect(size=inventorySize).contains(position):
        raise ValueError(f"{position} is not between (0, 0) and {tuple(inventorySize)}!")
    return position[0] + position[1] * inventorySize[0]


@deprecated("Deprecated along with lookup.py. See the documentation for the lookup.py module for the reasons and for alternatives.")
def getObtrusiveness(block: Block) -> int:
    """
    .. warning::
        :title: Deprecated

        Deprecated along with :mod:`.lookup`. See the warning at the top of
        the `lookup` page for the reasons and for alternatives.

    Returns the percieved obtrusiveness of the given ``block``.

    Returns a numeric weight from 0 (invisible) to 4 (opaque).
    """
    from . import lookup # pylint: disable=import-outside-toplevel
    if not block.id:
        return 0
    if block.id in lookup.INVISIBLE:
        return 0
    if block.id in lookup.FILTERING:
        return 1
    if block.id in lookup.UNOBTRUSIVE:
        return 2
    if block.id in lookup.OBTRUSIVE:
        return 3
    return 4
