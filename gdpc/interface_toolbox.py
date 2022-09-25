#! /usr/bin/python3
"""### Provides various small functions for the interface."""

from datetime import datetime as date
from random import choice

from . import lookup
from .interface import checkOutOfBounds, getBlock
from .interface import globalinterface as gi
from .interface import runCommand
from .toolbox import direction2rotation, identifyObtrusiveness, index2slot

__all__ = []

__author__ = "Blinkenlights"
__version__ = "v5.1"
__year__ = date.now().year


def flood_search_3D(x, y, z, x1, y1, z1, x2, y2, z2, search_blocks,
                    result=None, observed=None, diagonal=False,
                    vectors=None, depth=256):
    """Return a list of coordinates with blocks that fulfil the search.

    Activating caching is *highly* recommended.
    """
    result = set() if result is None else result
    observed = set() if observed is None else observed
    result.add((x, y, z))
    observed.add((x, y, z))
    if vectors is None:
        vectors = lookup.VECTORS
        if diagonal:
            vectors += lookup.DIAGONALVECTORS

    # prevent RecursionError by limiting recursion depth
    if depth > 0:
        for dx, dy, dz in vectors:
            if ((x + dx, y + dy, z + dz) not in observed
                and not checkOutOfBounds(x + dx, y + dy, z + dz, x1, y1, z1,
                                         x2, y2, z2, warn=False)):
                if getBlock(x + dx, y + dy, z + dz) in search_blocks:
                    result, observed = flood_search_3D(x + dx, y + dy, z + dz,
                                                       x1, y1, z1, x2, y2, z2,
                                                       search_blocks,
                                                       result, observed,
                                                       diagonal, vectors,
                                                       depth - 1)
                else:
                    observed.add((x + dx, y + dy, z + dz))
    return result, observed


def placeLectern(x, y, z, bookData, facing=None, interface=gi):
    """**Place a lectern with a book in the world**."""
    if facing is None:
        facing = choice(getOptimalDirection(x, y, z))
    interface.placeBlock(x, y, z, f"lectern[facing={facing}, has_book=true]")
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
                        items=None, replace=True, interface=gi):
    """**Place an inventorised block with any number of items in the world**.

    Items is expected to be a sequence of (x, y, item[, amount])
        or a sequence of such sequences e.g. ((x, y, item), (x, y, item), ...)
    """
    items = [] if items is None else items
    if block not in lookup.INVENTORYLOOKUP:
        raise ValueError(f"The inventory for {block} is not available.\n"
                         "Make sure you are using the namespaced ID.")
    dx, dy = lookup.INVENTORYLOOKUP[block]
    if replace:
        if facing is None:
            facing = choice(getOptimalDirection(x, y, z))
        interface.placeBlock(x, y, z, f"{block}[facing={facing}]")
    else:
        if block not in gi.getBlock(x, y, z):
            print(f"{lookup.TCOLORS['orange']}Warning: Block at {x} {y} {z} "
                  f"is not of specified type {block}!\n"
                  f"\t{lookup.TCOLORS['CLR']}This may result in "
                  f"incorrectly placed items.")

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
              wood='oak', wall=False, interface=gi):
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
            interface.placeBlock(
                x, y, z, f"{wood}_wall_sign[facing={choice(facing)}]")

    if not wall:
        if rotation is None:
            rotation = direction2rotation(facing)
        interface.placeBlock(x, y, z, f"{wood}_sign[rotation={rotation}]")

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
            return lookup.DIRECTIONS[2:]

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
