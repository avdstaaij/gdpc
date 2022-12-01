"""Provide access to the HTTP interface of the Minecraft HTTP server.

This file contains various functions that map directly onto the HTTP interface.
It is recommended to use `interface.py` instead.
"""


import requests
from requests.exceptions import ConnectionError as RequestConnectionError

from .util import eprint


HOST = "http://localhost:9000"


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


def getBlock(x, y, z, retries=5, timeout=None):
    """Return the block ID from the world."""
    url = f'{HOST}/blocks?x={x}&y={y}&z={z}'
    return _get(url, retries=retries, timeout=timeout).text


def placeBlock(x, y, z, blockStr, doBlockUpdates=True, customFlags=None, retries=5, timeout=None):
    """Place one or multiple blocks in the world."""
    if customFlags is not None:
        blockUpdateQueryParam = f"customFlags={customFlags}"
    else:
        blockUpdateQueryParam = f"doBlockUpdates={doBlockUpdates}"

    url = (f'{HOST}/blocks?x={x}&y={y}&z={z}&{blockUpdateQueryParam}')
    return _put(url, blockStr, retries=retries, timeout=timeout).text


def sendBlocks(
    blockList,
    x=0, y=0, z=0,
    doBlockUpdates=True,
    customFlags=None,
    retries=5,
    timeout=None
):
    """Take a list of blocks and place them into the world in one go."""
    body = str.join("\n", ['~{} ~{} ~{} {}'.format(*bp) for bp in blockList])
    return placeBlock(x, y, z, body, doBlockUpdates, customFlags, retries=retries, timeout=timeout)


def runCommand(command, retries=5, timeout=None):
    """Run a Minecraft command in the world."""
    url = '{HOST}/command'
    return _post(url, bytes(command, "utf-8"), retries=retries, timeout=timeout).text


def requestBuildArea(retries=5, timeout=None):
    """Return the building area."""
    area = 0, 0, 0, 128, 256, 128   # default area for beginners
    response = _get('{HOST}/buildarea', retries=retries, timeout=timeout)
    if response.ok:
        buildArea = response.json()
        if buildArea != -1:
            x1 = buildArea["xFrom"]
            y1 = buildArea["yFrom"]
            z1 = buildArea["zFrom"]
            x2 = buildArea["xTo"]
            y2 = buildArea["yTo"]
            z2 = buildArea["zTo"]
            area = x1, y1, z1, x2, y2, z2
    else:
        eprint(response.text)
        eprint("Using default build area (0, 0, 0, 128, 256, 128).")
    return area


def getChunks(x, z, dx, dz, rtype='text', retries=5, timeout=None):
    """Get raw chunk data."""
    url = f'{HOST}/chunks?x={x}&z={z}&dx={dx}&dz={dz}'
    acceptType = 'application/octet-stream' if rtype == 'bytes' else 'text/raw'
    response = _get(url, headers={"Accept": acceptType}, retries=retries, timeout=timeout)
    if response.status_code >= 400:
        eprint(f"Error: {response.text}")

    if rtype == 'text':
        return response.text
    if rtype == 'bytes':
        return response.content
    raise ValueError(f"{rtype} is not a valid return type.")
