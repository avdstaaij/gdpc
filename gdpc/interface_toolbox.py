"""Provides various small functions for the interface."""


from typing import Optional
from random import choice

from glm import ivec3



from .vector_util import EAST, NORTH, SOUTH, WEST, boxBetween
from .block import Block
from .nbt_util import signNBT
from . import lookup
from .interface import Editor, runCommand
from .toolbox import direction2rotation, identifyObtrusiveness, index2slot


def flood_search_3D(editor: Editor, x, y, z, x1, y1, z1, x2, y2, z2, search_blocks,
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
            if (
                (x + dx, y + dy, z + dz) not in observed and
                boxBetween(ivec3(x1, y1, z1), ivec3(x2, y2, z2)).contains(ivec3(x + dx, y + dy, z + dz))
            ):
                if editor.getBlock(ivec3(x+dx,y+dy,z+dz)) in search_blocks:
                    result, observed = flood_search_3D(x + dx, y + dy, z + dz,
                                                       x1, y1, z1, x2, y2, z2,
                                                       search_blocks,
                                                       result, observed,
                                                       diagonal, vectors,
                                                       depth - 1)
                else:
                    observed.add((x + dx, y + dy, z + dz))
    return result, observed


def placeLectern(editor: Editor, x, y, z, bookData, facing: Optional[str] = None):
    """Place a lectern with a book in the world."""
    if facing is None:
        facing = choice(getOptimalDirection(editor, ivec3(x,y,z)))
    response = editor.placeBlock(
        ivec3(x,y,z),
        Block(
            "lectern",
            facing=facing,
            otherState="has_book=true",
            nbt=f'Book: {{id: "minecraft:written_book", Count: 1b, tag: {bookData}}}, Page: 0'
        )
    )
    if not response.isnumeric():
        print(f"{lookup.TCOLORS['orange']}Warning: Server returned error "
              f"upon placing book in lectern:\n\t{lookup.TCOLORS['CLR']}"
              f"{response}")


def placeInventoryBlock(editor: Editor, x, y, z, block='minecraft:chest', facing=None,
                        items=None, replace=True):
    """Place an inventorised block with any number of items in the world.

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
            facing = choice(getOptimalDirection(editor, ivec3(x,y,z)))
        editor.placeBlock(ivec3(x,y,z), Block(block, facing=facing))
        editor.sendBufferedBlocks()
        editor.awaitBufferFlushes()
    else:
        if block not in editor.getBlock(ivec3(x,y,z)):
            print(f"{lookup.TCOLORS['orange']}Warning: Block at {x} {y} {z} "
                  f"is not of specified type {block}!\n"
                  f"\t{lookup.TCOLORS['CLR']}This may result in "
                  f"incorrectly placed items.")

    # we received a single item
    if 3 <= len(items) <= 4 and isinstance(items[0], int):
        items = [items, ]

    response = '0'
    for item in items:
        slot = index2slot(item[0], item[1], dx, dy)
        if len(item) == 3:
            item = list(item)
            item.append(1)
        globalPosition = editor.transform * ivec3(x,y,z)
        response = runCommand(f"replaceitem block {' '.join(globalPosition)} container.{slot} {item[2]} {item[3]}")

    if not response.isnumeric():
        print(f"{lookup.TCOLORS['orange']}Warning: Server returned error "
              f"upon placing items:\n\t{lookup.TCOLORS['CLR']}{response}")


def placeSign(editor: Editor, x, y, z, facing=None, rotation=None,
              text1="", text2="", text3="", text4="",
              wood='oak', wall=False):
    """Place a written sign in the world.

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
        facing = getOptimalDirection(editor, ivec3(x,y,z))

    nbt = signNBT(text1, text2, text3, text4)

    if wall:
        wall = False
        for direction in facing:
            inversion = lookup.INVERTDIRECTION[direction]
            dx, dz = lookup.DIRECTION2VECTOR[inversion]
            if editor.getBlock(x + dx, y, z + dz) in lookup.TRANSPARENT:
                break
            wall = True
            editor.placeBlock(ivec3(x,y,z), Block(f"{wood}_wall_sign", facing=choice(facing)), nbt=nbt)

    if not wall:
        if rotation is None:
            rotation = direction2rotation(facing)
        editor.placeBlock(ivec3(x,y,z), Block(f"{wood}_sign", otherState=f"rotation={rotation}"), nbt=nbt)


def getOptimalDirection(editor: Editor, pos: ivec3):
    """Return the least obstructed direction to have something facing."""
    north = (identifyObtrusiveness(editor.getBlock(pos + NORTH)), 'north')
    east  = (identifyObtrusiveness(editor.getBlock(pos + EAST )), 'east')
    south = (identifyObtrusiveness(editor.getBlock(pos + SOUTH)), 'south')
    west  = (identifyObtrusiveness(editor.getBlock(pos + WEST )), 'west')

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
