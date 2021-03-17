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
# __version__

import warnings

import requests


class Interface():
    """**Provides tools for interacting with the HTML interface.**

    All function parameters and returns are in local coordinates.
    """

    def __init__(self, offset=(0, 0, 0), useBatching=True, batchSize=100):
        self.buffer = []
        self.offset = offset
        self.useBatching = useBatching
        self.batchSize = batchSize

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
                             *self.global2local(x2 - x1, None, z2 - z1))
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
        url = 'http://localhost:9000/command'
        try:
            response = requests.post(url, bytes(command, "utf-8"))
        except ConnectionError:
            return "connection error"

        # TODO: global2local

        return response.text

    def getBlock(self, x, y, z):
        """**Returns the name of a block in the world.**"""
        x, y, z = self.local2global(x, y, z)

        url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        # DEBUG: print(url)
        try:
            response = requests.get(url)
        except ConnectionError:
            return "minecraft:void_air"
        return response.text
        # DEBUG: print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))

    def setBlock(self, x, y, z, blockStr):
        if self.useBatching:
            self._placeBlockBatched(x, y, z, blockStr, self.batchSize)
        else:
            self._setBlockDirect(x, y, z, blockStr)

    def sendOutstandingBlocks(self):
        self._sendBlocks()

    def _setBlockDirect(self, x, y, z, blockStr):
        """**Places a block in the world.**"""
        x, y, z = self.local2global(x, y, z)

        url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        # DEBUG: print('setting block {} at {} {} {}'.format(blockStr, x, y, z))
        try:
            response = requests.put(url, blockStr)
        except ConnectionError:
            return "0"
        return response.text
        # DEBUG: print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))

    # --------------------------------------------------------- block buffers

    def _placeBlockBatched(self, x, y, z, blockStr, limit=50):
        """**Place a block in the buffer and send if the limit is exceeded.**"""
        x, y, z = self.local2global(x, y, z)

        self.buffer.append((x, y, z, blockStr))
        if len(self.buffer) >= limit:
            return self._sendBlocks()
        else:
            return None

    def _sendBlocks(self, x=0, y=0, z=0, retries=5):
        """**Sends the buffer to the server and clears it.**

        Since the buffer contains global coordinates no conversion takes place in this function
        """

        url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
        body = str.join("\n", ['~{} ~{} ~{} {}'.format(*bp)
                               for bp in self.buffer])
        # DEBUG: print(body)
        try:
            response = requests.put(url, body)
            self.buffer = []
            return response.text
        except ConnectionError as e:
            print("Request failed: {} Retrying ({} left)".format(e, retries))
            if retries > 0:
                return self._sendBlocks(x, y, z, retries - 1)

    # --------------------------------------------------------- utility functions

    def local2global(self, x, y, z):
        result = []
        if x != None:
            result.append(x + self.offset[0])
        if y != None:
            result.append(y + self.offset[1])
        if z != None:
            result.append(z + self.offset[2])
        return result

    def global2local(self, x, y, z):
        result = []
        if x != None:
            result.append(x - self.offset[0])
        if y != None:
            result.append(y - self.offset[1])
        if z != None:
            result.append(z - self.offset[2])
        return result


# ========================================================= DEPRACATED


def requestBuildArea():
    """**Returns the building area. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    response = requests.get('http://localhost:9000/buildarea')
    if response.ok:
        return response.json()
    else:
        print(response.text)
        return -1


def runCommand(command):
    """**Runs a Minecraft command in the world. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    # print("running cmd " + command)
    url = 'http://localhost:9000/command'
    try:
        response = requests.post(url, bytes(command, "utf-8"))
    except ConnectionError:
        return "connection error"
    return response.text

# --------------------------------------------------------- get/set block


def getBlock(x, y, z):
    """**Returns the namespaced id of a block in the world. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    # print(url)
    try:
        response = requests.get(url)
    except ConnectionError:
        return "minecraft:void_air"
    return response.text
    # print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))


def setBlock(x, y, z, blockStr):
    """**Places a block in the world. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)

    url = 'http://localhost:9000/blocks?x={}&y={}&z={}'.format(x, y, z)
    # print('setting block {} at {} {} {}'.format(blockStr, x, y, z))
    try:
        response = requests.put(url, blockStr)
    except ConnectionError:
        return "0"
    return response.text
    # print("{}, {}, {}: {} - {}".format(x, y, z, response.status_code, response.text))


# --------------------------------------------------------- block buffers

blockBuffer = []


def placeBlockBatched(x, y, z, blockStr, limit=50):
    """**Place a block in the buffer and send if the limit is exceeded. (deprecated)**"""
    warnings.warn("Please use the Interface class.", DeprecationWarning)
    global blockBuffer

    blockBuffer.append((x, y, z, blockStr))
    if len(blockBuffer) >= limit:
        return sendBlocks(0, 0, 0)
    else:
        return None


def sendBlocks(x=0, y=0, z=0, retries=5):
    """**Sends the buffer to the server and clears it. (deprecated)**"""
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
