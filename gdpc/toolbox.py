"""Provides various small functions for the average workflow."""


from functools import lru_cache
from itertools import product

import cv2
import numpy as np
from matplotlib import pyplot as plt
from termcolor import colored

from .util import isSequence
from . import lookup
from .lookup import SUPPORTS, VERSIONS
from .worldLoader import WorldSlice


def closest_version(version):
    """Retrieve next-best version code to given version code."""
    if version in VERSIONS:
        return version
    for val in sorted(VERSIONS.keys(), reverse=True):
        if version - val >= 0:
            return val
    return 0


def check_version():
    """Retrieve Minecraft version and check compatibility."""
    wslice = WorldSlice(0, 0, 1, 1)  # single-chunk slice
    current = int(wslice.nbtfile["Chunks"][0]["DataVersion"].value)
    closestname = "Unknown"
    # check compatibility
    if current not in VERSIONS or VERSIONS[SUPPORTS] not in VERSIONS[current]:
        closest = closest_version(current)
        closestname = VERSIONS[closest]
        closestname += " snapshot" if current > closest else ""
        if closest > SUPPORTS:
            print(colored(color="yellow", text=\
                f"WARNING: You are using a newer "
                "version of Minecraft then GDPC supports!\n"
                f"\tSupports: {VERSIONS[SUPPORTS]} "
                f"Detected: {closestname}"
            ))
        elif closest < SUPPORTS:
            print(colored(color="yellow", text=\
                f"WARNING: You are using an older "
                "version of Minecraft then GDPC supports!\n"
                f"\tSupports: {VERSIONS[SUPPORTS]} "
                f"Detected: {closestname}"
            ))
        else:
            raise ValueError(colored(color="red", text=\
                f"Invalid supported version: "
                f"SUPPORTS = {current}!"
            ))
    else:
        closestname = VERSIONS[current]

    return (current, closestname)


def normalizeCoordinates(x1, y1, z1, x2, y2=None, z2=None):
    """Return set of coordinates where (x1, y1, z1) <= (x2, y2, z2)."""
    # if 2D coords are provided reshape to 3D coords
    if y2 is None or z2 is None:
        y1, z1, x2, y2, z2 = 0, y1, z1, 255, x2
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    if z1 > z2:
        z1, z2 = z2, z1
    return x1, y1, z1, x2, y2, z2


def loop2d(a1, b1, a2=None, b2=None):
    """Return all coordinates in a 2D region.

    If only one pair is provided, the loop will yield a1*b1 values.

    If two pairs are provided the loop will yield all results between them inclusively.
    """
    if a2 is None or b2 is None:
        a1, b1, a2, b2 = 0, 0, a1 - 1, b1 - 1

    a1, b1, _, a2, b2, _ = normalizeCoordinates(a1, b1, 0, a2, b2, 0)

    return product(range(a1, a2 + 1), range(b1, b2 + 1))


def loop3d(x1, y1, z1, x2=None, y2=None, z2=None):
    """Return all coordinates in a region of size dx, dy, dz.

    Behaves like loop2d
    """
    if x2 is None or y2 is None or z2 is None:
        x1, y1, z1, x2, y2, z2 = 0, 0, 0, x1 - 1, y1 - 1, z1 - 1

    x1, y1, z1, x2, y2, z2 = normalizeCoordinates(x1, y1, z1, x2, y2, z2)

    return product(range(x1, x2 + 1), range(y1, y2 + 1), range(z1, z2 + 1))


def index2slot(sx, sy, ox, oy):
    """Return slot number of an inventory correlating to a 2d index."""
    if not (0 <= sx < ox and 0 <= sy < oy):
        raise ValueError(f"{sx, sy} is not within (0, 0) and {ox, oy}!")
    return sx + sy * ox


def writeBook(text, title="Chronicle", author="Anonymous",
              description="I wonder what\\'s inside?", desccolor='gold'):
    r"""Return NBT data for a correctly formatted book.

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
        """Return the length of a word based on character width.

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
                     '║                      `║\\\\n'
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


def identifyObtrusiveness(blockStr):
    """Return the percieved obtrusiveness of a given block.

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
    """Visualizes one or multiple numpy arrays."""
    def normalize(array):
        """Normalize the array to contain values from 0 to 1."""
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
    """Return the inverted direction of direcion."""
    if isSequence(direction):
        return [lookup.INVERTDIRECTION[n] for n in direction]
    return lookup.INVERTDIRECTION[direction]


def direction2rotation(direction):
    """Convert a direction to a rotation.

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
    """Convert a direction to a vector."""
    return lookup.DIRECTION2VECTOR[direction]


def axis2vector(axis):
    """Convert an axis to a vector."""
    return lookup.AXIS2VECTOR[axis]
