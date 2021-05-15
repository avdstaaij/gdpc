#! /usr/bin/python3
"""### Provides various small functions for the average workflow."""

__all__ = []
__version__ = 'v4.2_dev'
__year__ = '2021'
__author__ = 'Blinkenlights'

from functools import lru_cache
from random import choice

import lookup
from interfaceUtils import getBlock
from interfaceUtils import globalinterface as gi
from interfaceUtils import runCommand


def loop2d(dx, dz):
    """**Return all coordinates in a region of size dx, dz**."""
    for x in range(dx + 1):
        for z in range(dz + 1):
            yield x, z


def loop3d(dx, dy, dz):
    """**Return all coordinates in a region of size dx, dy, dz**."""
    for x in range(dx + 1):
        for y in range(dy + 1):
            for z in range(dz + 1):
                yield x, y, z


def writeBook(text, title="Chronicle", author=__author__,
              description="I wonder what's inside?", desccolor='gold'):
    r"""**Return NBT data for a correctly formatted book**.

    The following special characters are used for formatting the book:
    - `\n`: New line
    - `\f`: Form/page break

    - `§0`: Black text
    - '§1': Dark blue text
    - '§2': Dark_green text
    - '§3': Dark_aqua text
    - '§4': Dark_red text
    - '§5': Dark_purple text
    - '§6': Gold text
    - '§7': Gray text
    - '§8': Dark_gray text
    - '§9': Blue text
    - `§a`: Green text
    - `§b`: Aqua text
    - `§c`: Red text
    - `§d`: Light_purple text
    - `§e`: Yellow text
    - `§f`: White text

    - `§k`: Obfuscated text
    - `§l`: **Bold** text
    - `§m`: ~~Strikethrough~~ text
    - `§n`: __Underline__ text
    - `§o`: *Italic* text
    - `§r`: Reset text formatting

    - `\\s`: When at start of page, print page as string directly
    - `\\c`: When at start of line, align text to center
    - `\\r`: When at start of line, align text to right side

    NOTE: For supported special characters see
        https://minecraft.fandom.com/wiki/Language#Font
    IMPORTANT: When using `\\s` text is directly interpreted by Minecraft,
        so all line breaks must be `\\\\n` to function
    """
    pages_left = 97                     # per book
    characters_left = CHARACTERS = 255  # per page
    lines_left = LINES = 14             # per page
    pixels_left = PIXELS = 113          # per line
    toprint = ''

    @lru_cache
    def fontwidth(word):
        """**Return the length of a word based on character width**.

        If a letter is not found, a width of 9 is assumed
        A character spacing of 1 is automatically integrated
        """
        return sum([lookup.ASCIIPIXELS[letter] + 1
                    if letter in lookup.ASCIIPIXELS
                    else 10
                    for letter in word]) - 1

    def printline():
        nonlocal bookData, toprint
        formatting = toprint[:2]
        spaces_left = pixels_left // 4 + 3
        if formatting == '\\c':      # centered text
            bookData += spaces_left // 2 * ' ' \
                + toprint[2:-1] + spaces_left // 2 * ' '
        elif formatting == '\\r':    # right-aligned text
            bookData += spaces_left * ' ' + toprint[2:-1]
        else:
            bookData += toprint
        toprint = ''

    def newline():
        nonlocal characters_left, lines_left, pixels_left, bookData
        printline()
        if characters_left < 2 or lines_left < 1:
            return newpage()
        characters_left -= 2
        lines_left -= 1
        pixels_left = PIXELS
        bookData += "\\\\n"

    def newpage():
        nonlocal characters_left, lines_left, pixels_left, bookData
        printline()
        characters_left = CHARACTERS
        lines_left = LINES
        pixels_left = PIXELS
        bookData += '"}\',\'{"text":"'    # end page and start new page

    def jokepage():
        nonlocal bookData
        bookData += ('"}\',\'{"text":"'
                     '…and there was more\\\\n'
                     'to say, but the paper\\\\n'
                     '        ran out…\\\\n'
                     '\\\\n'
                     '\\\\n'
                     '        ⌠       ⌠\\\\n'
                     '        `|  THE  |\\\\n'
                     '        `|  END  |\\\\n'
                     '        ⌡`       ⌡\\\\n'
                     '\\\\n'
                     '\\\\n'
                     '\\\\n'
                     '§7§o…and frankly it was\\\\n'
                     'getting boring…§r')
        newpage()

    def finalpage():
        nonlocal bookData
        bookData += ('§8╔══════════╗\\\\n'
                     '║                      `║\\\\n'
                     '║                      `║\\\\n'
                     '║      ᴘᴜʙʟiꜱʜᴇᴅ   .`║\\\\n'
                     '║          ʙʏ         `║\\\\n'
                     '║     §2Ⓟ§8ᴇɴᴅᴇʀᴍᴀɴ  .`║\\\\n'
                     '║                      `║\\\\n'
                     '║           ⁂         `║\\\\n'
                     '║                      `║\\\\n'
                     '║         GDMC       `║\\\\n'
                     f'║         {__year__}       `║\\\\n'
                     '║                      `║\\\\n'
                     '║                      `║\\\\n'
                     '╚══════════╝\\\\n'
                     '"}\']}')

    pages = [page for page in text.split('\f')]
    text = [[[word for word in line.split()] for line in page.split('\n')]
            for page in text.split('\f')]   # convert string to 3D list

    bookData = ("{"
                f'title: "{title}", author: "{author}", '
                f'display:{{Lore:[\'[{{"text":"{description}",'
                f'"color":"{desccolor}"}}]\']}}, pages:[')

    bookData += '\'{"text":"'   # start first page
    for page in pages:
        if pages_left < 1:
            jokepage()
            break
        if page[:3] == '\\\\s':
            print(page[3:])
            bookData += page[3:]
            newpage()
            continue
        else:
            page = [[word for word in line.split()]
                    for line in page.split('\n')]
        for line in page:
            toprint = ""
            for word in line:
                width = fontwidth(word + ' ')
                if width > pixels_left:
                    if width > PIXELS:  # cut word to fit
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
    finalpage()        # end last page (book is complete)
    return bookData


def placeLectern(x, y, z, bookData, facing=None):
    """**Place a lectern with a book in the world**."""
    if facing is None:
        facing = choice(getOptimalDirection(x, y, z))
    gi.placeBlock(x, y, z, f"lectern[facing={facing}, has_book=true]")
    command = (f'data merge block {x} {y} {z} '
               f'{{Book: {{id: "minecraft:written_book", '
               f'Count: 1b, tag: {bookData}'
               '}, Page: 0}')
    response = runCommand(command)
    if not response.isnumeric():
        print(f"{lookup.TCOLORS['orange']}Warning: Server returned error "
              f"upon placing block:\n\t{lookup.TCOLORS['CLR']}{response}")


def placeSign(x, y, z, facing=None, rotation=None,
              text1="", text2="", text3="", text4="",
              wood='oak', wall=False):
    """**Place a written sign in the world**.

    Facing is for wall placement, rotation for ground placement
    If there is no supporting wall the sign will revert to ground placement
    By default the sign will attempt to orient itself to be most legible

    Note: If you are experiencing performance issues provide your own facing
        and rotation values to reduce the required calculations
    """
    if wood not in lookup.WOODS:
        raise ValueError(f"{wood} is not a valid wood type!")

    if facing is not None and facing not in lookup.DIRECTIONS:
        print(f"{facing} is not a valid direction.\n"
              "Working with default behaviour.")
        facing = None
    try:
        if not 0 <= int(rotation) <= 15:
            raise TypeError
    except TypeError:
        if rotation is not None:
            print(f"{rotation} is not a valid rotation.\n"
                  "Working with default behaviour.")
        rotation = None

    if facing is None and rotation is None:
        facing = getOptimalDirection(x, y, z)

    if wall:
        wall = False
        for direction in facing:
            inversion = lookup.INVERTDIRECTION[direction]
            dx, dz = lookup.DIRECTIONTOVECTOR[inversion]
            if getBlock(x + dx, y, z + dz) in lookup.TRANSPARENT:
                break
            wall = True
            gi.placeBlock(
                x, y, z, f"{wood}_wall_sign[facing={choice(facing)}]")

    if not wall:
        if rotation is None:
            reference = {'north': 0, 'east': 4, 'south': 8, 'west': 12}
            if len(facing) == 1:
                rotation = reference[lookup.INVERTDIRECTION[facing[0]]]
            else:
                rotation = 0
                for direction in facing:
                    rotation += reference[lookup.INVERTDIRECTION[direction]]
                rotation //= 2

                if rotation == 6 and 'north' not in facing:
                    rotation = 14
                if rotation % 4 != 2:
                    rotation = reference[facing[0]]
        gi.placeBlock(x, y, z, f"{wood}_sign[rotation={rotation}]")

    data = "{" + f'Text1:\'{{"text":"{text1}"}}\','
    data += f'Text2:\'{{"text":"{text2}"}}\','
    data += f'Text3:\'{{"text":"{text3}"}}\','
    data += f'Text4:\'{{"text":"{text4}"}}\'' + "}"
    runCommand(f"data merge block {x} {y} {z} {data}")


def getOptimalDirection(x, y, z):
    """**Return the least obstructed direction to have something facing**."""
    north = (identifyObtrusiveness(getBlock(x, y, z - 1)), 'north')
    east = (identifyObtrusiveness(getBlock(x + 1, y, z)), 'east')
    south = (identifyObtrusiveness(getBlock(x, y, z + 1)), 'south')
    west = (identifyObtrusiveness(getBlock(x - 1, y, z)), 'west')

    min_obstruction = min(north[0], east[0], south[0], west[0])
    max_obstruction = max(north[0], east[0], south[0], west[0])

    surrounding = [north, east, south, west]

    while surrounding[0][0] != max_obstruction:
        surrounding.append(surrounding.pop(0))

    directions = []
    while len(directions) == 0:
        if min_obstruction == max_obstruction:
            return lookup.DIRECTIONS

        if surrounding[2][0] == min_obstruction:
            directions.append(surrounding[2][1])
        if (surrounding[1][0] == min_obstruction
                and surrounding[3][0] != min_obstruction):
            directions.append(surrounding[1][1])
        elif (surrounding[3][0] == min_obstruction
                and surrounding[1][0] != min_obstruction):
            directions.append(surrounding[3][1])
        elif len(directions) == 0:
            directions.append(surrounding[1][1])
            directions.append(surrounding[3][1])

        min_obstruction += 1

    return directions


def identifyObtrusiveness(blockStr):
    """**Return the percieved obtrusiveness of a given block**.

    Returns a numeric weight from 0 (invisible) to 4 (opaque)
    """
    if blockStr in lookup.INVISIBLE:
        return 0
    if blockStr in lookup.FILTERING:
        return 1
    if blockStr in lookup.UNOBTRUSIVE:
        return 2
    if blockStr in lookup.OBTRUSIVE:
        return 3
    return 4
