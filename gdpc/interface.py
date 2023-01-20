"""Provides the Interface class, which contains direct wrappers for the endpoints of the
GDMC HTTP interface.\n

It is recommended to use the higher-level `editor.Editor` class instead.
"""


from typing import Sequence, Union, Tuple, Optional, List, Dict, Any
from functools import partial
import time

from glm import ivec2, ivec3
import requests
from requests.exceptions import ConnectionError as RequestConnectionError
from termcolor import colored

from .utility import eprint, withRetries
from .vector_tools import Box
from .block import Block


def _onRequestRetry(e: Exception, retriesLeft: int):
    eprint(colored(color="yellow", text=\
        "HTTP request failed! Is Minecraft running? If so, try reducing your render distance.\n"
        f"Error: {e}"
        f"I'll retry in a bit ({retriesLeft} retries left).\n"
    ))
    time.sleep(3)


def _get(*args, retries: int, **kwargs):
    return withRetries(partial(requests.get, *args, **kwargs), retries=retries, onRetry=_onRequestRetry)

def _put(*args, retries: int, **kwargs):
    return withRetries(partial(requests.put, *args, **kwargs), retries=retries, onRetry=_onRequestRetry)

def _post(*args, retries: int, **kwargs):
    return withRetries(partial(requests.post, *args, **kwargs), retries=retries, onRetry=_onRequestRetry)


class Interface:
    """Provides wrappers for the endpoints of the GDMC HTTP interface.\n
    It is recommended to use the higher-level `editor.Editor` class instead."""

    def __init__(self, host: str = "http://localhost:9000"):
        self.host = host


    def getBlocks(self, position: ivec3, size: Optional[ivec3] = None, dimension: Optional[str] = None, includeState=False, includeData=False, retries=5, timeout=None):
        """Returns the blocks in the specified region.

        <dimension> can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

        Returns a list of (position, block)-tuples.

        If a set of coordinates is invalid, the returned block ID will be "minecraft:void_air".
        """
        url = f"{self.host}/blocks"
        dx, dy, dz = (None, None, None) if size is None else size
        parameters = {
            'x': position.x,
            'y': position.y,
            'z': position.z,
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'includeState': True if includeState else None,
            'includeData':  True if includeData  else None,
            'dimension': dimension
        }
        response = _get(url, params=parameters, headers={"accept": "application/json"}, retries=retries, timeout=timeout)
        blockDicts: List[Dict[str, Any]] = response.json()
        # TODO: deal with b.get("data")
        if includeData:
            raise NotImplementedError("includeData is still a work-in-progress.")
        return [(ivec3(b["x"], b["y"], b["z"]), Block(b["id"], b.get("state", {}))) for b in blockDicts]


    def placeBlocks(self, blocks: Sequence[Tuple[ivec3, Block]], dimension: Optional[str] = None, doBlockUpdates=True, spawnDrops=False, customFlags: str = "", retries=5, timeout=None):
        """Places blocks in the world.

        Each element of <blocks> should be a tuple (position, block). The blocks must each describe
        exactly one block: palettes or "no placement" blocks are not allowed.

        <dimension> can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

        The <doBlockUpdates>, <spawnDrops> and <customFlags> parameters control block update
        behavior. See the GDMC HTTP API documentation for more info.

        Returns a list with one string for each block placement. If the block placement was
        successful, the string is "1" if the block changed, or "0" otherwise. If the placement
        failed, it is the error message.
        """
        url = f"{self.host}/blocks"

        blockStr = "\n".join(
            f"{pos.x} {pos.y} {pos.z} "
            f"{block.id + block.blockStateString() + (f'{{{block.data}}}' if block.data else '')}" for pos, block in blocks
        )

        if customFlags != "":
            blockUpdateParams = {"customFlags": customFlags}
        else:
            blockUpdateParams = {"doBlockUpdates": doBlockUpdates, "spawnDrops": spawnDrops}

        parameters = {"dimension": dimension}
        parameters.update(blockUpdateParams)

        return _put(url, data=bytes(blockStr, "utf-8"), params=parameters, retries=retries, timeout=timeout).text.split("\n")


    def runCommand(self, command: str, dimension: Optional[str] = None, retries=5, timeout=None):
        """Executes one or multiple Minecraft commands (separated by newlines).

        The leading "/" must be omitted.

        <dimension> can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

        Returns a list with one string for each command. If the command was successful, the string
        is its return value. Otherwise, it is the error message.
        """
        url = f"{self.host}/command"
        return _post(url, bytes(command, "utf-8"), params={'dimension': dimension}, retries=retries, timeout=timeout).text.split("\n")


    def getBuildArea(self, retries=5, timeout=None) -> Tuple[bool, Union[Box,str]]:
        """Retrieves the build area that was specified with /setbuildarea in-game.

        Fails if the build area was not specified yet.

        Returns (success, result).
        If a build area was specified, result is the box describing the build area.
        Otherwise, result is the error message string.
        """
        response = _get(f"{self.host}/buildarea", retries=retries, timeout=timeout)

        if not response.ok or response.json() == -1:
            return False, response.text

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
        return True, Box.between(fromPoint, toPoint)


    def getChunks(self, position: ivec2, size: Optional[ivec2] = None, dimension: Optional[str] = None, asBytes=False, retries=5, timeout=None):
        """Returns raw chunk data.

        <position> specifies the position in chunk coordinates, and <size> specifies how many chunks
        to get in each axis (default 1).
        <dimension> can be one of {"overworld", "the_nether", "the_end"} (default "overworld").

        If <asBytes> is True, returns raw binary data. Otherwise, returns a human-readable
        representation.

        On error, returns the error message instead.
        """
        url = f"{self.host}/chunks"
        dx, dz = (None, None) if size is None else size
        parameters = {
            "x": position.x,
            "z": position.y,
            "dx": dx,
            "dz": dz,
            "dimension": dimension,
        }
        acceptType = "application/octet-stream" if asBytes else "text/plain"
        response = _get(url, params=parameters, headers={"Accept": acceptType}, retries=retries, timeout=timeout)
        if response.status_code >= 400:
            eprint(f"Error: {response.text}")

        return response.content if asBytes else response.text


    def getVersion(self, retries=5, timeout=None):
        """Returns the Minecraft version as a string."""
        return _get(f"{self.host}/version", retries=retries, timeout=timeout).text


    def isConnected(self) -> Tuple[bool, Optional[bool]]:
        """Returns whether this Interface is currently connected to an active GDMC HTTP interface.\n
        Checks whether a single HTTP request is succesfully received.
        """
        try:
            _ = self.getVersion(retries=0)
        except RequestConnectionError:
            return False
        return True
