"""Provides the Model class"""


from typing import Union, Optional, List, Dict
from copy import copy
from glm import ivec3

from .vector_tools import Box
from .transform import TransformLike
from .editor import Editor
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


    def getBlock(self, position: ivec3):
        """Returns the block at [vec]"""
        return self._blocks[(position.x * self._size.y + position.y) * self._size.z + position.z]

    def setBlock(self, position: ivec3, block: Optional[Block]):
        """Sets the block at [vec] to [block]"""
        self._blocks[(position.x * self._size.y + position.y) * self._size.z + position.z] = block


    def build(
        self,
        editor:         Editor,
        transformLike:  Optional[TransformLike]         = None,
        substitutions:  Optional[Dict[str, str]]        = None,
        replace:        Optional[Union[str, List[str]]] = None
    ):
        """Builds the model.

        Use [substitutions] to build the model with certain blocks types replaced by others.
        """
        if substitutions is None: substitutions = {}

        with editor.pushTransform(transformLike):
            for vec in Box(size=self._size).inner:
                block = self.getBlock(vec)
                if block is not None:
                    blockToPlace = copy(block)
                    blockToPlace.id = substitutions.get(block.id, block.id)
                    editor.placeBlock(vec, blockToPlace, replace)

    def __repr__(self):
        return f"Model(size={repr(self.size)}, blocks={repr(self.blocks)})"
