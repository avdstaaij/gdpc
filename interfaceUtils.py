# ! /usr/bin/python3
"""### Provide tools for placing and getting blocks and more.

This module contains functions to:
* Request the build area as defined in-world
* Run Minecraft commands
* Get the name of a block at a particular coordinate
* Place blocks in the world
"""
__all__ = ['requestBuildArea', 'runCommand',
           'setBlock', 'getBlock',
           'placeBlockBatched', 'sendBlocks']
__author__ = "Nils Gawlik <nilsgawlik@gmx.de>"
__date__ = "11 March 2021"
# __version__
__credits__ = "Nils Gawlick for being awesome and creating the framework" + \
    "Flashing Blinkenlights for general improvements"

import warnings

import requests


class Interface():
    """**Provides tools for interacting with the HTML interface**.

    All function parameters and returns are in local coordinates.
    """

    def __init__(self, offset=(0, 0, 0), buffering=False, bufferlimit=4096):
        self.offset = offset
        self.buffering = False
        self.bufferlimit = 4096
        self.buffer = []

    def requestBuildArea(self):
        """**Return the building area**."""
        response = requests.get('http://localhost:9000/buildarea')
        if response.ok:
            buildArea = response.json()
            if buildArea != -1:
                x1 = buildArea["xFrom"]
                z1 = buildArea["zFrom"]
                x2 = buildArea["xTo"]
                z2 = buildArea["zTo"]
                buildArea = (*self.global2local(x1, None, z1),
                             *self.global2local(x2 - x1, None, z2 - z1))
            return buildArea
        else:
            print(response.text)

    def getBlock(self, x, y, z):
        """**Return the name of a block in the world**."""
        x, y, z = self.local2global(x, y, z)

        url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        try:
            response = requests.get(url)
        except ConnectionError:
            return "minecraft:void_air"
        return response.text

    def setBlock(self, x, y, z, str):
        """**Place a block in the world depending on buffer activation**."""
        if self.buffering:
            self.placeBlockBatched(x, y, z, str, self.limit)
        else:
            self.placeBlock(x, y, z, str)

    def placeBlock(self, x, y, z, str):
        """**Place a single block in the world**."""
        x, y, z = self.local2global(x, y, z)

        url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        try:
            response = requests.put(url, str)
        except ConnectionError:
            return "0"
        return response.text

    # ----------------------------------------------------- block buffers

    def placeBlockBatched(self, x, y, z, str, limit=50):
        """**Place a block in the buffer and send once limit is exceeded**."""
        x, y, z = self.local2global(x, y, z)

        self.buffer.append((x, y, z, str))
        if len(self.buffer) >= limit:
            return self.sendBlocks()
        else:
            return None

    def sendBlocks(self, x=0, y=0, z=0, retries=5):
        """**Send the buffer to the server and clear it**.

        Since the buffer contains global coordinates
            no conversion takes place in this function
        """
        url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        body = str.join("\n", ['~{} ~{} ~{} {}'.format(*bp)
                               for bp in self.buffer])
        print(body)
        try:
            response = requests.put(url, body)
            self.buffer = []
            return response.text
        except ConnectionError as e:
            print("Request failed: {} Retrying ({} left)".format(e, retries))
            if retries > 0:
                return self.sendBlocks(x, y, z, retries - 1)

    # ----------------------------------------------------- utility functions

    def local2global(self, x, y, z):
        result = []
        if x is not None:
            result.append(x + self.offset[0])
        if y is not None:
            result.append(y + self.offset[1])
        if z is not None:
            result.append(z + self.offset[2])
        return result

    def global2local(self, x, y, z):
        result = []
        if x is not None:
            result.append(x - self.offset[0])
        if y is not None:
            result.append(y - self.offset[1])
        if z is not None:
            result.append(z - self.offset[2])
        return result


def runCommand(command):
    """**Run a Minecraft command in the world**."""
    url = 'http://localhost:9000/command'
    try:
        response = requests.post(url, bytes(command, "utf-8"))
    except ConnectionError:
        return "connection error"
    return response.text


# ========================================================= DEPRACATED


def requestBuildArea():
    """**Return the building area (deprecated)**."""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    response = requests.get('http://localhost:9000/buildarea')
    if response.ok:
        return response.json()
    else:
        print(response.text)
        return -1


# --------------------------------------------------------- get/set block


def getBlock(x, y, z):
    """**Return the name of a block in the world (deprecated)**."""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    try:
        response = requests.get(url)
    except ConnectionError:
        return "minecraft:void_air"
    return response.text


def setBlock(x, y, z, str):
    """**Place a block in the world (deprecated)**."""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    try:
        response = requests.put(url, str)
    except ConnectionError:
        return "0"
    return response.text


# --------------------------------------------------------- block buffers

blockBuffer = []


def placeBlockBatched(x, y, z, str, limit=50):
    """**Place block in buffer and send once limit exceeded (deprecated)**."""
    warnings.warn("Please use the Interface class.", DeprecationWarning)
    global blockBuffer

    blockBuffer.append((x, y, z, str))
    if len(blockBuffer) >= limit:
        return sendBlocks(0, 0, 0)
    else:
        return None


def sendBlocks(x=0, y=0, z=0, retries=5):
    """**Send the buffer to the server and clears it (deprecated)**."""
    warnings.warn("Please use the Interface class.", DeprecationWarning)
    global blockBuffer

    url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    body = str.join("\n", ['~{} ~{} ~{} {}'.format(*bp) for bp in blockBuffer])
    try:
        response = requests.put(url, body)
        blockBuffer = []
        return response.text
    except ConnectionError as e:
        print("Request failed: {} Retrying ({} left)".format(e, retries))
        if retries > 0:
            return sendBlocks(x, y, z, retries - 1)
