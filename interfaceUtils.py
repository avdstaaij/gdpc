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
    """**Provides tools for interacting with the HTML interface.**

    All function parameters and returns are in local coordinates.
    """

    self.buffer = []

    def __init__(offset=(0, 0, 0)):
        self.offset = offset

    def requestBuildArea(self):
        """**Returns the building area.**"""

        response = requests.get('http://localhost:9000/buildarea')
        if response.ok:
            buildArea = response.json()
            if buildArea != -1:
                x1 = buildArea["xFrom"]
                z1 = buildArea["zFrom"]
                x2 = buildArea["xTo"]
                z2 = buildArea["zTo"]
                # print(buildArea)
                buildArea = (*self.global2local(x1, None, z1),
                             *self.global2local(x2 - x1, None, z2 - z1)
            return buildArea
        else:
            print(response.text)

    def runCommand(self, command):
        """**Runs a Minecraft command in the world.**

        TODO: extract and convert local coordinates
        """

        # TODO: local2global
        print("WARNING: Interface.runCommand not correctly implemented yet!")

        # DEBUG: print("running cmd " + command)
        url='http://localhost:9000/command'
        try:
            response=requests.post(url, bytes(command, "utf-8"))
        except ConnectionError:
            return "connection error"

        # TODO: global2local

        return response.text

    def getBlock(self, x, y, z):
        """**Returns the name of a block in the world.**"""
        x, y, z=self.local2global(x, y, z)

        url='http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        # DEBUG: print(url)
        try:
            response=requests.get(url)
        except ConnectionError:
            return "minecraft:void_air"
        return response.text
        # DEBUG: print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))

    def setBlock(self, x, y, z, str):
        """**Places a block in the world.**"""
        x, y, z=self.local2global(x, y, z)

        url='http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        # DEBUG: print('setting block {} at {} {} {}'.format(str, x, y, z))
        try:
            response=requests.put(url, str)
        except ConnectionError:
            return "0"
        return response.text
        # DEBUG: print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))

    def local2global(self, x, y, z):
        result=[]
        if x != None:
            result.append(x + self.offset[0])
        if y != None:
            result.append(y + self.offset[1])
        if z != None:
            result.append(z + self.offset[2])
        return result

    def global2local(self, x, y, z):
        result=[]
        if x != None:
            result.append(x - self.offset[0])
        if y != None:
            result.append(y - self.offset[1])
        if z != None:
            result.append(z - self.offset[2])
        return result

    # --------------------------------------------------------- block buffers

    blockBuffer=[]

    def placeBlockBatched(x, y, z, str, limit=50):
        """**Place a block in the buffer and send if the limit is exceeded. (deprecated)**"""
        warnings.warn("Please use the Interface class.", DeprecationWarning)

        registerSetBlock(x, y, z, str)
        if len(blockBuffer) >= limit:
            return sendBlocks(0, 0, 0)
        else:
            return None

    def sendBlocks(x=0, y=0, z=0, retries=5):
        """**Sends the buffer to the server and clears it. (deprecated)**"""
        warnings.warn("Please use the Interface class.", DeprecationWarning)

        global blockBuffer
        body="\n" + '~{} ~{} ~{} {}'.format(*[bp for bp in blockBuffer])
        url='http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        try:
            response=requests.put(url, body)
            clearBlockBuffer()
            return response.text
        except ConnectionError as e:
            print("Request failed: {} Retrying ({} left)".format(e, retries))
            if retries > 0:
                return sendBlocks(x, y, z, retries - 1)

    def registerSetBlock(x, y, z, str):
        """**Places a block in the buffer.**"""

        # buffer += () '~{} ~{} ~{} {}'.format(x, y, z, str)
        self.buffer.append((x, y, z, str))

    def clearBuffer():
        """**Clears the block buffer.**"""

        self.buffer=[]


# ========================================================= DEPRACATED


def requestBuildArea():
    """**Returns the building area. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    response=requests.get('http://localhost:9000/buildarea')
    if response.ok:
        return response.json()
    else:
        print(response.text)
        return -1


def runCommand(command):
    """**Runs a Minecraft command in the world. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    # print("running cmd " + command)
    url='http://localhost:9000/command'
    try:
        response=requests.post(url, bytes(command, "utf-8"))
    except ConnectionError:
        return "connection error"
    return response.text

# --------------------------------------------------------- get/set block


def getBlock(x, y, z):
    """**Returns the name of a block in the world. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    url='http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    # print(url)
    try:
        response=requests.get(url)
    except ConnectionError:
        return "minecraft:void_air"
    return response.text
    # print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))


def setBlock(x, y, z, str):
    """**Places a block in the world. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    url='http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    # print('setting block {} at {} {} {}'.format(str, x, y, z))
    try:
        response=requests.put(url, str)
    except ConnectionError:
        return "0"
    return response.text
    # print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))


# --------------------------------------------------------- block buffers

blockBuffer=[]


def placeBlockBatched(x, y, z, str, limit=50):
    """**Place a block in the buffer and send if the limit is exceeded. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    registerSetBlock(x, y, z, str)
    if len(blockBuffer) >= limit:
        return sendBlocks(0, 0, 0)
    else:
        return None


def sendBlocks(x=0, y=0, z=0, retries=5):
    """**Sends the buffer to the server and clears it. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    global blockBuffer
    body="\n" + '~{} ~{} ~{} {}'.format(*[bp for bp in blockBuffer])
    url='http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    try:
        response=requests.put(url, body)
        clearBlockBuffer()
        return response.text
    except ConnectionError as e:
        print("Request failed: {} Retrying ({} left)".format(e, retries))
        if retries > 0:
            return sendBlocks(x, y, z, retries - 1)


def registerSetBlock(x, y, z, str):
    """**Places a block in the buffer. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    global blockBuffer
    # blockBuffer += () '~{} ~{} ~{} {}'.format(x, y, z, str)
    blockBuffer.append((x, y, z, str))


def clearBlockBuffer():
    """**Clears the block buffer. (deprecated)**"""

    warnings.warn("Please use the Interface class.", DeprecationWarning)
    global blockBuffer
    blockBuffer=[]
