"""Provide access to the HTTP interface of the Minecraft HTTP server.

This file contains various functions that map directly onto the HTTP interface.
It is recommended to use `interface.py` instead.
"""

import requests
from requests.exceptions import ConnectionError as RequestConnectionError


def get(*args):
    try:
        return requests.get(*args)
    except RequestConnectionError as e:
        raise RequestConnectionError(
            "Connection could not be established! (is Minecraft running?)"
        ) from e


def post(*args):
    try:
        return requests.post(*args)
    except RequestConnectionError as e:
        raise RequestConnectionError(
            "Connection could not be established! (is Minecraft running?)"
        ) from e


def getBlock(x, y, z, dx=None, dy=None, dz=None, includeState=None, includeData=None, dimension=None, asJsonResponse=True):
    """Return block material, position and other attributes on one or multiple positions in the world."""
    url = 'http://localhost:9000/blocks'
    parameters = {
        'x': x,
        'y': y,
        'z': z,
        'dx': dx,
        'dy': dy,
        'dz': dz,
        'includeState': includeState,
        'includeData': includeData,
        'dimension': dimension,
    }
    try:
        if asJsonResponse:
            response = requests.get(url, params=parameters, headers={'Accept': 'application/json'}).json()
            if len(response) == 1:
                response = response[0]
        else:
            response = requests.get(url, params=parameters).text
    except RequestConnectionError:
        if asJsonResponse:
            return {
                'id': 'minecraft:void_air',
                'x': x,
                'y': y,
                'z': z,
            }
        return f'{x} {y} {z} minecraft:void_air'
    return response


def placeBlock(x, y, z, blockStr, doBlockUpdates=True, customFlags=None, dimension=None, asJsonResponse=False):
    """Place one or multiple blocks in the world."""
    url = 'http://localhost:9000/blocks'
    parameters = {
        'x': x,
        'y': y,
        'z': z,
        'doBlockUpdates': doBlockUpdates,
        'customFlags': customFlags,
        'dimension': dimension,
    }
    headers = {'Accept': 'application/json'} if asJsonResponse else {}
    try:
        response = requests.put(url, data=bytes(blockStr, "utf-8"), params=parameters, headers=headers)
    except RequestConnectionError:
        return "0"
    if asJsonResponse:
        return response.json()
    return response.text


def sendBlocks(blockList, x=0, y=0, z=0, retries=5,
               doBlockUpdates=True, customFlags=None, dimension=None):
    """Take a list of blocks and place them into the world in one go."""
    body = str.join("\n", ['~{} ~{} ~{} {}'.format(*bp) for bp in blockList])
    try:
        response = placeBlock(x, y, z, body, doBlockUpdates, customFlags, dimension)
        return response
    except RequestConnectionError as e:
        print("Request failed: {} Retrying ({} left)".format(e, retries))
        if retries > 0:
            return sendBlocks(blockList, x, y, z, retries - 1, doBlockUpdates, customFlags, dimension)
    return False


def runCommand(command, dimension=None):
    """Run a Minecraft command in the world."""
    url = 'http://localhost:9000/command'
    try:
        response = requests.post(url, bytes(command, "utf-8"), params={'dimension': dimension})
    except RequestConnectionError:
        return "connection error"
    return response.text


def requestBuildArea():
    """Return the building area."""
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


def getChunks(x, z, dx, dz, dimension=None, rtype='text'):
    """Get raw chunk data."""
    url = 'http://localhost:9000/chunks'
    parameters = {
        'x': x,
        'z': z,
        'dx': dx,
        'dz': dz,
        'dimension': dimension,
    }
    acceptType = 'application/octet-stream' if rtype == 'bytes' else 'text/plain'
    response = requests.get(url, params=parameters, headers={"Accept": acceptType})
    if response.status_code >= 400:
        print(f"Error: {response.text}")

    if rtype == 'text':
        return response.text
    elif rtype == 'bytes':
        return response.content
    else:
        raise Exception(f"{rtype} is not a valid return type.")
