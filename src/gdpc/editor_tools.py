"""Provides various Minecraft-related utilities that require an :class:`.Editor`."""


from typing import Optional, Iterable, Set, Tuple, Union, List, Dict, cast

from deprecated import deprecated
import numpy as np
from pyglm.glm import ivec2, ivec3

from .vector_tools import Vec2iLike, Vec3iLike, Box, neighbors3D
from .block import Block
from .block_state_tools import facingToVector
from .minecraft_tools import getObtrusiveness, lecternBlock, positionToInventoryIndex, signBlock
from .editor import Editor


_INVENTORY_SIZE_TO_CONTAINER_BLOCK_IDS: Dict[ivec2, Set[str]] = {
    ivec2(9,3): {
        'minecraft:chest',
        'minecraft:ender_chest',
        'minecraft:trapped_chest',
        'minecraft:barrel',
        'minecraft:red_shulker_box',
        'minecraft:magenta_shulker_box',
        'minecraft:light_gray_shulker_box',
        'minecraft:yellow_shulker_box',
        'minecraft:green_shulker_box',
        'minecraft:white_shulker_box',
        'minecraft:light_blue_shulker_box',
        'minecraft:pink_shulker_box',
        'minecraft:black_shulker_box',
        'minecraft:lime_shulker_box',
        'minecraft:purple_shulker_box',
        'minecraft:gray_shulker_box',
        'minecraft:cyan_shulker_box',
        'minecraft:brown_shulker_box',
        'minecraft:blue_shulker_box',
        'minecraft:shulker_box',
        'minecraft:orange_shulker_box',
    },
    ivec2(3,3): {"minecraft:dispenser", "minecraft:dropper"},
    ivec2(5,1): {"minecraft:hopper", "minecraft:brewing_stand"},
    ivec2(3,1): {'minecraft:blast_furnace', 'minecraft:smoker', 'minecraft:furnace'},
}

_CONTAINER_BLOCK_ID_TO_INVENTORY_SIZE: Dict[str, Vec2iLike] = {}
for size, ids in _INVENTORY_SIZE_TO_CONTAINER_BLOCK_IDS.items():
    for bid in ids:
        _CONTAINER_BLOCK_ID_TO_INVENTORY_SIZE[bid] = size


def centerBuildAreaOnPlayer(editor: Editor, size: Vec3iLike) -> Box:
    """Sets ``editor``'s build area to a box of ``size`` centered on the player, and returns it.\n
    The build area is always in **global coordinates**; ``editor.transform`` is ignored."""
    # -1 to correct for offset from player position
    radius = (ivec3(*size) - 1) // 2
    editor.runCommandGlobal(
        "execute at @p run setbuildarea "
        f"~{-radius.x} ~{-radius.y} ~{-radius.z} ~{radius.x} ~{radius.y} ~{radius.z}")
    return editor.getBuildArea()


def flood_search_3D(
    editor: Editor,
    origin: Vec3iLike,
    boundingBox: Box,
    search_block_ids: Iterable[str],
    diagonal: bool = False,
    depth: int = 256
) -> Set[ivec3]:
    """Return a list of coordinates with blocks that fulfill the search.\n
    Activating caching (:attr:`.Editor.caching`) is *highly* recommended."""
    def flood_search_3D_recursive(point: ivec3, result: Set[ivec3], visited: Set[ivec3], depth_: int):
        if point in visited:
            return

        visited.add(point)

        if cast(str, editor.getBlock(point).id) not in search_block_ids:
            return

        result.add(point)

        for neighbor in neighbors3D(point, boundingBox, diagonal):
            flood_search_3D_recursive(neighbor, result, visited, depth_ - 1)

    result:  Set[ivec3] = set()
    visited: Set[ivec3] = set()
    flood_search_3D_recursive(ivec3(*origin), result, visited, depth)
    return result


def placeSign(
    editor: Editor,
    position: Vec3iLike,
    wood: str = "oak",
    wall: bool = False,
    facing: str = "north",
    rotation: Union[str, int] = "0",
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
    isWaxed: bool = False
) -> None:
    """Places a sign with the specified properties.\n
    If ``wall`` is True, ``facing`` is used. Otherwise, ``rotation`` is used.\n
    See also: :func:`.minecraft_tools.signData`, :func:`.minecraft_tools.signBlock`."""
    if wall:
        rotationArg = "0"
        facingArg = facing
    else:
        facingArg = "north"
        rotationArg = rotation

    editor.placeBlock(position, signBlock(
        wood, wall, facingArg, rotationArg,
        frontLine1, frontLine2, frontLine3, frontLine4, frontColor, frontIsGlowing,
        backLine1,  backLine2,  backLine3,  backLine4,  backColor,  backIsGlowing,
        isWaxed
    ))


def placeLectern(editor: Editor, position: Vec3iLike, facing: str = "north", bookData: Optional[str] = None, page: int = 0) -> None:
    """Place a lectern with the specified properties.\n
    ``bookData`` should be an SNBT string defining a book.
    You can use :func:`.minecraft_tools.bookData` to create such a string.\n
    See also: :func:`.minecraft_tools.lecternData`, :func:`.minecraft_tools.lecternBlock`."""
    editor.placeBlock(position, lecternBlock(facing, bookData, page))


def placeContainerBlock(
    editor: Editor,
    position: Vec3iLike,
    block: Block = Block("minecraft:chest"),
    items: Optional[Iterable[Union[Tuple[Vec2iLike, str], Tuple[Vec2iLike, str, int]]]] = None,
    replace: bool = True
) -> None:
    """Place a container block with the specified items in the world.\n
    ``items`` should be a sequence of (position, item, [amount,])-tuples."""
    if block.id is None:
        raise ValueError(f'"{block.id}" is not a known container block. Make sure you are using its namespaced ID.')

    inventorySize = _CONTAINER_BLOCK_ID_TO_INVENTORY_SIZE.get(block.id)
    if inventorySize is None:
        raise ValueError(f'"{block.id}" is not a known container block. Make sure you are using its namespaced ID.')

    if not replace and editor.getBlock(position).id != block.id:
        return

    editor.placeBlock(position, block)

    if items is None:
        return

    for item in items:
        index = positionToInventoryIndex(item[0], inventorySize)
        if len(item) == 2:
            item = (*item, 1)
        editor.runCommand(f"item replace block ~ ~ ~ container.{index} with {item[1]} {item[2]}", position=position, syncWithBuffer=True)


def setContainerItem(editor: Editor, position: Vec3iLike, itemPosition: Vec2iLike, item: str, amount: int = 1) -> None:
    """Sets the item at ``itemPosition`` in the container block at ``position`` to the item with id ``item``."""
    blockId = cast(str, editor.getBlock(position).id)
    inventorySize = _CONTAINER_BLOCK_ID_TO_INVENTORY_SIZE.get(blockId)
    if inventorySize is None:
        raise ValueError(f'The block at {tuple(position)} is "{blockId}", which is not a known container block.')

    index = positionToInventoryIndex(itemPosition, inventorySize)
    editor.runCommand(f"item replace block ~ ~ ~ container.{index} with {item} {amount}", position=position, syncWithBuffer=True)


@deprecated("Deprecated along with lookup.py. See the documentation for the lookup.py module for the reasons and for alternatives.")
def getOptimalFacingDirection(editor: Editor, pos: Vec3iLike) -> List[str]:
    """
    .. warning::
        :title: Deprecated

        Deprecated along with :mod:`.lookup`. See the warning at the top of
        the `lookup` page for the reasons and for alternatives.

    Returns the least obstructed directions to have something facing (a "facing" block state value).

    Ranks directions by obtrusiveness first, and by obtrusiveness of the opposite direction second.
    """
    directions = ["north", "east", "south", "west"]
    obtrusivenesses = np.array([
        getObtrusiveness(editor.getBlock(ivec3(*pos) + facingToVector(direction)))
        for direction in directions
    ], dtype=np.int_)
    candidates              = np.nonzero(obtrusivenesses == np.min(obtrusivenesses))[0] # pyright: ignore [reportUnknownMemberType]
    oppositeObtrusivenesses = obtrusivenesses[(candidates + 2) % 4]
    winners                 = candidates[oppositeObtrusivenesses == np.max(oppositeObtrusivenesses)] # pyright: ignore [reportUnknownMemberType]
    return [directions[winner] for winner in winners]
