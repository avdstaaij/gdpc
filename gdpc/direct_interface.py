"""Provides direct wrappers for the endpoints of the Minecraft HTTP interface.

This file contains various functions that map directly onto the endpoints of the Minecraft
HTTP interface backend.
It is recommended to use the higher-level `interface.py` instead.
"""


from typing import Union, Tuple, Optional

import requests
from requests.exceptions import ConnectionError as RequestConnectionError

from .util import eprint


HOST = "http://localhost:9000"


# TODO: deduplicate retrying logic

def _get(*args, retries: int, **kwargs):
    retriesLeft = retries
    while True:
        try:
            return requests.get(*args, **kwargs) # pylint: disable=missing-timeout
        except RequestConnectionError as e:
            if retriesLeft == 0:
                raise e
            eprint(f"HTTP request failed! Retrying {retriesLeft} more times.")
            retriesLeft -= 1


def _put(*args, retries: int, **kwargs):
    retriesLeft = retries
    while True:
        try:
            return requests.put(*args, **kwargs) # pylint: disable=missing-timeout
        except RequestConnectionError as e:
            if retriesLeft == 0:
                raise e
            eprint(f"HTTP request failed! Retrying {retriesLeft} more times.")
            retriesLeft -= 1


def _post(*args, retries: int, **kwargs):
    retriesLeft = retries
    while True:
        try:
            return requests.post(*args, **kwargs) # pylint: disable=missing-timeout
        except RequestConnectionError as e:
            if retriesLeft == 0:
                raise e
            eprint(f"HTTP request failed! Retrying {retriesLeft} more times.")
            retriesLeft -= 1


# TODO: add includeState option
def getBlock(x: int, y: int, z: int, retries=5, timeout=None):
    """Returns the namespaced ID of the block at the given coordinates.

    If the given coordinates are invalid, returns "minecraft:void_air".
    """
    url = f"{HOST}/blocks?x={x}&y={y}&z={z}"
    return _get(url, retries=retries, timeout=timeout).text


def placeBlock(x: int, y: int, z: int, blockStr: str, doBlockUpdates=True, spawnDrops=False, customFlags: str = "", retries=5, timeout=None):
    """Places one or multiple blocks in the world.

    Each line of <blockStr> should describe a single block placement, using one of the
    following formats:
    1. <block>
    2. <position> <block>

    Placeholder explanation:
    - <block>: The (optionally namespaced) id of a block, optionally with block state info.
      NBT data is not supported. Examples: "minecraft:oak_log[axis=y]", "stone".
    - <position>: The (x,y,z) coordinates where to place the block. Coordinates can be given using
      tilde notation, in which case they are seen as relative to this function's <x>,<y>,<z>
      parameters. Examples: "1 2 3", "~4 ~5 ~6"

    The <doBlockUpdates>, <spawnDrops> and <customFlags> parameters control block update behavior.
    See the API documentation for more info.

    Returns a string with one line for each block placement. If the block placement was successful,
    the return line is "1" if the block changed, or "0" otherwise. If the placement failed, it is
    the error message.
    """
    if customFlags != "":
        blockUpdateQueryParam = f"customFlags={customFlags}"
    else:
        blockUpdateQueryParam = f"doBlockUpdates={doBlockUpdates}&spawnDrops={spawnDrops}"

    url = (f"{HOST}/blocks?x={x}&y={y}&z={z}&{blockUpdateQueryParam}")
    return _put(url, blockStr, retries=retries, timeout=timeout).text


def runCommand(command: str, retries=5, timeout=None):
    """Executes one or multiple Minecraft commands (separated by newlines).

    The leading "/" must be omitted.

    Returns a string with one line for each command. If the command was successful, the return line
    is its return value. Otherwise, it is the error message.
    """
    url = f"{HOST}/command"
    return _post(url, bytes(command, "utf-8"), retries=retries, timeout=timeout).text


def getBuildArea(retries=5, timeout=None) -> Tuple[bool, Union[Tuple[int,int,int,int,int,int],str]]:
    """Retrieves the build area that was specified with /setbuildarea in-game.

    Fails if the build area was not specified yet.

    Returns (success, result).
    If a build area was specified, result is a 6-tuple (xFrom, yFrom, zFrom, xTo, yTo, zTo).
    Otherwise, result is the error message string.
    """
    response = _get(f"{HOST}/buildarea", retries=retries, timeout=timeout)

    if not response.ok or response.json() == -1:
        return False, response.text

    buildAreaJson = response.json()
    x1 = buildAreaJson["xFrom"]
    y1 = buildAreaJson["yFrom"]
    z1 = buildAreaJson["zFrom"]
    x2 = buildAreaJson["xTo"]
    y2 = buildAreaJson["yTo"]
    z2 = buildAreaJson["zTo"]
    return True, (x1, y1, z1, x2, y2, z2)


def getChunks(x: int, z: int, dx: int = 1, dz: int = 1, asBytes=False, retries=5, timeout=None):
    """Returns raw chunk data.

    <x> and <z> specify the position in chunk coordinates, and <dx> and <dz> specify how many
    chunks to get.

    If <asBytes> is True, returns raw binary data. Otherwise, returns a human-readable
    representation.

    On error, returns the error message instead.
    """
    url = f"{HOST}/chunks?x={x}&z={z}&dx={dx}&dz={dz}"
    acceptType = "application/octet-stream" if asBytes else "text/raw"
    response = _get(url, headers={"Accept": acceptType}, retries=retries, timeout=timeout)
    if response.status_code >= 400:
        eprint(f"Error: {response.text}")

    return response.content if asBytes else response.text
