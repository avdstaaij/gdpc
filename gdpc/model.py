"""Provides the Model class"""


from dataclasses import dataclass
from typing import Union, Optional, List, Dict
from copy import copy
from glm import ivec3

from .vector_tools import Box
from .transform import Transform
from .interface import Editor
from .block import Block


class Model:
    """A 3D model of Minecraft blocks.

    Can be used to store a structure in memory, allowing it to be built under different
    transformations.
    """

    def __init__(self, size: ivec3, blocks: Optional[List[Optional[Block]]] = None):
        """Constructs a Model of size [size], optionally filled with [blocks]."""
        self._size = copy(size)
        if blocks is not None:
            if len(blocks) != size.x * size.y * size.z:
                raise ValueError("The number of blocks should be equal to size.x * size.y * size.z")
            self._blocks = copy(blocks)
        else:
            self._blocks = [None] * (size.x * size.y * size.z)


    @property
    def size(self):
        """This Model's size"""
        return copy(self._size)

    @property
    def blocks(self) -> List[Optional[Block]]:
        """This Model's block list"""
        return copy(self._blocks) # Allows block modification, but not resizing


    def block(self, vec: ivec3):
        """Returns the block at [vec]"""
        return self._blocks[(vec.x * self._size.y + vec.y) * self._size.z + vec.z]

    def set_block(self, vec: ivec3, block: Optional[Block]):
        """Sets the block at [vec] to [block]"""
        self._blocks[(vec.x * self._size.y + vec.y) * self._size.z + vec.z] = block


    def build(
        self,
        editor:         Editor,
        transformOrVec: Optional[Union[Transform, ivec3]] = None,
        substitutions:  Optional[Dict[str, str]]          = None,
        replace:        Optional[Union[str, List[str]]]   = None
    ):
        """Builds the model.

        Use [substitutions] to build the model with certain blocks types replaced by others.

        Small limitation: when using [replace], neighbor-dependent blocks such as fences may
        get the wrong shape"""

        # Combining [replace] and late placement is not supported for the following reason:
        # Late-placed blocks need to be placed multiple times to make sure they get the right shape,
        # but if [replace] is used, then every placement after the first one needs to set replace to
        # the namespaced id of late-placed block itself. However, obtaining the namespaced id of the
        # late-placed block is not trivial, since it may be specified as an un-namespaced id.
        # For example, when late-placing "fence" with replacement, every placement after the first
        # would have to replace "<namespace>:fence" (e.g. "minecraft:fence"), but we can't easily
        # figure out what <namespace> needs to be. We could just assume "minecraft", but that might
        # break if other mods are used.

        if substitutions is None: substitutions = {}

        @dataclass
        class LateBlockInfo:
            block:    Block
            position: ivec3

        lateBlocks: List[LateBlockInfo] = []

        with editor.pushTransform(transformOrVec):

            for vec in Box(size=self._size).inner:
                block = self.block(vec)
                if block is not None:
                    blockToPlace = copy(block)
                    blockToPlace.id = substitutions.get(block.id, block.id)
                    if blockToPlace.needsLatePlacement and replace is None:
                        lateBlocks.append(LateBlockInfo(blockToPlace, vec))
                    else:
                        editor.placeBlock(vec, blockToPlace, replace)

            # Place the late blocks, thrice.
            # Yes, placing them three time is really necessary. Wall-type blocks require it.
            for info in lateBlocks:
                editor.placeBlock(info.position, info.block)
            for info in lateBlocks[::-1]:
                editor.placeBlock(info.position, info.block)
            for info in lateBlocks:
                editor.placeBlock(info.position, info.block)


    def __repr__(self):
        return f"Model(size={repr(self.size)}, blocks={repr(self.blocks)})"
