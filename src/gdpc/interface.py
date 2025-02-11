"""Provides direct wrappers for the endpoints of the GDMC HTTP interface.

These functions are quite low-level. It is recommended to use the higher-level
:class:`.editor.Editor` class instead.
"""


from typing import Sequence, Tuple, Optional, List, Dict, Any, Union
from functools import partial
import time
from urllib.parse import urlparse
import logging
import json
import io

from glm import ivec3
from nbt import nbt
import requests
from requests.exceptions import ConnectionError as RequestConnectionError

from . import __url__
from .utils import withRetries
from .vector_tools import Vec2iLike, Vec3iLike, Box
from .block import Block
from . import exceptions


DEFAULT_HOST = "http://localhost:9000"
"""Default host"""


logger = logging.getLogger(__name__)


def _onRequestRetry(e: Exception, retriesLeft: int) -> None:
    logger.warning(
        "HTTP request failed! I'll retry in a bit (%i retries left).",
        retriesLeft
    )
    time.sleep(3)


def _request(method: str, url: str, *args, retries: int, **kwargs) -> requests.Response:
    try:
        response = withRetries(partial(requests.request, method, url, *args, **kwargs), RequestConnectionError, retries=retries, onRetry=_onRequestRetry)
    except RequestConnectionError as e:
        u = urlparse(url)
        raise exceptions.InterfaceConnectionError(
            f"Could not connect to the GDMC HTTP interface at {u.scheme}://{u.netloc}.\n"
             "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
             "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
            f"See {__url__}/README.md for more information."
        ) from e

    if response.status_code == 500:
        raise exceptions.InterfaceInternalError("The GDMC HTTP interface reported an internal server error (500)")

    return response


def getBlocks(position: Vec3iLike, size: Optional[Vec3iLike] = None, dimension: Optional[str] = None, includeState=True, includeData=True, retries=0, timeout=None, host=DEFAULT_HOST) -> List[Tuple[ivec3, Block]]:
    """Returns the blocks in the specified region.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    Returns a list of (position, block)-tuples.

    If a set of coordinates is invalid, the returned block ID will be "minecraft:void_air".
    """
    url = f"{host}/blocks"
    x, y, z = position
    dx, dy, dz = (None, None, None) if size is None else size
    parameters = {
        'x': x,
        'y': y,
        'z': z,
        'dx': dx,
        'dy': dy,
        'dz': dz,
        'includeState': True if includeState else None,
        'includeData':  True if includeData  else None,
        'dimension': dimension
    }
    response = _request("GET", url, params=parameters, retries=retries, timeout=timeout)
    blockDicts: List[Dict[str, Any]] = response.json()
    return [(ivec3(b["x"], b["y"], b["z"]), Block(b["id"], b.get("state", {}), b.get("data") if b.get("data") != "{}" else None)) for b in blockDicts]


def getBiomes(position: Vec3iLike, size: Optional[Vec3iLike] = None, dimension: Optional[str] = None, retries=0, timeout=None, host=DEFAULT_HOST) -> List[Tuple[ivec3, str]]:
    """Returns the biomes in the specified region.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    Returns a list of (position, biome id)-tuples.

    If a set of coordinates is invalid, the returned biome ID will be an empty string.
    """
    url = f"{host}/biomes"
    x, y, z = position
    dx, dy, dz = (None, None, None) if size is None else size
    parameters = {
        'x': x,
        'y': y,
        'z': z,
        'dx': dx,
        'dy': dy,
        'dz': dz,
        'dimension': dimension
    }
    response = _request("GET", url, params=parameters, retries=retries, timeout=timeout)
    biomeDicts: List[Dict[str, Any]] = response.json()
    return [(ivec3(b["x"], b["y"], b["z"]), str(b["id"])) for b in biomeDicts]


def placeBlocks(blocks: Sequence[Tuple[Vec3iLike, Block]], dimension: Optional[str] = None, doBlockUpdates=True, spawnDrops=False, customFlags: str = "", retries=0, timeout=None, host=DEFAULT_HOST) -> List[Tuple[bool, Union[int, str]]]:
    """Places blocks in the world.

    Each element of ``blocks`` should be a tuple (position, block). Empty blocks (blocks without an
    id) are not allowed.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    The ``doBlockUpdates``, ``spawnDrops`` and ``customFlags`` parameters control block update
    behavior. See the GDMC HTTP API documentation for more info.

    Returns a list of (success, result)-tuples, one for each block. If a block placement was
    successful, result will be 1 if the block changed, or 0 otherwise. If a block placement failed,
    result will be the error message.
    """
    url = f"{host}/blocks"

    if customFlags != "":
        blockUpdateParams = {"customFlags": customFlags}
    else:
        blockUpdateParams = {"doBlockUpdates": doBlockUpdates, "spawnDrops": spawnDrops}

    parameters = {"dimension": dimension}
    parameters.update(blockUpdateParams)

    body = (
        "[" +
        ",".join(
            '{' +
            f'"x":{pos[0]},"y":{pos[1]},"z":{pos[2]},"id":"{block.id}"' +
            (f',"state":{json.dumps(block.states, separators=(",",":"))}' if block.states else '') +
            (f',"data":{repr(block.data)}' if block.data is not None else '') +
            '}'
            for pos, block in blocks
        ) +
        "]"
    )

    response = _request("PUT", url, data=bytes(body, "utf-8"), params=parameters, retries=retries, timeout=timeout)

    result: List[Tuple[bool, Union[int, str]]] = [("message" not in entry, entry.get("message", int(entry["status"]))) for entry in response.json()]
    return result


def runCommand(command: str, dimension: Optional[str] = None, retries=0, timeout=None, host=DEFAULT_HOST) -> List[Tuple[bool, Optional[str]]]:
    """Executes one or multiple Minecraft commands (separated by newlines).

    The leading "/" must be omitted.

    ``dimension`` can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

    Returns a list of (success, result)-tuples, one for each command. If a command was succesful,
    result is its return value (if any). Otherwise, it is the error message.
    """
    url = f"{host}/command"
    response = _request("POST", url, data=bytes(command, "utf-8"), params={'dimension': dimension}, retries=retries, timeout=timeout)
    result: List[Tuple[bool, Optional[str]]] = [(bool(entry["status"]), entry.get("message")) for entry in response.json()]
    return result


def getBuildArea(retries=0, timeout=None, host=DEFAULT_HOST) -> Box:
    """Retrieves the build area that was specified with /setbuildarea in-game.

    Raises a :exc:`.BuildAreaNotSetError` if the build area was not specified yet.

    If a build area was specified, result is the box describing the build area.
    """
    response = _request("GET", f"{host}/buildarea", retries=retries, timeout=timeout)

    if not response.ok or response.json() == -1:
        raise exceptions.BuildAreaNotSetError(
            "Failed to get the build area.\n"
            "Make sure to set the build area with /setbuildarea in-game.\n"
            "For example: /setbuildarea ~0 0 ~0 ~128 255 ~128"
        )

    buildAreaJson = response.json()
    fromPoint = ivec3(
        buildAreaJson["xFrom"],
        buildAreaJson["yFrom"],
        buildAreaJson["zFrom"]
    )
    toPoint = ivec3(
        buildAreaJson["xTo"],
        buildAreaJson["yTo"],
        buildAreaJson["zTo"]
    )
    return Box.between(fromPoint, toPoint)


def getChunks(position: Vec2iLike, size: Optional[Vec2iLike] = None, dimension: Optional[str] = None, asBytes=False, retries=0, timeout=None, host=DEFAULT_HOST) -> Union[str, bytes]:
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


def placeStructure(structureData: Union[bytes, nbt.NBTFile], position: Vec3iLike, mirror: Optional[Vec2iLike] = None, rotate: Optional[int] = None, pivot: Optional[Vec3iLike] = None, includeEntities: Optional[bool] = None, dimension: Optional[str] = None, doBlockUpdates=True, spawnDrops=False, customFlags: str = "", retries=0, timeout=None, host=DEFAULT_HOST) -> None:
    """Places a structure defined using the Minecraft structure format in the world.

    ``structureData`` should be a string of bytes in the Minecraft structure file format, the format used by the
    in-game structure blocks. You can extract structures in this format in various ways, such as using the
    GET /structure endpoint of GDMC-HTTP or the aformentioned in-game structure blocks.
    ``structureData`` can also be an instance of nbt.NBTFile. Using this library has the benefit of providing ways for
    modifying data before placing it in Minecraft.

    See the GDMC HTTP API documentation for more information about these parameters:
    https://github.com/Niels-NTG/gdmc_http_interface/blob/master/docs/Endpoints.md#place-nbt-structure-file-post-structure
    """
    if isinstance(structureData, nbt.NBTFile):
        # If data is an instance of NBTFile instead of bytes, write out the bytes representing an NBT file to a buffer.
        outputBuffer = io.BytesIO()
        structureData.write_file(buffer=outputBuffer)
        structureData = outputBuffer.getvalue()
        outputBuffer.close()

    url = f"{host}/structure"
    x, y, z = position
    rotate = (rotate % 4) if rotate else None
    mirrorArg = None
    if mirror is None:
        mirrorArg = None
    elif mirror[0] and mirror[1]:
        rotate = (rotate + 2) % 4
    elif mirror[0]:
        mirrorArg = 'x'
    elif mirror[1]:
        mirrorArg = 'z'
    else:
        mirrorArg = None
    pivotX, pivotY, pivotZ = (None, None, None) if pivot is None else pivot
    parameters = {
        'x': x,
        'y': y,
        'z': z,
        'mirror': mirrorArg,
        'rotate': rotate,
        'pivotx': pivotX,
        'pivoty': pivotY,
        'pivotz': pivotZ,
        'dimension': dimension,
        'entities': includeEntities,
    }
    if customFlags != "":
        parameters['customFlags'] = customFlags
    else:
        parameters['doBlockUpdates'] = doBlockUpdates
        parameters['spawnDrops'] = spawnDrops

    response = _request(method="POST", url=url, data=structureData, params=parameters, retries=retries, timeout=timeout)
    return response.json()


def getStructure(position: Vec3iLike, size: Vec3iLike, dimension: Optional[str] = None, includeEntities: Optional[bool] = None, returnCompressed: Optional[bool] = True, retries=0, timeout=None, host=DEFAULT_HOST) -> bytes:
    """Returns the specified area in the Minecraft structure file format (an NBT byte string).

    The Minecraft structure file format is the format used by the in-game structure blocks. Structures in this format
    are commonly saved in .nbt files, and can be placed using tools such as the POST /structure endpoint of GDMC-HTTP
    or the aforementioned in-game structure blocks.

    Setting the ``includeEntities`` to True will attach all entities present in the given area at the moment of calling
    getStructure to the resulting data. Meaning that saving a house in a Minecraft village will include the NPC
    living inside it. Note that when placing this structure using GDMC-HTTP, the includeEntities parameter needs to
    be set to True for these entities to be placed into the world together with the blocks making up the structure.
    """
    url = f"{host}/structure"
    x, y, z = position
    dx, dy, dz = size
    parameters = {
        'x': x,
        'y': y,
        'z': z,
        'dx': dx,
        'dy': dy,
        'dz': dz,
        'dimension': dimension,
        'entities': includeEntities,
    }
    headers = {'Accept-Encoding': 'gzip'} if returnCompressed is True else None

    response = _request(method="GET", url=url, params=parameters, headers=headers, retries=retries, timeout=timeout)
    return response.content


def getEntities(selector: Optional[str] = None, includeData: bool = True, dimension: Optional[str] = None, retries=0, timeout=None, host=DEFAULT_HOST) -> Any:
    url = f'{host}/entities'
    parameters = {
        'selector': selector,
        'dimension': dimension,
        'includeData': includeData,
    }
    response = _request(method='GET', url=url, params=parameters, retries=retries, timeout=timeout)
    return response.json()


def getPlayers(selector: Optional[str] = None, includeData: bool = True, dimension: Optional[str] = None, retries=0, timeout=None, host=DEFAULT_HOST) -> Any:
    url = f'{host}/players'
    parameters = {
        'selector': selector,
        'dimension': dimension,
        'includeData': includeData,
    }
    response = _request(method='GET', url=url, params=parameters, retries=retries, timeout=timeout)
    return response.json()


def getVersion(retries=0, timeout=None, host=DEFAULT_HOST) -> str:
    """Returns the Minecraft version as a string."""
    return _request("GET", f"{host}/version", retries=retries, timeout=timeout).text
