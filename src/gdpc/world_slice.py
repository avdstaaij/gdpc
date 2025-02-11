"""Provides the :class:`.WorldSlice` class"""

from typing import Dict, Iterable, Optional
from dataclasses import dataclass
from io import BytesIO
from math import floor, ceil, log2

from glm import ivec2, ivec3
from nbt import nbt
from nbt.nbt import TAG_Compound
import numpy as np

from .vector_tools import Vec3iLike, addY, loop2D, loop3D, trueMod2D, Rect, Box
from .block import Block
from . import interface


# Chunk format information:
# https://minecraft.wiki/Chunk_format


class _BitArray:
    """Store an array of binary values and its metrics.

    Minecraft stores block and heightmap data in compacted arrays of longs (bitarrays).
    This class performs index mapping and bit shifting to access the data.
    """

    def __init__(self, bitsPerEntry: int, logicalArraySize: int, data) -> None:
        """Initialise a BitArray."""
        self._logicalArraySize = logicalArraySize
        self._bitsPerEntry     = bitsPerEntry
        self._entriesPerLong   = 64 // bitsPerEntry
        self._maxEntryValue    = (1 << bitsPerEntry) - 1
        if data is None:
            self.longArray = []
        else:
            expectedLongCount = floor((logicalArraySize + self._entriesPerLong - 1) / self._entriesPerLong)
            if len(data) != expectedLongCount:
                raise ValueError(f"Invalid data length: got {len(data)} but expected {expectedLongCount}")
            self.longArray = data

    def __repr__(self) -> str:
        """Represents the BitArray as a constructor."""
        return f"BitArray{(self._bitsPerEntry, self._logicalArraySize, self.longArray)}"

    def __getitem__(self, index: int) -> int:
        """Returns the binary value stored at ``index``."""
        # If longArray size is 0, this is because the corresponding palette
        # only contains a single value.
        if len(self.longArray) == 0:
            return 0
        longIndex = index // self._entriesPerLong
        long = self.longArray[longIndex]
        k = (index - longIndex * self._entriesPerLong) * self._bitsPerEntry
        return long >> k & self._maxEntryValue

    def __len__(self) -> int:
        """Returns the logical array size."""
        return self._logicalArraySize


@dataclass
class _ChunkSection:
    """Represents a chunk section or sub-chunk (16x16x16)."""

    blockPalette:        nbt.TAG_List
    blockStatesBitArray: _BitArray
    biomesPalette:       nbt.TAG_List
    biomesBitArray:      _BitArray

    def getBlockStateTagAtIndex(self, index) -> nbt.TAG_Compound:
        return self.blockPalette[self.blockStatesBitArray[index]]

    def getBiomeAtIndex(self, index) -> nbt.TAG_String:
        return self.biomesPalette[self.biomesBitArray[index]]


class WorldSlice:
    """Contains information on a slice of the world."""

    def __init__(self, rect: Rect, dimension: Optional[str] = None, heightmapTypes: Optional[Iterable[str]] = None, retries=0, timeout=None, host=interface.DEFAULT_HOST) -> None:
        """Load a world slice.

        If ``heightmapTypes`` is None, all heightmaps are loaded.
        """

        # To protect from calling this with a Box, which can lead to very confusing bugs.
        if not isinstance(rect, Rect):
            raise TypeError(f"<rect> should be a Rect, not a {type(rect)}")

        if heightmapTypes is None:
            heightmapTypes = [
                "MOTION_BLOCKING",
                "MOTION_BLOCKING_NO_LEAVES",
                "OCEAN_FLOOR",
                "WORLD_SURFACE"
            ]

        self._rect = rect
        self._chunkRect = Rect(
            self._rect.offset >> 4,
            ((self._rect.last) >> 4) - (self._rect.offset >> 4) + 1
        )

        chunkBytes = interface.getChunks(self._chunkRect.offset, self._chunkRect.size, dimension=dimension, asBytes=True, retries=retries, timeout=timeout, host=host)
        chunkBuffer = BytesIO(chunkBytes)

        self._nbt = nbt.NBTFile(buffer=chunkBuffer)

        self._heightmaps: Dict[str, np.ndarray] = {}
        for hmName in heightmapTypes:
            self._heightmaps[hmName] = np.zeros(self._rect.size, dtype=int)

        self._sections: Dict[ivec3, _ChunkSection] = {}

        self._blockEntities: Dict[ivec3, nbt.TAG_Compound] = {}

        inChunkRectOffset = trueMod2D(self._rect.offset, 16)

        # This assumes that the build bounds are the same for every chunk.
        self._yBegin = 16 * int(self._nbt["Chunks"][0]["yPos"].value)
        self._ySize  = 16 * len(self._nbt["Chunks"][0]["sections"])

        # Loop through chunks
        for chunkPos in loop2D(self._chunkRect.size):
            chunkID = chunkPos.x + chunkPos.y * self._chunkRect.size.x
            chunkTag = self._nbt['Chunks'][chunkID]

            # Read heightmaps
            heightmapsTag = chunkTag['Heightmaps']
            for hmName in heightmapTypes:
                hmRaw = heightmapsTag[hmName]
                hmBitsPerEntry = max(1, ceil(log2(self._ySize)))
                hmBitArray = _BitArray(hmBitsPerEntry, 16*16, hmRaw)
                heightmap = self._heightmaps[hmName]
                for inChunkPos in loop2D(ivec2(16,16)):
                    try:
                        # In the heightmap data, the lowest point is encoded as 0, while since
                        # Minecraft 1.18 the actual lowest y position is below zero. We subtract
                        # yBegin from the heightmap value to compensate for this difference.
                        hmPos = -inChunkRectOffset + chunkPos * 16 + inChunkPos # pylint: disable=invalid-unary-operand-type
                        heightmap[hmPos.x, hmPos.y] = hmBitArray[inChunkPos.y * 16 + inChunkPos.x] + self._yBegin
                    except IndexError:
                        pass

            # Read chunk sections
            for sectionTag in chunkTag['sections']:
                y = int(sectionTag['Y'].value)

                if (not ('block_states' in sectionTag) or len(sectionTag['block_states']) == 0):
                    continue

                blockPalette = sectionTag['block_states']['palette']
                blockData = None
                if 'data' in sectionTag['block_states']:
                    blockData = sectionTag['block_states']['data']
                blockPaletteBitsPerEntry = max(4, ceil(log2(len(blockPalette))))
                blockDataBitArray = _BitArray(blockPaletteBitsPerEntry, 16*16*16, blockData)

                biomesPalette = sectionTag['biomes']['palette']
                biomesData = None
                if 'data' in sectionTag['biomes']:
                    biomesData = sectionTag['biomes']['data']
                biomesBitsPerEntry = max(1, ceil(log2(len(biomesPalette))))
                biomesDataBitArray = _BitArray(biomesBitsPerEntry, 64, biomesData)

                self._sections[addY(chunkPos, y)] = _ChunkSection(
                    blockPalette, blockDataBitArray, biomesPalette, biomesDataBitArray
                )

            # Read block entities
            if 'block_entities' in chunkTag:
                for blockEntityTag in chunkTag['block_entities']:
                    blockEntityPos = ivec3(
                        blockEntityTag['x'].value,
                        blockEntityTag['y'].value,
                        blockEntityTag['z'].value
                    )
                    self._blockEntities[blockEntityPos] = blockEntityTag


    def __repr__(self) -> str:
        return f"WorldSlice{repr(self._rect)}"


    @property
    def rect(self) -> Rect:
        """The Rect of block coordinates this WorldSlice covers."""
        return self._rect

    @property
    def chunkRect(self) -> Rect:
        """The Rect of chunk coordinates this WorldSlice covers."""
        return self._chunkRect

    @property
    def yBegin(self) -> int:
        """The minimum block y coordinate."""
        return self._yBegin

    @property
    def yEnd(self) -> int:
        """The maximum block y coordinate (exclusive); the "build height" plus one."""
        return self._yBegin + self._ySize

    @property
    def ySize(self) -> int:
        """The amount of blocks in the Y-axis."""
        return self._ySize

    @property
    def box(self) -> Box:
        """The Box of block coordinates this WorldSlice covers."""
        return self._rect.toBox(offsetY=self._yBegin, sizeY=self._ySize)

    @property
    def nbt(self) -> nbt.NBTFile:
        """The parsed NBT data for the chunks of this WorldSlice.\n
        Its structure is described in the GDMC HTTP interface API."""
        return self._nbt

    @property
    def heightmaps(self) -> Dict[str, np.ndarray]:
        """The heightmaps of this WorldSlice."""
        return self._heightmaps


    def getChunkSectionPositionGlobal(self, blockPosition: Vec3iLike) -> ivec3:
        """Returns the local position of the chunk section that contains the global ``blockPosition``."""
        return (ivec3(*blockPosition) >> 4) - addY(self._chunkRect.offset)

    def getChunkSectionPosition(self, blockPosition: Vec3iLike) -> ivec3:
        """Returns the local position of the chunk section that contains the local ``blockPosition``."""
        return self.getChunkSectionPositionGlobal(ivec3(*blockPosition) + addY(self._rect.offset))


    def _getChunkSectionGlobal(self, blockPosition: Vec3iLike) -> Optional[_ChunkSection]:
        """Returns the chunk section that contains the global ``blockPosition``."""
        return self._sections.get(self.getChunkSectionPositionGlobal(blockPosition))


    def getBlockStateTagGlobal(self, position: Vec3iLike) -> Optional[TAG_Compound]:
        """Returns the block state compound tag at global ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns None."""
        chunkSection = self._getChunkSectionGlobal(position)
        if chunkSection is None:
            return None
        blockIndex = (
            (position[1] % 16) * 16 * 16 +
            (position[2] % 16) * 16 +
            (position[0] % 16)
        )
        return chunkSection.getBlockStateTagAtIndex(blockIndex)

    def getBlockStateTag(self, position: Vec3iLike) -> Optional[TAG_Compound]:
        """Returns the block state compound tag at local ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns None."""
        return self.getBlockStateTagGlobal(ivec3(*position) + addY(self._rect.offset))


    def getBlockGlobal(self, position: Vec3iLike) -> Block:
        """Returns the block at global ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns Block("minecraft:void_air")."""
        blockStateTag = self.getBlockStateTagGlobal(position)
        if blockStateTag is None:
            return Block("minecraft:void_air")
        blockEntityTag = self._blockEntities.get(ivec3(*position))
        return Block.fromBlockStateTag(blockStateTag, blockEntityTag)

    def getBlock(self, position: Vec3iLike) -> Block:
        """Returns the block at local ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns Block("minecraft:void_air")."""
        return self.getBlockGlobal(ivec3(*position) + addY(self._rect.offset))


    def getBiomeGlobal(self, position: Vec3iLike) -> str:
        """Returns the namespaced id of the biome at global ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns an empty string.\n
        Note that Minecraft stores biomes in groups of 4x4x4 blocks. This function returns the
        biome of ``position``'s group."""
        chunkSection = self._getChunkSectionGlobal(position)
        if chunkSection is None:
            return ""
        # Constrain pos to inside this chunk, then shift 2 bits since biome data is encoded
        # in 64 groups of 4x4x4 per chunk.
        biomePos = ivec3(
            (position[0] % 16) >> 2,
            (position[1] % 16) >> 2,
            (position[2] % 16) >> 2
        )
        biomeIndex = (biomePos.y << 4) | (biomePos.z << 2) | biomePos.x # pylint: disable=unsupported-binary-operation
        return str(chunkSection.getBiomeAtIndex(biomeIndex).value)

    def getBiome(self, position: Vec3iLike) -> str:
        """Returns the namespaced id of the biome at local ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns an empty string.\n
        Note that Minecraft stores biomes in groups of 4x4x4 blocks. This function returns the
        biome of ``position``'s group."""
        return self.getBiomeGlobal(ivec3(*position) + addY(self._rect.offset))


    def getBiomeCountsInChunkGlobal(self, position: Vec3iLike) -> Optional[Dict[str, int]]:
        """Returns a dict of biomes in the same chunk as the global ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns None.\n
        Minecraft stores biomes in groups of 4x4x4 blocks. The returned dict maps the namespaced id
        of a biome to the number of groups with that biome in the chunk."""
        chunkSection = self._getChunkSectionGlobal(position)
        if chunkSection is None:
            return None
        biomeCounts: Dict[str, int] = dict()
        for biomePos in loop3D(ivec3(4,4,4)):
            biomeIndex = (biomePos.y << 4) | (biomePos.z << 2) | biomePos.x
            biome = str(chunkSection.getBiomeAtIndex(biomeIndex).value)
            biomeCounts[biome] = biomeCounts.get(biome, 0) + 1
        return biomeCounts

    def getBiomeCountsInChunk(self, position: Vec3iLike) -> Optional[Dict[str, int]]:
        """Returns a dict of biomes in the same chunk as the local ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns None.\n
        Minecraft stores biomes in groups of 4x4x4 blocks. The returned dict maps the namespaced id
        of a biome to the number of groups with that biome in the chunk."""
        return self.getBiomeCountsInChunkGlobal(ivec3(*position) + addY(self._rect.offset))


    def getPrimaryBiomeInChunkGlobal(self, position: Vec3iLike) -> Optional[str]:
        """Returns the most prevalent biome in the same chunk as the global ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns None."""
        foundBiomes = self.getBiomeCountsInChunkGlobal(position)
        biome: str = max(foundBiomes.keys(), key=foundBiomes.get)
        return biome

    def getPrimaryBiomeInChunk(self, position: Vec3iLike) -> Optional[str]:
        """Returns the most prevalent biome in the same chunk as the local ``position``.\n
        If ``position`` is not contained in this WorldSlice, returns None."""
        return self.getPrimaryBiomeInChunkGlobal(ivec3(*position) + addY(self._rect.offset))
