"""Provides various small functions for the interface."""


from typing import Optional, Iterable, Set
from random import choice

from glm import ivec3
from termcolor import colored

from .util import eprint
from .vector_util import EAST, NORTH, SOUTH, WEST, Box, boxBetween, neighbors3D
from .block import Block
from .block_data_util import signData
from . import lookup
from .interface import Editor, runCommand
from .toolbox import direction2rotation, identifyObtrusiveness, index2slot


def flood_search_3D(
    editor: Editor,
    origin: ivec3,
    boundingBox: Box,
    search_block_ids: Iterable[str],
    diagonal=False,
    depth=256
):
    """Return a list of coordinates with blocks that fulfill the search.

    Activating caching is *highly* recommended.
    """
    def flood_search_3D_recursive(point: ivec3, result: Set[ivec3], visited: Set[ivec3], depth_: int):
        if point in visited:
            return

        visited.add(point)

        if editor.getBlock(point) not in search_block_ids:
            return

        result.add(point)

        for point in neighbors3D(point, boundingBox, diagonal):
            flood_search_3D_recursive(point, result, visited, depth_ - 1)

    result:  Set[ivec3] = set()
    visited: Set[ivec3] = set()
    flood_search_3D_recursive(origin, result, visited, depth)
    return result


def placeLectern(editor: Editor, position: ivec3, bookData: str, facing: Optional[str] = None):
    """Place a lectern with a book in the world."""
    if facing is None:
        facing = choice(getOptimalDirection(editor, position))
    editor.placeBlock(
        position,
        Block(
            "lectern", {"facing": facing, "has_book": "true"},
            data=f'Book: {{id: "minecraft:written_book", Count: 1b, tag: {bookData}}}, Page: 0'
        )
    )


def placeInventoryBlock(
    editor: Editor,
    position: ivec3,
    block='minecraft:chest',
    facing=None,
    items=None,
    replace=True
):
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
            facing = choice(getOptimalDirection(editor, position))
        editor.placeBlock(position, Block(block, {"facing": facing}))
        editor.sendBufferedBlocks()
        editor.awaitBufferFlushes()
    else:
        if block not in editor.getBlock(position):
            eprint(colored(color="orange", text=\
                f"Warning: Block at {position.x} {position.y} {position.z} "
                f"is not of specified type {block}!\n"
                f"This may result in "
                f"incorrectly placed items."
            ))

    # we received a single item
    if 3 <= len(items) <= 4 and isinstance(items[0], int):
        items = [items, ]

    for item in items:
        slot = index2slot(item[0], item[1], dx, dy)
        if len(item) == 3:
            item = list(item)
            item.append(1)
        globalPosition = editor.transform * ivec3(x,y,z)
        runCommand(f"replaceitem block {' '.join(globalPosition)} container.{slot} {item[2]} {item[3]}")


def placeSign(
    editor: Editor,
    position: ivec3,
    facing: Optional[str] = None,
    rotation: Optional[str] = None,
    text1="", text2="", text3="", text4="",
    wood='oak',
    wall=False
):
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
        eprint(f"{facing} is not a valid direction.\n"
              "Working with default behaviour.")
        facing = None
    try:
        if not 0 <= int(rotation) <= 15:
            raise TypeError
    except TypeError:
        if rotation is not None:
            eprint(f"{rotation} is not a valid rotation.\n"
                  "Working with default behaviour.")
        rotation = None

    if facing is None and rotation is None:
        facing = getOptimalDirection(editor, position)

    data = signData(text1, text2, text3, text4)

    if wall:
        wall = False
        for direction in facing:
            inversion = lookup.INVERTDIRECTION[direction]
            dx, _, dz = lookup.DIRECTION2VECTOR[inversion]
            if editor.getBlock(position + ivec3(dx, 0, dz)) in lookup.TRANSPARENT:
                break
            wall = True
            editor.placeBlock(position, Block(f"{wood}_wall_sign", {"facing": choice(facing)}, data=data))

    if not wall:
        if rotation is None:
            rotation = direction2rotation(facing)
        editor.placeBlock(ivec3(x,y,z), Block(f"{wood}_sign", {"rotation": str(rotation)}, data=data))


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
