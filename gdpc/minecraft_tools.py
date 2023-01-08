"""Provides miscellaneous Minecraft-related utility functions."""


from functools import lru_cache

from glm import ivec2
import cv2
import numpy as np
from matplotlib import pyplot as plt
from termcolor import colored

from .vector_tools import Rect
from .block import Block
from . import lookup
from .lookup import SUPPORTS, VERSIONS
from .worldSlice import WorldSlice


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
    wslice = WorldSlice(Rect(size=ivec2(1,1))) # single-chunk slice
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


def positionToInventoryIndex(position: ivec2, inventorySize: ivec2):
    """Returns the flat index of the slot at <position> in an inventory of size <inventorySize>."""
    if not Rect(size=inventorySize).contains(position):
        raise ValueError(f"{position} is not between (0, 0) and {inventorySize}!")
    return position.x + position.y * inventorySize.x


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


def identifyObtrusiveness(block: Block):
    """Return the percieved obtrusiveness of a given block.

    Returns a numeric weight from 0 (invisible) to 4 (opaque)
    """
    blockId = block.id if isinstance(block.id, str) else block.id[0] # TODO: mean?
    if blockId in lookup.INVISIBLE:
        return 0
    if blockId in lookup.FILTERING:
        return 1
    if blockId in lookup.UNOBTRUSIVE:
        return 2
    if blockId in lookup.OBTRUSIVE:
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
