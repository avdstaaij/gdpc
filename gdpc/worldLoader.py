# ! /usr/bin/python3
"""### Provides tools for reading chunk data.

This module contains functions to:
* Calculate a heightmap ideal for building
* Visualise numpy arrays
"""
__all__ = ['WorldSlice']
__version__ = "v5.0"

from io import BytesIO
from math import ceil, log2

import nbt
import numpy as np

from . import direct_interface as di
from .bitarray import BitArray


class CachedSection:
    """**Represents a cached chunk section (16x16x16)**."""

    def __init__(self, x, y, z, blockPalette, blockStatesBitArray, biomesPalette, biomesBitArray):
        self.blockPalette = blockPalette
        self.blockStatesBitArray = blockStatesBitArray
        self.biomesPalette = biomesPalette
        self.biomesBitArray = biomesBitArray
        self.x = x
        self.y = y
        self.z = z

    def getBlockCompoundAtIndex(self, index):
        return self.blockPalette[self.blockStatesBitArray.getAt(index)]

    def getBiomeAtIndex(self, index):
        return self.biomesPalette[self.biomesBitArray.getAt(index)]

    # __repr__ displays the class well enough so __str__ is omitted
    def __repr__(self):
        return f"CachedSection({repr(self.blockPalette)}, " \
               f"{repr(self.blockStatesBitArray)})"


class WorldSlice:
    """**Contains information on a slice of the world**."""

    def __init__(self, x1, z1, x2, z2,
                 heightmapTypes=None):
        """**Initialise WorldSlice with region and heightmaps**.

        x2 and z2 are exclusive
        """
        if heightmapTypes is None:
            heightmapTypes = ["MOTION_BLOCKING",
                              "MOTION_BLOCKING_NO_LEAVES",
                              "OCEAN_FLOOR",
                              "WORLD_SURFACE"]
        self.rect = x1, z1, x2 - x1, z2 - z1
        self.chunkRect = (self.rect[0] >> 4, self.rect[1] >> 4,
                          ((self.rect[0] + self.rect[2] - 1) >> 4)
                          - (self.rect[0] >> 4) + 1,
                          ((self.rect[1] + self.rect[3] - 1) >> 4)
                          - (self.rect[1] >> 4) + 1)
        self.heightmapTypes = heightmapTypes

        chunkBytes = di.getChunks(*self.chunkRect, rtype='bytes')
        file_like = BytesIO(chunkBytes)

        self.nbtfile = nbt.nbt.NBTFile(buffer=file_like)

        rectOffset = [self.rect[0] % 16, self.rect[1] % 16]

        # For each type of heightmap, create a 2D array of zeros in the shape
        # of the build area.
        self.heightmaps = {}
        for hmName in self.heightmapTypes:
            self.heightmaps[hmName] = np.zeros(
                (self.rect[2] + 1, self.rect[3] + 1), dtype=int)

        # For each x-z position in the build area, get the height from the
        # heightmap data from the corresponding chunk for all types of
        # heightmap data.
        for x in range(self.chunkRect[2]):
            for z in range(self.chunkRect[3]):
                chunkID = x + z * self.chunkRect[2]

                hms = self.nbtfile['Chunks'][chunkID]['Heightmaps']
                for hmName in self.heightmapTypes:
                    hmRaw = hms[hmName]
                    heightmapBitArray = BitArray(9, 16 * 16, hmRaw)
                    heightmap = self.heightmaps[hmName]
                    for cz in range(16):
                        for cx in range(16):
                            try:
                                # In the heightmap data the lowest point is
                                # encoded as 0, while since Minecraft 1.18 the
                                # actual lowest y position is below zero at -64.
                                # Subtract 64 from the heightmap value to
                                # compensate for this difference.
                                heightmap[-rectOffset[0] + x * 16 + cx,
                                          -rectOffset[1] + z * 16 + cz] \
                                    = heightmapBitArray.getAt(cz * 16 + cx) - 64
                            except IndexError:
                                pass

        # sections
        # Flat dict of all chunk sections in this world slice
        self.sections = dict()
        for x in range(self.chunkRect[2]):
            for z in range(self.chunkRect[3]):
                chunkID = x + z * self.chunkRect[2]
                chunk = self.nbtfile['Chunks'][chunkID]
                chunkSections = chunk['sections']

                for section in chunkSections:
                    y = section['Y'].value

                    if (not ('block_states' in section)
                            or len(section['block_states']) == 0):
                        continue

                    blockPalette = section['block_states']['palette']
                    blockData = None
                    if 'data' in section['block_states']:
                        blockData = section['block_states']['data']
                    blockPaletteBitsPerEntry = max(4, ceil(log2(len(blockPalette))))
                    blockDataBitArray = BitArray(blockPaletteBitsPerEntry, 16 * 16 * 16, blockData)

                    biomesPalette = section['biomes']['palette']
                    biomesData = None
                    if 'data' in section['biomes']:
                        biomesData = section['biomes']['data']
                    biomesBitsPerEntry = max(1, ceil(log2(len(biomesPalette))))
                    biomesDataBitArray = BitArray(biomesBitsPerEntry, 64, biomesData)

                    self.sections[(x, y, z)] = CachedSection(
                        x, y, z, blockPalette, blockDataBitArray, biomesPalette, biomesDataBitArray
                    )

    # __repr__ displays the class well enough so __str__ is omitted
    def __repr__(self):
        """**Represent the WorldSlice as a constructor**."""
        x1, z1 = self.rect[:2]
        x2, z2 = self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]
        return f"WorldSlice{(x1, z1, x2, z2)}"

    def getChunkSectionPos(self, x, y, z):
        """**Get chunk section x,y,z index from global x, y, z position**"""
        chunkX = (x >> 4) - self.chunkRect[0]
        chunkZ = (z >> 4) - self.chunkRect[1]
        chunkY = y >> 4
        return chunkX, chunkY, chunkZ

    def getBlockCompoundAt(self, x, y, z):
        """**Return block data**."""
        cachedSection = self.sections.get(self.getChunkSectionPos(x, y, z))
        if cachedSection is None:
            return None

        blockIndex = (y % 16) * 16 * 16 + \
                     (z % 16) * 16 + x % 16
        return cachedSection.getBlockCompoundAtIndex(blockIndex)

    def getBlockAt(self, x, y, z):
        """**Return the block's namespaced id at blockPos**."""
        blockCompound = self.getBlockCompoundAt(x, y, z)
        if blockCompound is None:
            return "minecraft:void_air"
        else:
            return blockCompound["Name"].value

    def getBiomeAt(self, x, y, z):
        """**Return biome at given coordinates**."""

        cachedSection = self.sections.get(self.getChunkSectionPos(x, y, z))
        if cachedSection is None:
            return None

        # Constrain pos to inside this chunk, then shift 2 bits since biome data is encoded
        # in groups of 4x4x4 per chunk.
        biomeX = (x % 16) >> 2
        biomeY = (y % 16) >> 2
        biomeZ = (z % 16) >> 2
        biomeIndex = (biomeY << 4) | (biomeZ << 2) | biomeX
        return cachedSection.getBiomeAtIndex(biomeIndex)

    def getPrimaryBiomeNear(self, x, y, z):
        """**Return the most prevelant biome in the same chunk**."""
        cachedSection = self.sections.get(self.getChunkSectionPos(x, y, z))
        if cachedSection is None:
            return None

        # Find and count each biome type for each biome area (a 4x4x4 block) of the chunk.
        foundBiomes = dict()
        for biomeX in range(0, 4):
            for biomeY in range(0, 4):
                for biomeZ in range(0, 4):
                    biomeIndex = (biomeY << 4) | (biomeZ << 2) | biomeX
                    foundBiome: str = cachedSection.getBiomeAtIndex(biomeIndex)
                    if foundBiome not in foundBiomes:
                        foundBiomes[foundBiome] = 1
                    else:
                        foundBiomes[foundBiome] = foundBiomes.get(foundBiome) + 1

        # Return the biome that was found the most.
        return max(foundBiomes, key=foundBiomes.get)
