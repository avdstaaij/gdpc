# ! /usr/bin/python3
"""### Provide tools for placing and getting blocks and more.

This module contains functions to:
* Request the build area as defined in-world
* Run Minecraft commands
* Get the name of a block at a particular coordinate
* Place blocks in the world
"""
__all__ = ['Interface', 'runCommand',
           'setBuildArea', 'requestBuildArea', 'requestPlayerArea',
           'makeGlobalSlice', 'getBlock', 'placeBlock',
           'getBlockFlags', 'setBlockFlags',
           'isCaching', 'setCaching', 'getCacheLimit', 'setCacheLimit',
           'isBuffering', 'setBuffering', 'getBufferLimit', 'setBufferLimit',
           'sendBlocks', 'checkOutOfBounds']
__version__ = "v4.3_dev"

from collections import OrderedDict
from random import choice

import direct_interface as di
import numpy as np
from lookup import TCOLORS
from worldLoader import WorldSlice


class OrderedByLookupDict(OrderedDict):
    """Limit size, evicting the least recently looked-up key when full.

    Taken from
    https://docs.python.org/3/library/collections.html?highlight=ordereddict#collections.OrderedDict
    """

    def __init__(self, maxsize, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    # inherited __repr__ from OrderedDict is sufficient

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if self.maxsize > 0 and len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


class Interface():
    """**Provides tools for interacting with the HTML interface**.

    All function parameters and returns are in local coordinates.
    """

    def __init__(self, x=0, y=0, z=0,
                 buffering=False, bufferlimit=1024,
                 caching=False, cachelimit=8192):
        """**Initialise an interface with offset and buffering**."""
        self.offset = x, y, z
        self.__buffering = buffering
        self.bufferlimit = bufferlimit
        self.buffer = []    # buffer is in global coordinates
        self.setblockflags = (True, None)   # (doBlockUpdates, CustomFlags)
        self.bufferblockflags = (True, None)   # (doBlockUpdates, CustomFlags)
        self.caching = caching
        # cache is in global coordinates
        self.cache = OrderedByLookupDict(cachelimit)
        # Interface.cache.maxsize to change size

    def __del__(self):
        """**Clean up before destruction**."""
        self.sendBlocks()

    # __repr__ displays the class well enough so __str__ is omitted
    def __repr__(self):
        """**Represent the Interface as a constructor**."""
        return "Interface(" \
            f"{self.offset[0]}, {self.offset[1]}, {self.offset[2]}, " \
            f"{self.__buffering}, {self.bufferlimit}, " \
            f"{self.caching}, {self.cache.maxsize})"

    def getBlock(self, x, y, z):
        """**Return the name of a block in the world**.

        Takes local coordinates, works with global coordinates
        """
        x, y, z = self.local2global(x, y, z)

        if self.caching and (x, y, z) in self.cache:
            return self.cache[(x, y, z)]

        if self.caching and globalWorldSlice is not None:
            dx, dy, dz = global2buildlocal(x, y, z)  # convert for decay index
            if not checkOutOfBounds(x, y, z) and not globalDecay[dx][dy][dz]:
                block = globalWorldSlice.getBlockAt(x, y, z)
                self.cache[(x, y, z)] = block
                return block

        response = di.getBlock(x, y, z)
        if self.caching:
            self.cache[(x, y, z)] = response

        return response

    def placeBlock(self, x, y, z, block, replace=None,
                   doBlockUpdates=-1, customFlags=-1):
        """**Place a block in the world depending on buffer activation**.

        Takes local coordinates, works with local and global coordinates
        """
        flags = doBlockUpdates, customFlags
        from toolbox import isSequence
        if isinstance(replace, str):
            if self.getBlock(x, y, z) != replace:
                return '0'
        elif isSequence(replace) and self.getBlock(x, y, z) not in replace:
            return '0'

        if not isinstance(block, str) and isSequence(block):
            block = choice(block)

        if self.__buffering:
            response = self.setBlockBuffered(x, y, z, block, self.bufferlimit,
                                             flags)
        else:
            response = self.setBlock(x, y, z, block, flags)

        # switch to global coordinates
        x, y, z = self.local2global(x, y, z)
        if self.caching:
            self.cache[(x, y, z)] = block
        # mark block as decayed
        if not checkOutOfBounds(x, y, z) and globalDecay is not None:
            x, y, z = global2buildlocal(x, y, z)
            globalDecay[x][y][z] = True

        return response

    def setBlock(self, x, y, z, blockStr,
                 doBlockUpdates=-1, customFlags=-1):
        """**Place a single block in the world directly**.

        Takes local coordinates, works with global coordinates
        """
        if doBlockUpdates == -1:
            doBlockUpdates = self.setblockflags[0]
        if customFlags == -1:
            customFlags = self.setblockflags[1]

        x, y, z = self.local2global(x, y, z)
        result = di.setBlock(x, y, z, blockStr, doBlockUpdates, customFlags)
        if not result.isnumeric():
            print(f"{TCOLORS['orange']}Warning: Server returned error "
                  f"upon placing block:\n\t{TCOLORS['CLR']}{result}")
        return result

    def getBlockFlags(self):
        """**Get default block placement flags**."""
        return self.setblockflags

    def setBlockFlags(self, doBlockUpdates=True, customFlags=None):
        """**Set default block placement flags**."""
        self.setblockflags = doBlockUpdates, customFlags

    # ----------------------------------------------------- block buffers

    def isBuffering(self):
        """**Get self.__buffering**."""
        return self.__buffering

    def setBuffering(self, value, notify=True):
        """**Set self.__buffering**."""
        self.__buffering = value
        if self.__buffering and notify:
            print("Buffering has been activated.")
        elif notify:
            self.sendBlocks()
            print("Buffering has been deactivated.")

    def getBufferLimit(self):
        """**Get self.bufferlimit**."""
        return self.bufferlimit

    def setBufferLimit(self, value):
        """**Set self.bufferlimit**."""
        self.bufferlimit = value

    def isCaching(self):
        """**Get self.caching**."""
        return self.caching

    def setCaching(self, value=False):
        """**Set self.caching**."""
        self.caching = value

    def getCacheLimit(self):
        """**Get maximum cache size**."""
        return self.cache.maxsize

    def setCacheLimit(self, value=8192):
        """**Set maximum cache size**."""
        self.cache.maxsize = value

    def setBlockBuffered(self, x, y, z, blockStr, limit=50,
                         doBlockUpdates=-1, customFlags=-1):
        """**Place a block in the buffer and send once limit is exceeded**.

        Takes local coordinates and works with global coordinates
        """
        if doBlockUpdates == -1:
            doBlockUpdates = self.setblockflags[0]
        if customFlags == -1:
            customFlags = self.setblockflags[1]

        if (doBlockUpdates, customFlags) != self.bufferblockflags:
            self.sendBlocks()
            self.bufferblockflags = doBlockUpdates, customFlags

        x, y, z = self.local2global(x, y, z)

        self.buffer.append((x, y, z, blockStr))
        if len(self.buffer) >= limit:
            return self.sendBlocks()
        else:
            return '0'

    def sendBlocks(self, x=0, y=0, z=0, retries=5):
        """**Send the buffer to the server and clear it**.

        Since the buffer contains global coordinates
            no conversion takes place in this function
        """
        if self.buffer == []:
            return '0'
        response = di.sendBlocks(self.buffer, x, y, z,
                                 retries, *self.bufferblockflags).split('\n')
        if all(map(lambda val: val.isnumeric(), response)):  # no errors
            self.buffer = []
            return str(sum(map(int, response)))
        else:
            print(f"{TCOLORS['orange']}Warning: Server returned error upon "
                  f"sending block buffer:\n\t{TCOLORS['CLR']}{repr(response)}")

    # ----------------------------------------------------- utility functions

    def local2global(self, x, y, z):
        """**Translate local to global coordinates**."""
        result = []
        if x is not None:
            result.append(x + self.offset[0])
        if y is not None:
            result.append(y + self.offset[1])
        if z is not None:
            result.append(z + self.offset[2])
        return result

    def global2local(self, x, y, z):
        """**Translate global to local coordinates**."""
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
    return di.runCommand(command)


def setBuildArea(x1, y1, z1, x2, y2, z2):
    """**Set and return the build area**."""
    runCommand(f"setbuildarea {x1} {y1} {z1} {x2} {y2} {z2}")
    return requestBuildArea()


def requestBuildArea():
    """**Return the current building area**.

    Will reset anything dependant on the build area.
    """
    global globalBuildArea

    x1, _, z1, x2, _, z2 = globalBuildArea = di.requestBuildArea()

    if globalWorldSlice is not None:
        resetGlobalDecay()

    return globalBuildArea


def requestPlayerArea(dx=128, dz=128):
    """**Return the building area surrounding the player**."""
    # Correcting for offset from player position
    dx -= 1
    dz -= 1
    runCommand("execute at @p run setbuildarea "
               f"~{-dx//2} 0 ~{-dz//2} ~{dx//2} 255 ~{dz//2}")
    return requestBuildArea()


# ========================================================= global interface


globalWorldSlice = None
globalDecay = None
globalBuildArea = requestBuildArea()

globalinterface = Interface()


def makeGlobalSlice():
    """**Instantiate a global WorldSlice and refresh building area**."""
    global globalWorldSlice
    x1, y1, z1, x2, y2, z2 = requestBuildArea()
    globalWorldSlice = WorldSlice(x1, z1, x2, z2)
    resetGlobalDecay()
    return globalWorldSlice


def getBlock(x, y, z):
    """**Global getBlock**."""
    return globalinterface.getBlock(x, y, z)


def placeBlock(x, y, z, blocks, replace=None):
    """**Global setBlock**."""
    return globalinterface.placeBlock(x, y, z, blocks, replace)


def getBlockFlags():
    """**Global getBlockFlags**."""
    return globalinterface.getBlockFlags()


def setBlockFlags(doBlockUpdates=True, customFlags=None):
    """**Global setBlockFlags**."""
    globalinterface.setBlockFlags(doBlockUpdates, customFlags)

# ----------------------------------------------------- block buffers


def isCaching():
    """**Global isCaching**."""
    return globalinterface.caching


def setCaching(value=False):
    """**Global setCaching**."""
    globalinterface.caching = value


def getCacheLimit():
    """**Global getCacheLimit**."""
    return globalinterface.cache.maxsize


def setCacheLimit(value=8192):
    """**Global setCacheLimit**."""
    globalinterface.cache.maxsize = value


def isBuffering():
    """**Global isBuffering**."""
    return globalinterface.isBuffering()


def setBuffering(val):
    """**Global setBuffering**."""
    globalinterface.setBuffering(val)


def getBufferLimit():
    """**Global getBufferLimit**."""
    return globalinterface.getBufferLimit()


def setBufferLimit(val):
    """**Global setBufferLimit**."""
    globalinterface.setBufferLimit(val)


def sendBlocks(x=0, y=0, z=0, retries=5):
    """**Global sendBlocks**."""
    return globalinterface.sendBlocks(x, y, z, retries)

# ----------------------------------------------------- utility functions


def checkOutOfBounds(x, y, z, warn=True):
    """**Check whether a given coordinate is outside the build area**."""
    x1, y1, z1, x2, y2, z2 = globalBuildArea
    if not (x1 <= x <= x2 and y1 <= y <= y2 and z1 <= z <= z2):
        if warn:
            # building outside the build area can be less efficient
            print(f"{TCOLORS['orange']}WARNING: Block at {x, y, z} is outside "
                  f"the build area!{TCOLORS['CLR']}")
        return True
    return False


def global2buildlocal(x, y, z):
    """**Convert global coordinates to ones relative to the build area**."""
    x0, y0, z0, _, _, _ = globalBuildArea
    return x - x0, y - y0, z - z0


def resetGlobalDecay():
    """**Reset the global decay marker**."""
    global globalDecay
    x1, _, z1, x2, _, z2 = globalBuildArea
    globalDecay = np.zeros((x2 - x1, 256, z2 - z1), dtype=bool)
