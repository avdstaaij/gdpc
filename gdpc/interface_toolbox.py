"""Provides various small functions for the interface."""


from typing import Optional, Iterable, Set, Tuple, Union
from random import choice

from glm import ivec2, ivec3
from termcolor import colored

from .util import eprint
from .vector_util import EAST, NORTH, SOUTH, WEST, Box, neighbors3D
from .block import Block
from gdpc.block_state_util import FACING_VALUES, facingToRotation, facingToVector, invertFacing
from .block_data_util import signData
from . import lookup
from .interface import Editor, runCommand
from .toolbox import identifyObtrusiveness, positionToInventoryIndex


def flood_search_3D(
    editor: Editor,
    origin: ivec3,
    boundingBox: Box,
    search_block_ids: Iterable[str],
    diagonal=False,
    depth=256
):
    """Return a list of coordinates with blocks that fulfill the search.\n
    Activating caching is *highly* recommended."""
    def flood_search_3D_recursive(point: ivec3, result: Set[ivec3], visited: Set[ivec3], depth_: int):
        if point in visited:
            return

        visited.add(point)

        if editor.getBlock(point) not in search_block_ids:
            return

        result.add(point)

        for neighbor in neighbors3D(point, boundingBox, diagonal):
            flood_search_3D_recursive(neighbor, result, visited, depth_ - 1)

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
    block: Block = Block("minecraft:chest"),
    items: Optional[Iterable[Union[Tuple[ivec2, str], Tuple[ivec2, str, int]]]] = None,
    replace=True
):
    """Place a container block with the specified items in the world.\n
    Items should be a sequence of (position, item, [amount,])-tuples."""
    if block.id not in lookup.CONTAINER_BLOCK_TO_INVENTORY_SIZE:
        raise ValueError(f"The inventory size for {block} is not available. Make sure you are using its namespaced ID.")
    inventorySize = lookup.CONTAINER_BLOCK_TO_INVENTORY_SIZE[block]

    if not replace and editor.getBlock(position).id != block.id:
        return

    editor.placeBlock(position, block)

    if items is None:
        return

    for item in items:
        index = positionToInventoryIndex(item[0], inventorySize)
        if len(item) == 3:
            item = list(item)
            item.append(1)
        globalPosition = editor.transform * position
        editor.runCommand(f"replaceitem block {' '.join(globalPosition)} container.{index} {item[2]} {item[3]}")


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

    if facing is not None and facing not in FACING_VALUES:
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
            inversion = invertFacing(direction)
            dx, _, dz = facingToVector(inversion)
            if editor.getBlock(position + ivec3(dx, 0, dz)) in lookup.TRANSPARENT:
                break
            wall = True
            editor.placeBlock(position, Block(f"{wood}_wall_sign", {"facing": choice(facing)}, data=data))

    if not wall:
        if rotation is None:
            rotation = facingToRotation(facing if isinstance(facing, str) else choice(facing))
        editor.placeBlock(position, Block(f"{wood}_sign", {"rotation": str(rotation)}, data=data))


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
            return ["north", "east", "south", "west"]

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
