"""Provides direct wrappers for the endpoints of the GDMC HTTP interface.

These functions are quite low-level. If possible, it is recommended to use the higher-level
:class:`.Editor` class instead.
However, some GDMC HTTP interface features that this module wraps may not be supported by
``Editor`` yet. You may find this module useful for those.
"""


from __future__ import annotations

import io
import json
import logging
import time
from functools import partial
from typing import Any, Iterable, cast
from urllib.parse import urlparse

import numpy as np
import numpy.typing as npt
import requests
from nbt import nbt
from pyglm.glm import ivec3
from requests.exceptions import ConnectionError as RequestConnectionError

from . import __url__, exceptions
from .block import Block
from .utils import isIterable, withRetries
from .vector_tools import Box, Vec2iLike, Vec3iLike


DEFAULT_HOST = "http://localhost:9000"
"""Default host"""


logger = logging.getLogger(__name__)


def _onRequestRetry(_: Exception, retriesLeft: int) -> None:
    logger.warning(
        "HTTP request failed! I'll retry in a bit (%i retries left).",
        retriesLeft,
    )
    time.sleep(3)


def _request(method: str, url: str, *args: Any, retries: int, **kwargs: Any) -> requests.Response:
    try:
        response = cast("requests.Response", withRetries(partial(requests.request, method, url, *args, **kwargs), RequestConnectionError, retries=retries, onRetry=_onRequestRetry))
    except RequestConnectionError as e:
        u = urlparse(url)
        msg = (
            f"Could not connect to the GDMC HTTP interface at {u.scheme}://{u.netloc}.\n"
            'To use GDPC, you need to use a "backend" that provides the GDMC HTTP interface.\n'
            "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
            f"See {__url__}/README.md for more information."
        )
        raise exceptions.InterfaceConnectionError(msg) from e

    if response.status_code == 500:
        msg = "The GDMC HTTP interface reported an internal server error (500)"
        raise exceptions.InterfaceInternalError(msg)

    return response


def getBlocks(
    position: Vec3iLike,
    size: Vec3iLike | None = None,
    dimension: str | None = None,
    includeState: bool = True,
    includeData: bool = True,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> list[tuple[ivec3, Block]]:
    """Returns the blocks in the specified region.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    Returns a list of (position, block)-tuples.

    For positions outside the vertical world limit, the returned block ID will be "minecraft:void_air".
    """
    url = f"{host}/blocks"
    x, y, z = position
    dx, dy, dz = (None, None, None) if size is None else size
    parameters = {
        "x": x,
        "y": y,
        "z": z,
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "includeState": True if includeState else None,
        "includeData":  True if includeData  else None,
        "dimension": dimension,
    }
    response = _request("GET", url, params=parameters, retries=retries, timeout=timeout)
    blockDicts: list[dict[str, Any]] = response.json()
    return [(ivec3(b["x"], b["y"], b["z"]), Block(b["id"], b.get("state", {}), b.get("data") if b.get("data") != "{}" else None)) for b in blockDicts]


def getBiomes(
    position: Vec3iLike,
    size: Vec3iLike | None = None,
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> list[tuple[ivec3, str]]:
    """Returns the biomes in the specified region.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    Returns a list of (position, biome id)-tuples.

    For positions outside the vertical world limit, an empty string is returned instead of a biome ID.
    """
    url = f"{host}/biomes"
    x, y, z = position
    dx, dy, dz = (None, None, None) if size is None else size
    parameters = {
        "x": x,
        "y": y,
        "z": z,
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "dimension": dimension,
    }
    response = _request("GET", url, params=parameters, retries=retries, timeout=timeout)
    biomeDicts: list[dict[str, Any]] = response.json()
    return [(ivec3(b["x"], b["y"], b["z"]), str(b["id"])) for b in biomeDicts]


def placeBlocks(
    blocks: Iterable[tuple[Vec3iLike, Block]],
    dimension: str | None = None,
    doBlockUpdates: bool = True,
    spawnDrops: bool = False,
    customFlags: str = "",
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> list[tuple[bool, int | str]]:
    """Places blocks in the world.

    Each element of ``blocks`` should be a tuple (position, block). Empty blocks (blocks without an
    id) are not allowed.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    The ``doBlockUpdates``, ``spawnDrops`` and ``customFlags`` parameters control block update
    behavior. See the `GDMC HTTP API documentation
    <https://github.com/Niels-NTG/gdmc_http_interface/blob/master/docs/Endpoints.md#-place-blocks-put-blocks>`_
    for more info.

    Returns a list of ``(success, result)``-tuples, one for each block. Each tuple is set according
    to one of three scenarios:

    1. Block placement succeeded, and the block at the target position was changed. In this case,
       ``success`` is ``True`` and ``result`` is ``1``.
    2. Block placement succeeded, but the block at the target position was not changed (the block
       *already was* what you tried to set it to). In this case, ``success`` is ``True`` and
       ``result`` is ``0``.
    3. Block placement failed. In this case, ``success`` is ``False`` and ``result`` is an error
       message.
    """
    url = f"{host}/blocks"

    if customFlags != "":
        blockUpdateParams = {"customFlags": customFlags}
    else:
        blockUpdateParams = {"doBlockUpdates": doBlockUpdates, "spawnDrops": spawnDrops}

    parameters: dict[str, Any] = {"dimension": dimension}
    parameters.update(blockUpdateParams)

    body = (
        "[" +
        ",".join(
            "{" +
            f'"x":{pos[0]},"y":{pos[1]},"z":{pos[2]},"id":"{block.id}"' +
            (f',"state":{json.dumps(block.states, separators=(",",":"))}' if block.states else "") +
            (f',"data":{repr(block.data)}' if block.data is not None else "") +
            "}"
            for pos, block in blocks
        ) +
        "]"
    )

    response = _request("PUT", url, data=bytes(body, "utf-8"), params=parameters, retries=retries, timeout=timeout)

    return [("message" not in entry, entry.get("message", int(entry["status"]))) for entry in response.json()]


def runCommand(
    command: str,
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> list[tuple[bool, str | None]]:
    """Executes one or multiple Minecraft commands (separated by newlines).

    The leading "/" must be omitted.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    Returns a list of (success, result)-tuples, one for each command. If a command was succesful,
    result is its return value (if any). Otherwise, it is the error message.
    """
    url = f"{host}/command"
    response = _request("POST", url, data=bytes(command, "utf-8"), params={"dimension": dimension}, retries=retries, timeout=timeout)
    return [(bool(entry["status"]), entry.get("message")) for entry in response.json()]


def getBuildArea(
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> Box:
    """Retrieves the build area that was specified with /setbuildarea in-game.

    Raises a :exc:`.BuildAreaNotSetError` if the build area was not specified yet.

    If a build area was specified, result is the box describing the build area.
    """
    response = _request("GET", f"{host}/buildarea", retries=retries, timeout=timeout)

    if not response.ok or response.json() == -1:
        msg = (
            "Failed to get the build area.\n"
            "Make sure to set the build area with /setbuildarea in-game.\n"
            "For example: /setbuildarea ~0 0 ~0 ~128 255 ~128"
        )
        raise exceptions.BuildAreaNotSetError(msg)

    buildAreaJson = response.json()
    fromPoint = ivec3(
        buildAreaJson["xFrom"],
        buildAreaJson["yFrom"],
        buildAreaJson["zFrom"],
    )
    toPoint = ivec3(
        buildAreaJson["xTo"],
        buildAreaJson["yTo"],
        buildAreaJson["zTo"],
    )
    return Box.between(fromPoint, toPoint)


def getChunks(
    position: Vec2iLike,
    size: Vec2iLike | None = None,
    dimension: str | None = None,
    asBytes: bool = False,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> str | bytes:
    """Returns raw chunk data.

    ``position`` specifies the position in chunk coordinates, and ``size`` specifies how many chunks
    to get in each axis (default 1).
    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    If ``asBytes`` is True, returns raw binary data. Otherwise, returns a human-readable
    representation.

    On error, returns the error message instead.
    """
    url = f"{host}/chunks"
    x, z = position
    dx, dz = (None, None) if size is None else size
    parameters = {
        "x": x,
        "z": z,
        "dx": dx,
        "dz": dz,
        "dimension": dimension,
    }
    acceptType = "application/octet-stream" if asBytes else "text/plain"
    response = _request("GET", url, params=parameters, headers={"Accept": acceptType}, retries=retries, timeout=timeout)
    return response.content if asBytes else response.text


def placeStructure(
    structureData: bytes | nbt.NBTFile,
    position: Vec3iLike,
    mirror: Vec2iLike | None = None,
    rotate: int | None = None,
    pivot: Vec3iLike | None = None,
    includeEntities: bool | None = None,
    dimension: str | None = None,
    doBlockUpdates: bool = True,
    spawnDrops: bool = False,
    customFlags: str = "",
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> None:
    """Places a structure defined using the Minecraft structure format in the world.

    ``structureData`` should be a string of bytes in the Minecraft structure file format, the format used by the
    in-game structure blocks. You can extract structures in this format in various ways, such as using the
    ``GET /structure`` endpoint of GDMC-HTTP or the aformentioned in-game structure blocks.
    ``structureData`` can also be an instance of nbt.NBTFile. Using this library has the benefit of providing ways for
    modifying data before placing it in Minecraft.

    See the `GDMC HTTP API documentation <https://github.com/Niels-NTG/gdmc_http_interface/blob/master/docs/Endpoints.md#place-nbt-structure-file-post-structure>`_
    for more information about these parameters.
    """
    if isinstance(structureData, nbt.NBTFile):
        # If data is an instance of NBTFile instead of bytes, write out the bytes representing an NBT file to a buffer.
        outputBuffer = io.BytesIO()
        structureData.write_file(buffer=outputBuffer)
        structureData = outputBuffer.getvalue()
        outputBuffer.close()

    url = f"{host}/structure"
    x, y, z = position
    rotate = (rotate % 4) if rotate else 0
    mirrorArg = None
    if mirror is None:
        mirrorArg = None
    elif mirror[0] and mirror[1]:
        rotate = (rotate + 2) % 4
    elif mirror[0]:
        mirrorArg = "x"
    elif mirror[1]:
        mirrorArg = "z"
    else:
        mirrorArg = None
    pivotX, pivotY, pivotZ = (None, None, None) if pivot is None else pivot
    parameters = {
        "x": x,
        "y": y,
        "z": z,
        "mirror": mirrorArg,
        "rotate": rotate,
        "pivotx": pivotX,
        "pivoty": pivotY,
        "pivotz": pivotZ,
        "dimension": dimension,
        "entities": includeEntities,
    }
    if customFlags != "":
        parameters["customFlags"] = customFlags
    else:
        parameters["doBlockUpdates"] = doBlockUpdates
        parameters["spawnDrops"] = spawnDrops

    response = _request(method="POST", url=url, data=structureData, params=parameters, retries=retries, timeout=timeout)
    return response.json()


def getStructure(
    position: Vec3iLike,
    size: Vec3iLike,
    dimension: str | None = None,
    includeEntities: bool | None = None,
    returnCompressed: bool | None = True,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> bytes:
    """Returns the specified area in the Minecraft structure file format (an NBT byte string).

    The Minecraft structure file format is the format used by the in-game structure blocks. Structures in this format
    are commonly saved in .nbt files, and can be placed using tools such as the ``POST /structure`` endpoint of
    GDMC-HTTP or the aforementioned in-game structure blocks.

    Setting the ``includeEntities`` to True will attach all entities present in the given area at the moment of calling
    getStructure to the resulting data. Meaning that saving a house in a Minecraft village will include the NPC
    living inside it. Note that when placing this structure using GDMC-HTTP, the ``includeEntities`` parameter needs to
    be set to ``True`` for these entities to be placed into the world together with the blocks making up the structure.
    """
    url = f"{host}/structure"
    x, y, z = position
    dx, dy, dz = size
    parameters = {
        "x": x,
        "y": y,
        "z": z,
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "dimension": dimension,
        "entities": includeEntities,
    }
    headers = {"Accept-Encoding": "gzip"} if returnCompressed is True else None

    response = _request(method="GET", url=url, params=parameters, headers=headers, retries=retries, timeout=timeout)
    return response.content


def getHeightmap(
    position: Vec3iLike | None = None,
    size: Vec3iLike | None = None,
    heightmapType: str | None = None,
    blocks: Iterable[str] | None = None,
    yMin: int | None = None,
    yMax: int | None = None,
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> npt.NDArray[np.int_]:
    """Returns heightmap of the given type within the current build area.

    This endpoint supports four of `Minecraft's built-in heightmap types <https://minecraft.wiki/w/Heightmap>`_:

    * ``'WORLD_SURFACE'``: Height of the surface ignoring air blocks.
    * ``'OCEAN_FLOOR'``: Height of the surface ignoring air, water, and lava.
    * ``'MOTION_BLOCKING'``: Height of the surface ignoring blocks that don't have movement collision (air, flowers,
      ferns, etc.), except for water and lava.
    * ``'MOTION_BLOCKING_NO_LEAVES'``: Same as ``'MOTION_BLOCKING'``, but also ignores
      `leaves <https://minecraft.wiki/w/Leaves>`_.

    Additionally, the GDMC-HTTP mod provides two extra heightmap types,
    which can only be retrieved using this endpoint:

    * ``'MOTION_BLOCKING_NO_PLANTS'``: Same as ``'MOTION_BLOCKING_NO_LEAVES'``, but also excludes various biological
      block types. For a full list, refer to the `GDMC-HTTP documentation
      <https://github.com/Niels-NTG/gdmc_http_interface/blob/master/docs/Endpoints.md#heightmap-preset-types>`_.
    * ``'OCEAN_FLOOR_NO_PLANTS'``: Same as ``'OCEAN_FLOOR'``, except it also excludes everything that is part of
      ``'MOTION_BLOCKING_NO_PLANTS'``.

    Instead of a heightmap type, you can also submit a list of block IDs using the ``blocks`` parameter.
    These are the blocks that should be considered "transparent" when the heightmap is calculated.
    **Note:** Air blocks (``'minecraft:air'``, ``'minecraft:cave_air'``) aren't included by default.

    Using the ``yMin`` and ``yMax`` parameters, the lower and/or upper limit of the heightmap calculation can be
    constrained. This can be useful for creating heightmaps of overworld caves or the Nether dimension.
    **Only works if used in conjunction with the** ``blocks`` **parameter.**
    """
    customBlocksQuery = ""
    yBoundsQuery = ""
    if isIterable(blocks):
        customBlocksQuery = ",".join(cast("Iterable[str]", blocks))
        yBoundsQuery = f'{yMin if isinstance(yMin, int) else ""}..{yMax if isinstance(yMax, int) else ""}'
    elif heightmapType is None:
        # Default to heightmap type WORLD_SURFACE if both `heightMapType` and `blocks` parameters aren't set.
        heightmapType = "WORLD_SURFACE"
    parameters: dict[str, Any] = {
        "type": heightmapType,
        "dimension": dimension,
        "blocks": customBlocksQuery,
        "yBounds": yBoundsQuery,
    }
    if position is not None:
        parameters.update({
            "x": position[0],
            "y": position[1],
            "z": position[2],
        })
    if size is not None:
        parameters.update({
            "dx": size[0],
            "dy": size[1],
            "dz": size[2],
        })
    response = _request(method="GET", url=f"{host}/heightmap", params=parameters, retries=retries, timeout=timeout)
    return np.asarray(response.json(), dtype=np.int_)


def placeEntities(
    entities: Iterable[dict[str, str | int]],
    position: Vec3iLike,
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> Any:
    """Place entities (animals, paintings, item frames, etc.).

    Requires list of dicts, each containing the ``id`` string of the entity (for instance, ``'minecraft:cat'``),
    the spawn x, y and z position (can be `relative <https://minecraft.wiki/w/Coordinates#Relative_world_coordinates>`_
    to the ``position`` argument). Optionally, providing the ``data`` attribute with a SNBT-formatted string sets
    non-default properties to the entity.
    """
    parameters: dict[str, Any] = {
        "x": position[0],
        "y": position[1],
        "z": position[2],
        "dimension": dimension,
    }
    body = json.dumps(entities)
    response = _request(method="PUT", url=f"{host}/entities", data=bytes(body, "utf-8"), params=parameters, retries=retries, timeout=timeout)
    return response.json()


def updateEntities(
    entities: Iterable[dict[str, str]],
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> Any:
    """Update specific entities (animals, paintings, item frames, etc.) already present in the world.

    Requires list of dicts, each containing the ``uuid`` string of the entity in the world and ``data`` SNBT-formatted
    string of entity properties that need to be patched.
    """
    parameters: dict[str, Any] = {
        "dimension": dimension,
    }
    body = json.dumps(entities)
    response = _request(method="PATCH", url=f"{host}/entities", data=bytes(body, "utf-8"), params=parameters, retries=retries, timeout=timeout)
    return response.json()


def removeEntities(
    entities: Iterable[str],
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> Any:
    """Remove specific entities (animals, paintings, item frames, etc.) already present in the world.

    Requires list of UUID strings of the entities that need to be removed.
    """
    parameters: dict[str, Any] = {
        "dimension": dimension,
    }
    body = json.dumps(entities)
    response = _request(method="DELETE", url=f"{host}/entities", data=bytes(body, "utf-8"), params=parameters, retries=retries, timeout=timeout)
    return response.json()


def getEntities(
    selector: str | None = None,
    includeData: bool = True,
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> Any:
    """Retrieve data on entities in the world matching the given
    `target selector query <https://minecraft.wiki/w/Target_selectors>`_.
    """
    url = f"{host}/entities"
    parameters = {
        "selector": selector,
        "dimension": dimension,
        "includeData": includeData,
    }
    response = _request(method="GET", url=url, params=parameters, retries=retries, timeout=timeout)
    return response.json()


def getPlayers(
    selector: str | None = None,
    includeData: bool = True,
    dimension: str | None = None,
    retries: int = 0,
    timeout: Any = None,
    host: str = DEFAULT_HOST,
) -> Any:
    """Retrieve data on player entities in the world matching the given
    `target selector query <https://minecraft.wiki/w/Target_selectors>`_.
    """
    url = f"{host}/players"
    parameters = {
        "selector": selector,
        "dimension": dimension,
        "includeData": includeData,
    }
    response = _request(method="GET", url=url, params=parameters, retries=retries, timeout=timeout)
    return response.json()


def getVersion(retries: int = 0, timeout: Any =None, host: str = DEFAULT_HOST) -> str:
    """Returns the Minecraft version as a string."""
    return _request("GET", f"{host}/version", retries=retries, timeout=timeout).text
