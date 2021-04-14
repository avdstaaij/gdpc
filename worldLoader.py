# ! /usr/bin/python3
"""### Provides tools for reading chunk data

This module contains functions to:
* Calculate a heightmap ideal for building
* Visualise numpy arrays
"""
__all__ = ['WorldSlice']
# __version__

from io import BytesIO
from math import ceil, log2

import nbt
import numpy as np
import requests

from bitarray import BitArray


def getChunks(x, z, dx, dz, rtype='text'):
    """**Get raw chunk data.**"""
    print(f"getting chunks {x} {z} {dx} {dz} ")

    url = f'http://localhost:9000/chunks?x={x}&z={z}&dx={dx}&dz={dz}'
    print(f"request url: {url}")
    acceptType = 'application/octet-stream' if rtype == 'bytes' else 'text/raw'
    response = requests.get(url, headers={"Accept": acceptType})
    print(f"result: {response.status_code}")
    if response.status_code >= 400:
        print(f"error: {response.text}")

    if rtype == 'text':
        return response.text
    elif rtype == 'bytes':
        return response.content


class CachedSection:
    """**Represents a cached chunk section (16x16x16).**"""

    def __init__(self, palette, blockStatesBitArray):
        self.palette = palette
        self.blockStatesBitArray = blockStatesBitArray


class WorldSlice:
    """**Contains information on a slice of the world.**"""
    # TODO format this to blocks

    def __init__(self, rect, heightmapTypes=["MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "WORLD_SURFACE"]):
        self.rect = rect
        self.chunkRect = (rect[0] >> 4, rect[1] >> 4, ((rect[0] + rect[2] - 1) >> 4) - (
            rect[0] >> 4) + 1, ((rect[1] + rect[3] - 1) >> 4) - (rect[1] >> 4) + 1)
        self.heightmapTypes = heightmapTypes

        bytes = getChunks(*self.chunkRect, rtype='bytes')
        file_like = BytesIO(bytes)

        print("parsing NBT")
        self.nbtfile = nbt.nbt.NBTFile(buffer=file_like)

        rectOffset = [rect[0] % 16, rect[1] % 16]

        # heightmaps
        self.heightmaps = {}
        for hmName in self.heightmapTypes:
            self.heightmaps[hmName] = np.zeros(
                (rect[2], rect[3]), dtype=np.int)

        # Sections are in x,z,y order!!! (reverse minecraft order :p)
        self.sections = [[[None for i in range(16)] for z in range(
            self.chunkRect[3])] for x in range(self.chunkRect[2])]

        # heightmaps
        print("extracting heightmaps")

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
                                heightmap[-rectOffset[0] + x * 16 + cx, -rectOffset[1] +
                                          z * 16 + cz] = heightmapBitArray.getAt(cz * 16 + cx)
                            except IndexError:
                                pass

        # sections
        print("extracting chunk sections")

        for x in range(self.chunkRect[2]):
            for z in range(self.chunkRect[3]):
                chunkID = x + z * self.chunkRect[2]
                chunkSections = self.nbtfile['Chunks'][chunkID]['Level']['Sections']

                for section in chunkSections:
                    y = section['Y'].value

                    if not ('BlockStates' in section) or len(section['BlockStates']) == 0:
                        continue

                    palette = section['Palette']
                    rawBlockStates = section['BlockStates']
                    bitsPerEntry = max(4, ceil(log2(len(palette))))
                    blockStatesBitArray = BitArray(
                        bitsPerEntry, 16 * 16 * 16, rawBlockStates)

                    self.sections[x][z][y] = CachedSection(
                        palette, blockStatesBitArray)

        print("done")

    def getBlockCompoundAt(self, blockPos):
        """**Returns block data.**"""
        # chunkID = relativeChunkPos[0] + relativeChunkPos[1] * self.chunkRect[2]

        # section = self.nbtfile['Chunks'][chunkID]['Level']['Sections'][(blockPos[1] >> 4)+1]

        # if not ('BlockStates' in section) or len(section['BlockStates']) == 0:
        #     return -1 # TODO return air compound

        # palette = section['Palette']
        # blockStates = section['BlockStates']
        # bitsPerEntry = max(4, ceil(log2(len(palette))))
        chunkX = (blockPos[0] >> 4) - self.chunkRect[0]
        chunkZ = (blockPos[2] >> 4) - self.chunkRect[1]
        chunkY = blockPos[1] >> 4
        # bitarray = BitArray(bitsPerEntry, 16*16*16, blockStates) # TODO this needs to be 'cached' somewhere
        cachedSection = self.sections[chunkX][chunkZ][chunkY]

        if cachedSection == None:
            return None  # TODO return air compound instead

        bitarray = cachedSection.blockStatesBitArray
        palette = cachedSection.palette

        blockIndex = (blockPos[1] % 16) * 16 * 16 + \
            (blockPos[2] % 16) * 16 + blockPos[0] % 16
        return palette[bitarray.getAt(blockIndex)]

    def getBlockAt(self, blockPos):
        """**Returns the block's namespaced id at blockPos.**"""
        blockCompound = self.getBlockCompoundAt(blockPos)
        if blockCompound == None:
            return "minecraft:air"
        else:
            return blockCompound["Name"].value
