"""Provides the :class:`.Model` class, which can store a model of Minecraft blocks."""


from __future__ import annotations

from typing import Union, Optional, List, Dict
from copy import copy
from glm import ivec3

from .vector_tools import Vec3iLike, Box
from .transform import TransformLike
from .editor import Editor
from .block import Block


class Model:
    """A 3D model of Minecraft blocks.

    Can be used to store a structure in memory, allowing it to be built under different
    transformations.
    """

    def __init__(self, size: Vec3iLike, blocks: Optional[List[Optional[Block]]] = None) -> None:
        """Constructs a Model of size ``size``, optionally filled with ``blocks``."""
        self._size = ivec3(*size)
        volume = self._size.x * self._size.y * self._size.z
        if blocks is not None:
            if len(blocks) != volume:
                raise ValueError("The number of blocks should be equal to size[0] * size[1] * size[2]")
            self._blocks = copy(blocks)
        else:
            self._blocks = [None] * volume


    @property
    def size(self) -> ivec3:
        """This Model's size"""
        return copy(self._size)

    @property
    def blocks(self) -> List[Optional[Block]]:
        """This Model's block list"""
        return copy(self._blocks) # Allows block modification, but not resizing


    def getBlock(self, position: Vec3iLike) -> Optional[Block]:
        """Returns the block at ``vec``"""
        return self._blocks[(position[0] * self._size.y + position[1]) * self._size.z + position[2]]

    def setBlock(self, position: Vec3iLike, block: Optional[Block]) -> None:
        """Sets the block at ``vec`` to ``block``"""
        self._blocks[(position[0] * self._size.y + position[1]) * self._size.z + position[2]] = block


    def build(
        self,
        editor:         Editor,
        transformLike:  Optional[TransformLike]         = None,
        substitutions:  Optional[Dict[str, str]]        = None,
        replace:        Optional[Union[str, List[str]]] = None
    ) -> None:
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
