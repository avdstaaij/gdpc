"""Provides the Block class"""


from typing import Any, Union, Optional, Dict, Sequence
from dataclasses import dataclass, field
from copy import copy, deepcopy
import random

from glm import bvec3
from nbt import nbt

from .vector_tools import Vec3bLike
from .nbt_tools import nbtToSnbt
from .block_state_tools import transformAxis, transformFacing, transformRotation


@dataclass
class Block:
    """A Minecraft block.

    Block states can be stored in .states, and block entity data can be stored in .data as an SNBT
    string.

    If .id is an empty string or None, the block represents "nothing". Placing such a block has no
    effect. This is opposed to blocks of air, which do replace existing blocks. Nothing-blocks can
    be useful in block palettes.

    The transform methods modify a number of orientation-related block states. These are:
    - axis
    - facing
    - rotation

    Other orientation-related block states are currently not supported by the transformation
    system, but support may be added in a future version.
    """

    # TODO: Known orientation-related block states that are currently not supported:
    # - type="bottom"/"top" (e.g. slabs)  (note that slabs can also have type="double"!)
    # - half="bottom"/"top" (e.g. stairs) ("half" is also used for other purposes, see e.g. doors)

    id:     Optional[str]  = "minecraft:stone"
    states: Dict[str, str] = field(default_factory=dict)
    data:   Optional[str]  = None


    def transform(self, rotation: int = 0, flip: Vec3bLike = bvec3()):
        """Transforms this block.\n
        Flips first, rotates second."""
        axisState     = self.states.get("axis")
        facingState   = self.states.get("facing")
        rotationState = self.states.get("rotation")
        if axisState     is not None: self.states["axis"]     = transformAxis    (axisState,     rotation)
        if facingState   is not None: self.states["facing"]   = transformFacing  (facingState,   rotation, flip)
        if rotationState is not None: self.states["rotation"] = transformRotation(rotationState, rotation, flip)


    def transformed(self, rotation: int = 0, flip: Vec3bLike = bvec3()):
        """Returns a transformed copy of this block.\n
        Flips first, rotates second."""
        block = deepcopy(self)
        block.transform(rotation, flip)
        return block


    def stateString(self):
        """Returns a string containing the block states of this block, including the outer brackets."""
        stateString = ",".join([f"{key}={value}" for key, value in self.states.items()])
        return "" if stateString == "" else f"[{stateString}]"


    def __str__(self):
        if not self.id:
            return ""
        return self.id + self.stateString() + (self.data if self.data else "")


    def __repr__(self):
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
    def fromBlockStateTag(blockStateTag: nbt.TAG_Compound, blockEntityTag: Optional[nbt.TAG_Compound] = None):
        """Parses a block state compound tag (as found in chunk palettes) into a Block.\n
        If <blockEntityTag> is provided, it is parsed into the Block's .data attribute."""
        block = Block(str(blockStateTag["Name"]))

        if "Properties" in blockStateTag:
            for tag in blockStateTag["Properties"].tags:
                block.states[str(tag.name)] = str(tag.value)

        if blockEntityTag is not None:
            blockEntityTag = deepcopy(blockEntityTag)
            del blockEntityTag["x"]
            del blockEntityTag["y"]
            del blockEntityTag["z"]
            del blockEntityTag["id"]
            del blockEntityTag["keepPacked"]
            block.data = nbtToSnbt(blockEntityTag)

        return block


def transformedBlockOrPalette(block: Union[Block, Sequence[Block]], rotation: int, flip: Vec3bLike):
    """Convenience function that transforms a block or a palette of blocks."""
    if isinstance(block, Block):
        return block.transformed(rotation, flip)
    else:
        return [b.transformed(rotation, flip) for b in block]
