#! /usr/bin/python3
"""### Provides various small functions for the average workflow."""

__all__ = ['isSequence', 'normalizeCoordinates', 'loop2d', 'loop3d',
           'writeBook', 'placeLectern', 'placeInventoryBlock', 'placeSign',
           'getOptimalDirection', 'visualizeHeightmap',
           'invertDirection', 'direction2rotation', 'direction2vector',
           'axis2vector']
__version__ = 'v4.3_dev'
__year__ = '2021'
__author__ = 'Blinkenlights'

from functools import lru_cache
from itertools import product
from random import choice

import cv2
import lookup
import numpy as np
from interface import getBlock
from interface import globalinterface as gi
from interface import runCommand
from matplotlib import pyplot as plt


def isSequence(sequence):
    """**Determine whether sequence is a sequence**."""
    try:
        sequence[0:-1]
        return True
    except TypeError:
        return False


def normalizeCoordinates(x1, y1, z1, x2, y2=None, z2=None):
    """**Return set of coordinates where (x1, y1, z1) <= (x2, y2, z2)**."""
    # if 2D coords are provided reshape to 3D coords
    if y2 is None or z2 is None:
        x1, y1, z1, x2, y2, z2 = x1, 0, y1, z1, 255, x2
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    if z1 > z2:
        z1, z2 = z2, z1
    return x1, y1, z1, x2, y2, z2


def loop2d(a1, b1, a2=None, b2=None):
    """**Return all coordinates in a 2D region**.

    If only one pair is provided, the loop will yield a1*b1 values
    If two pairs are provided the loop will yield all results between them
        inclusively
    """
    if a2 is None or b2 is None:
        a1, b1, a2, b2 = 0, 0, a1 - 1, b1 - 1

    a1, b1, _, a2, b2, _ = normalizeCoordinates(a1, b1, 0, a2, b2, 0)

    return product(range(a1, a2 + 1), range(b1, b2 + 1))


def loop3d(x1, y1, z1, x2=None, y2=None, z2=None):
    """**Return all coordinates in a region of size dx, dy, dz**.

    Behaves like loop2d
    """
    if x2 is None or y2 is None or z2 is None:
        x1, y1, z1, x2, y2, z2 = 0, 0, 0, x1 - 1, y1 - 1, z1 - 1

    x1, y1, z1, x2, y2, z2 = normalizeCoordinates(x1, y1, z1, x2, y2, z2)

    return product(range(x1, x2 + 1), range(y1, y2 + 1), range(z1, z2 + 1))


def index2slot(sx, sy, ox, oy):
    """**Return slot number of an inventory correlating to a 2d index**."""
    if not (0 <= sx < ox and 0 <= sy < oy):
        raise ValueError(f"{sx, sy} is not within (0, 0) and {ox, oy}!")
    return sx + sy * ox


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

    - `\\\\s`: When at start of page, print page as string directly
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

    @lru_cache()
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
              f"upon placing book in lectern:\n\t{lookup.TCOLORS['CLR']}"
              f"{response}")


def placeInventoryBlock(x, y, z, block='minecraft:chest', facing=None,
                        items=[]):
    """**Place an invetorized block with any number of items in the world**.

    Items is expected to be a sequence of (x, y, item[, amount])
        or a sequence of such sequences e.g. ((x, y, item), (x, y, item), ...)
    """
    if block not in lookup.INVENTORYLOOKUP:
        raise ValueError(f"The inventory for {block} is not available.\n"
                         "Make sure you are using the namespaced ID.")
    dx, dy = lookup.INVENTORYLOOKUP[block]
    if facing is None:
        facing = choice(getOptimalDirection(x, y, z))
    gi.placeBlock(x, y, z, f"{block}[facing={facing}]")

    # we received a single item
    if 3 <= len(items) <= 4 and type(items[0]) == int:
        items = [items, ]

    response = '0'
    for item in items:
        slot = index2slot(item[0], item[1], dx, dy)
        if len(item) == 3:
            item = list(item)
            item.append(1)
        response = runCommand(f"replaceitem block {x} {y} {z} "
                              f"container.{slot} {item[2]} {item[3]}")

    if not response.isnumeric():
        print(f"{lookup.TCOLORS['orange']}Warning: Server returned error "
              f"upon placing items:\n\t{lookup.TCOLORS['CLR']}{response}")


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
            dx, dz = lookup.DIRECTION2VECTOR[inversion]
            if getBlock(x + dx, y, z + dz) in lookup.TRANSPARENT:
                break
            wall = True
            gi.placeBlock(
                x, y, z, f"{wood}_wall_sign[facing={choice(facing)}]")

    if not wall:
        if rotation is None:
            rotation = direction2rotation(facing)
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


def visualizeHeightmap(*arrays, title=None, autonormalize=True):
    """**Visualizes one or multiple numpy arrays**."""
    def normalize(array):
        """**Normalize the array to contain values from 0 to 1**."""
        return (array - array.min()) / (array.max() - array.min())

    for array in arrays:
        if autonormalize:
            array = (normalize(array) * 255).astype(np.uint8)

        plt.figure()
        if title:
            plt.title(title)
        plt_image = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        plt.imshow(plt_image)
    plt.show()


# ========================================================= converters
# The 'data types' commonly used in this package are:
#
# axis: 'x', 'y', 'z'
# direction: 'up', 'down', 'north', 'south', 'east', 'west'
# rotation: 0 - 15 (22.5° clockwise turns starting at north)
# vector: any multiple of (1, 1, 1) e.g. (0, 1, -4)
# =========================================================


def invertDirection(direction):
    """**Return the inverted direction of direcion**."""
    if isSequence(direction):
        return [lookup.INVERTDIRECTION[n] for n in direction]
    return lookup.INVERTDIRECTION[direction]


def direction2rotation(direction):
    """**Convert a direction to a rotation**.

    If a sequence is provided, the average is returned.
    """
    reference = {'north': 0, 'east': 4, 'south': 8, 'west': 12}
    if len(direction) == 1:
        rotation = reference[lookup.INVERTDIRECTION[direction[0]]]
    else:
        rotation = 0
        for direction in direction:
            rotation += reference[lookup.INVERTDIRECTION[direction]]
        rotation //= 2

        if rotation == 6 and 'north' not in direction:
            rotation = 14
        if rotation % 4 != 2:
            rotation = reference[direction[0]]
    return rotation


def direction2vector(direction):
    """**Convert a direction to a vector**."""
    return lookup.DIRECTION2VECTOR[direction]


def axis2vector(axis):
    """**Convert an axis to a vector**."""
    return lookup.AXIS2VECTOR[axis]
