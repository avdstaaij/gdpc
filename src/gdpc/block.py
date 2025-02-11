"""Provides the :class:`.Block` class, which represents a Minecraft block."""


from typing import Any, Union, Optional, Dict, Sequence
from dataclasses import dataclass, field
from copy import copy, deepcopy
import random

from glm import bvec3
from nbt import nbt

from .vector_tools import Vec3bLike
from .nbt_tools import nbtToSnbt
from .block_state_tools import transformAxis, transformFacing, transformRotation, transformHalf


@dataclass
class Block:
    """A Minecraft block.

    Block states can be stored in :attr:`.states`, and block entity data can be stored in
    :attr:`.data` as an SNBT string.

    If :attr:`.id` is an empty string or None, the block represents "nothing". Placing such a block
    has no effect. This is opposed to blocks of air, which do replace existing blocks.
    Nothing-blocks can be useful in block palettes.

    The transform methods modify a number of orientation-related block states. These are:

    - axis
    - facing
    - rotation

    Other orientation-related block states are currently not supported by the transformation
    system, but support may be added in a future version.
    """

    # TODO: Known orientation-related block states that are currently not supported:
    # - type="bottom"/"top" (e.g. slabs)  (note that slabs can also have type="double"!)

    id:     Optional[str]  = "minecraft:stone" #: Block ID
    states: Dict[str, str] = field(default_factory=dict) #: Block states
    data:   Optional[str]  = None #: Block entity data

    # We explicitly add this method instead of using @dataclass so that it looks better in the docs
    # and we can add a docstring.
    def __init__(
        self,
        id: Optional[str] = "minecraft:stone",
        states: Optional[Dict[str, str]] = None,
        data: Optional[str] = None
    ) -> None:
        """Constructs a Block instance with the given properties."""
        self.id     = id
        self.states = states if states is not None else {}
        self.data   = data


    def transform(self, rotation: int = 0, flip: Vec3bLike = bvec3()) -> None:
        """Transforms this block.\n
        Flips first, rotates second."""
        axisState     = self.states.get("axis")
        facingState   = self.states.get("facing")
        rotationState = self.states.get("rotation")
        halfState     = self.states.get("half")
        if axisState     is not None: self.states["axis"]     = transformAxis    (axisState,     rotation)
        if facingState   is not None: self.states["facing"]   = transformFacing  (facingState,   rotation, flip)
        if rotationState is not None: self.states["rotation"] = transformRotation(rotationState, rotation, flip)
        if halfState     is not None: self.states["half"]     = transformHalf    (halfState,               flip)


    def transformed(self, rotation: int = 0, flip: Vec3bLike = bvec3()) -> "Block":
        """Returns a transformed copy of this block.\n
        Flips first, rotates second."""
        block = deepcopy(self)
        block.transform(rotation, flip)
        return block


    def stateString(self) -> str:
        """Returns a string containing the block states of this block, including the outer brackets."""
        stateString = ",".join([f"{key}={value}" for key, value in self.states.items()])
        return "" if stateString == "" else f"[{stateString}]"


    def __str__(self) -> str:
        if not self.id:
            return ""
        return self.id + self.stateString() + (self.data if self.data else "")


    def __repr__(self) -> str:
        # This is used for model dumping; it needs to return a string that eval()'s to this Block.
        # The default repr includes unnecessary default values, which make model dumps way larger
        # than they need to be.
        return (
            f"Block({repr(self.id)}"
            + (f",states={repr(self.states)}" if self.states else "")
            + (f",data={repr(self.data)}"     if self.data   else "")
            + ")"
        )


    @staticmethod
    def fromBlockStateTag(blockStateTag: nbt.TAG_Compound, blockEntityTag: Optional[nbt.TAG_Compound] = None) -> "Block":
        """Parses a block state compound tag (as found in chunk palettes) into a Block.\n
        If ``blockEntityTag`` is provided, it is parsed into the Block's :attr:`.data` attribute."""
        block = Block(str(blockStateTag["Name"]))

        if "Properties" in blockStateTag:
            for tag in blockStateTag["Properties"].tags:
                block.states[str(tag.name)] = str(tag.value)

        if blockEntityTag is not None:
            cleanBlockEntityTag = nbt.TAG_Compound()
            for tag in blockEntityTag.tags:
                if tag.name not in {"x", "y", "z", "id", "keepPacked"}:
                    cleanBlockEntityTag.tags.append(tag)
            block.data = nbtToSnbt(cleanBlockEntityTag)

        return block


def transformedBlockOrPalette(block: Union[Block, Sequence[Block]], rotation: int, flip: Vec3bLike) -> Union[Block, Sequence[Block]]:
    """Convenience function that transforms a block or a palette of blocks."""
    if isinstance(block, Block):
        return block.transformed(rotation, flip)
    else:
        return [b.transformed(rotation, flip) for b in block]
