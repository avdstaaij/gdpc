# ! /usr/bin/python3
"""### Provide tools for placing and getting blocks and more.

This module contains functions to:
* Request the build area as defined in-world
* Run Minecraft commands
* Get the name of a block at a particular coordinate
* Place blocks in the world
"""
__all__ = ['Interface', 'requestBuildArea', 'runCommand',
           'setBlock', 'getBlock', 'sendBlocks']
__version__ = "v4.2_dev"

from collections import OrderedDict

import direct_interface as di
import numpy as np
from worldLoader import WorldSlice


class OrderedByLookupDict(OrderedDict):
    """Limit size, evicting the least recently looked-up key when full.

    Taken from
    https://docs.python.org/3/library/collections.html?highlight=ordereddict#collections.OrderedDict
    """

    def __init__(self, maxsize=128, /, *args, **kwds):
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
        if self.maxsize != -1 and len(self) > self.maxsize:
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
        x1, y1, z1, x2, y2, z2 = requestBuildArea()

        self.offset = x, y, z
        self.__buffering = buffering
        self.bufferlimit = bufferlimit
        self.buffer = []
        self.caching = caching
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
        """**Return the name of a block in the world**."""
        x, y, z = self.local2global(x, y, z)

        if self.caching and (x, y, z) in self.cache:
            return self.cache[(x, y, z)]

        if self.caching and globalWorldSlice is not None:
            dx, dy, dz = global2buildlocal(x, y, z)  # convert for decay index
            print(f"{x, y, z, dx, dy, dz}")
            if not globalDecay[dx][dy][dz]:
                block = globalWorldSlice.getBlockAt(x, y, z)
                self.cache[(x, y, z)] = block
                return block

        response = di.getBlock(x, y, z)
        if self.caching:
            self.cache[(x, y, z)] = response

        return response

    def fill(self, x1, y1, z1, x2, y2, z2, blockStr):
        """**Fill the given region with the given block**."""
        x1, y1, z1 = self.local2global(x1, y1, z1)
        x2, y2, z2 = self.local2global(x2, y2, z2)
        xlo, ylo, zlo = min(x1, x2), min(y1, y2), min(z1, z2)
        xhi, yhi, zhi = max(x1, x2), max(y1, y2), max(z1, z2)

        for x in range(xlo, xhi + 1):
            for y in range(ylo, yhi + 1):
                for z in range(zlo, zhi + 1):
                    self.setBlock(x, y, z, blockStr)

    def setBlock(self, x, y, z, blockStr):
        """**Place a block in the world depending on buffer activation**."""
        if self.__buffering:
            self.placeBlockBatched(x, y, z, blockStr, self.bufferlimit)
        else:
            self.placeBlock(x, y, z, blockStr)
        if self.caching:
            self.cache[(x, y, z)] = blockStr
        # mark block as decayed
        if globalDecay is not None:
            x, y, z = global2buildlocal(*self.local2global(x, y, z))
            globalDecay[x][y][z] = True

    def placeBlock(self, x, y, z, blockStr):
        """**Place a single block in the world**."""
        x, y, z = self.local2global(x, y, z)
        return di.setBlock(x, y, z, blockStr)

    # ----------------------------------------------------- block buffers

    def toggleBuffer(self):
        """**Activates or deactivates the buffer function safely**."""
        self.buffering = not self.buffering
        return self.buffering

    def isBuffering(self):
        """**Get self.__buffering**."""
        return self.__buffering

    def setBuffering(self, value):
        """**Set self.__buffering**."""
        self.__buffering = value
        if self.__buffering:
            print("Buffering has been activated.")
        else:
            self.sendBlocks()
            print("Buffering has been deactivated.")

    def getBufferlimit(self):
        """**Get self.bufferlimit**."""
        return self.bufferlimit

    def setBufferLimit(self, value):
        """**Set self.bufferlimit**."""
        self.bufferlimit = value

    def placeBlockBatched(self, x, y, z, blockStr, limit=50):
        """**Place a block in the buffer and send once limit is exceeded**."""
        x, y, z = self.local2global(x, y, z)

        self.buffer.append((x, y, z, blockStr))
        if len(self.buffer) >= limit:
            return self.sendBlocks()
        else:
            return None

    def sendBlocks(self, x=0, y=0, z=0, retries=5):
        """**Send the buffer to the server and clear it**.

        Since the buffer contains global coordinates
            no conversion takes place in this function
        """
        response = di.sendBlocks(self.buffer, x, y, z, retries)
        if response:
            self.buffer = []

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


def requestBuildArea():
    """**Return the building area**."""
    return di.requestBuildArea()


def requestPlayerArea(dx=128, dz=128):
    """**Return the building area surrounding the player**."""
    # Correcting for offset from player position
    dx -= 1
    dz -= 1
    runCommand("execute at @p run setbuildarea "
               f"~{-dx//2} 0 ~{-dz//2} ~{dx//2} 255 ~{dz//2}")
    return di.requestBuildArea()


# ========================================================= global interface


globalWorldSlice = None
globalDecay = None

globalinterface = Interface()


def makeGlobalSlice():
    global globalWorldSlice
    global globalDecay
    x1, y1, z1, x2, y2, z2 = requestBuildArea()
    globalWorldSlice = WorldSlice(x1, z1, x2, z2)
    globalDecay = np.zeros((x2 - x1, 255, z2 - z1), dtype=bool)


def global2buildlocal(x, y, z):
    """**Convert global coordinates to ones relative to the build area**."""
    x0, y0, z0, _, _, _ = requestBuildArea()
    return x - x0, y - y0, z - z0


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


def getBlock(x, y, z):
    """**Global getBlock**."""
    return globalinterface.getBlock(x, y, z)


def fill(x1, y1, z1, x2, y2, z2, blockStr):
    """**Global fill**."""
    return globalinterface.fill(x1, y1, z1, x2, y2, z2, blockStr)


def setBlock(x, y, z, blockStr):
    """**Global setBlock**."""
    return globalinterface.setBlock(x, y, z, blockStr)

# ----------------------------------------------------- block buffers


def toggleBuffer():
    """**Global toggleBuffer**."""
    return globalinterface.toggleBuffer()


def sendBlocks(x=0, y=0, z=0, retries=5):
    """**Global sendBlocks**."""
    return globalinterface.sendBlocks(x, y, z, retries)
