# ! /usr/bin/python3
"""### Provides tools for reading chunk data.

This module contains functions to:
* Calculate a heightmap ideal for building
* Visualise numpy arrays
"""
__all__ = ['WorldSlice']
__version__ = 'v4.2_dev'

from io import BytesIO
from math import ceil, log2

import direct_interface as di
import nbt
import numpy as np
from bitarray import BitArray
from lookup import BIOMES


class CachedSection:
    """**Represents a cached chunk section (16x16x16)**."""

    def __init__(self, palette, blockStatesBitArray):
        self.palette = palette
        self.blockStatesBitArray = blockStatesBitArray

    # __repr__ displays the class well enough so __str__ is omitted
    def __repr__(self):
        return f"CachedSection({repr(self.palette)}, " \
            f"{repr(self.blockStatesBitArray)})"


class WorldSlice:
    """**Contains information on a slice of the world**."""

    def __init__(self, x1, z1, x2, z2,
                 heightmapTypes=["MOTION_BLOCKING",
                                 "MOTION_BLOCKING_NO_LEAVES",
                                 "OCEAN_FLOOR",
                                 "WORLD_SURFACE"]):
        """**Initialise WorldSlice with region and heightmaps**."""
        self.rect = x1, z1, x2 - x1, z2 - z1
        self.chunkRect = (self.rect[0] >> 4, self.rect[1] >> 4,
                          ((self.rect[0] + self.rect[2] - 1) >> 4)
                          - (self.rect[0] >> 4) + 1,
                          ((self.rect[1] + self.rect[3] - 1) >> 4)
                          - (self.rect[1] >> 4) + 1)
        self.heightmapTypes = heightmapTypes

        bytes = di.getChunks(*self.chunkRect, rtype='bytes')
        file_like = BytesIO(bytes)

        self.nbtfile = nbt.nbt.NBTFile(buffer=file_like)

        rectOffset = [self.rect[0] % 16, self.rect[1] % 16]

        # heightmaps
        self.heightmaps = {}
        for hmName in self.heightmapTypes:
            self.heightmaps[hmName] = np.zeros(
                (self.rect[2] + 1, self.rect[3] + 1), dtype=int)

        # Sections are in x,z,y order!!! (reverse minecraft order :p)
        self.sections = [[[None for i in range(16)] for z in range(
            self.chunkRect[3])] for x in range(self.chunkRect[2])]

        # heightmaps
        for x in range(self.chunkRect[2]):
            for z in range(self.chunkRect[3]):
                chunkID = x + z * self.chunkRect[2]

                hms = self.nbtfile['Chunks'][chunkID]['Level']['Heightmaps']
                for hmName in self.heightmapTypes:
                    # hmRaw = hms['MOTION_BLOCKING']
                    hmRaw = hms[hmName]
                    heightmapBitArray = BitArray(9, 16 * 16, hmRaw)
                    heightmap = self.heightmaps[hmName]
                    for cz in range(16):
                        for cx in range(16):
                            try:
                                heightmap[-rectOffset[0] + x * 16 + cx,
                                          -rectOffset[1] + z * 16 + cz] \
                                    = heightmapBitArray.getAt(cz * 16 + cx)
                            except IndexError:
                                pass

        # sections
        for x in range(self.chunkRect[2]):
            for z in range(self.chunkRect[3]):
                chunkID = x + z * self.chunkRect[2]
                chunk = self.nbtfile['Chunks'][chunkID]
                chunkSections = chunk['Level']['Sections']

                for section in chunkSections:
                    y = section['Y'].value

                    if (not ('BlockStates' in section)
                            or len(section['BlockStates']) == 0):
                        continue

                    palette = section['Palette']
                    rawBlockStates = section['BlockStates']
                    bitsPerEntry = max(4, ceil(log2(len(palette))))
                    blockStatesBitArray = BitArray(bitsPerEntry, 16 * 16 * 16,
                                                   rawBlockStates)

                    self.sections[x][z][y] = CachedSection(palette,
                                                           blockStatesBitArray)

    # __repr__ displays the class well enough so __str__ is omitted
    def __repr__(self):
        """**Represent the WorldSlice as a constructor**."""
        x1, z1 = self.rect[:2]
        x2, z2 = self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]
        return f"WorldSlice{(x1, z1, x2, z2)}"

    def getBlockCompoundAt(self, x, y, z):
        """**Return block data**."""
        chunkX = (x >> 4) - self.chunkRect[0]
        chunkZ = (z >> 4) - self.chunkRect[1]
        chunkY = y >> 4

        cachedSection = self.sections[chunkX][chunkZ][chunkY]

        if cachedSection is None:
            return None  # TODO return air compound instead

        bitarray = cachedSection.blockStatesBitArray
        palette = cachedSection.palette

        blockIndex = (y % 16) * 16 * 16 + \
            (z % 16) * 16 + x % 16
        return palette[bitarray.getAt(blockIndex)]

    def getBlockAt(self, x, y, z):
        """**Return the block's namespaced id at blockPos**."""
        blockCompound = self.getBlockCompoundAt(x, y, z)
        if blockCompound is None:
            return "minecraft:void_air"
        else:
            return blockCompound["Name"].value

    def getBiomeAt(self, x, y, z):
        """**Return biome at given coordinates**.

        Due to the noise around chunk borders,
            there is an inacurracy of +/-2 blocks.
        """
        chunkID = x // 16 + z // 16 * self.chunkRect[2]
        data = self.nbtfile['Chunks'][chunkID]['Level']['Biomes']
        x = (x % 16) // 4
        z = (z % 16) // 4
        y = y // 4
        index = x + 4 * z + 16 * y
        return(BIOMES[data[index]])

    def getBiomesNear(self, x, y, z):
        """**Return a list of biomes in the same chunk**."""
        chunkID = x // 16 + z // 16 * self.chunkRect[2]
        data = self.nbtfile['Chunks'][chunkID]['Level']['Biomes']
        # "sorted(list(set(data)))" is used to remove duplicates from data
        return [BIOMES[i] for i in sorted(list(set(data)))]

    def getPrimaryBiomeNear(self, x, y, z):
        """**Return the most prevelant biome in the same chunk**."""
        chunkID = x // 16 + z // 16 * self.chunkRect[2]
        data = self.nbtfile['Chunks'][chunkID]['Level']['Biomes']
        # "max(set(data), key=data.count)" is used to find the most common item
        data = max(set(data), key=data.count)
        return [BIOMES[i] for i in sorted(list(set(data)))]
