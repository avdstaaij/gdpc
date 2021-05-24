#! /usr/bin/python3
"""### Provide access to the HTTP interface of the Minecraft HTTP server.

This file contains various functions that map directly onto the HTTP interface.
It is recommended to use `interface.py` instead.
"""
__all__ = []
__version__ = "v4.3_dev"

import requests
from requests.exceptions import ConnectionError


def getBlock(x, y, z):
    """**Return the name of a block from the world**."""
    url = f'http://localhost:9000/blocks?x={x}&y={y}&z={z}'
    try:
        response = requests.get(url).text
    except ConnectionError:
        return "minecraft:void_air"
    return response


def setBlock(x, y, z, blockStr, doBlockUpdates=True, customFlags=None):
    """**Place one or multiple blocks in the world**."""
    if customFlags is not None:
        blockUpdateQueryParam = f"customFlags={customFlags}"
    else:
        blockUpdateQueryParam = f"doBlockUpdates={doBlockUpdates}"

    url = (f'http://localhost:9000/blocks?x={x}&y={y}&z={z}'
           f'&{blockUpdateQueryParam}')
    try:
        response = requests.put(url, blockStr)
    except ConnectionError:
        return "0"
    return response.text


def sendBlocks(blockList, x=0, y=0, z=0, retries=5,
               doBlockUpdates=True, customFlags=None):
    """**Take a list of blocks and place them into the world in one go**."""
    body = str.join("\n", ['~{} ~{} ~{} {}'.format(*bp) for bp in blockList])
    try:
        response = setBlock(x, y, z, body, doBlockUpdates, customFlags)
        return response
    except ConnectionError as e:
        print("Request failed: {} Retrying ({} left)".format(e, retries))
        if retries > 0:
            return sendBlocks(x, y, z, retries - 1)
    return False


def runCommand(command):
    """**Run a Minecraft command in the world**."""
    url = 'http://localhost:9000/command'
    try:
        response = requests.post(url, bytes(command, "utf-8"))
    except ConnectionError:
        return "connection error"
    return response.text


def requestBuildArea():
    """**Return the building area**."""
    area = 0, 0, 0, 128, 256, 128   # default area for beginners
    response = requests.get('http://localhost:9000/buildarea')
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
        print(response.text)
        print("Using default build area (0, 0, 0, 128, 256, 128).")
    return area


def getChunks(x, z, dx, dz, rtype='text'):
    """**Get raw chunk data**."""
    url = f'http://localhost:9000/chunks?x={x}&z={z}&dx={dx}&dz={dz}'
    acceptType = 'application/octet-stream' if rtype == 'bytes' else 'text/raw'
    response = requests.get(url, headers={"Accept": acceptType})
    if response.status_code >= 400:
        print(f"Error: {response.text}")

    if rtype == 'text':
        return response.text
    elif rtype == 'bytes':
        return response.content
    else:
        raise Exception(f"{rtype} is not a valid return type.")
