"""Provides the Block class"""


from typing import Any, Union, Optional, List, Dict, Sequence
from dataclasses import dataclass, field
from copy import copy, deepcopy
import random

from glm import bvec3

from .block_state_util import transformAxis, transformFacing, transformRotation


@dataclass
class Block:
    """A Minecraft block.

    Block states can be stored in .states, and block entity SNBT data can be stored in .data
    (excluding the outer braces).

    If .id is a sequence, the instance represents a palette of blocks that share the same
    block states and SNBT data.

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

    id:     Union[str, Sequence[str]] = "minecraft:stone"
    states: Dict[str, str]            = field(default_factory=dict)
    data:   Optional[str]             = None
    needsLatePlacement: bool  = False # Whether the block needs to be placed after its neighbors


    def chooseId(self):
        """Returns a copy of this block with a single ID.\n
        If .id is a sequence, one ID is chosen at random."""
        result = copy(self)
        if not isinstance(self.id, str):
            self.id = random.choice(self.id)
        return result


    def transform(self, rotation: int = 0, flip: bvec3 = bvec3()):
        """Transforms this block.\n
        Flips first, rotates second."""
        axisState     = self.states.get("axis")
        facingState   = self.states.get("facing")
        rotationState = self.states.get("rotation")
        if axisState     is not None: self.states["axis"]     = transformAxis  (axisState,   rotation)
        if facingState   is not None: self.states["facing"]   = transformFacing(facingState, rotation, flip)
        if rotationState is not None: self.states["rotation"] = transformRotation(rotationState, rotation, flip)


    def transformed(self, rotation: int = 0, flip: bvec3 = bvec3()):
        """Returns a transformed copy of this block.\n
        Flips first, rotates second."""
        block = deepcopy(self)
        block.transform(rotation, flip)
        return block


    def blockStateString(self, rotation: int = 0, flip: bvec3 = bvec3()):
        """Returns a string containing the block states of this block, including the outer brackets."""
        stateString = ",".join([f"{key}={value}" for key, value in self.states.items()])
        return "" if stateString == "" else f"[{stateString}]"


    def __str__(self):
        dataStr = self.blockStateString() + (f"{{{self.data}}}" if self.data else "")
        if isinstance(self.id, str):
            return "" if self.id == "" else self.id + dataStr
        return ",".join([(name if name == "" else name + dataStr) for name in self.id])


    def __repr__(self):
        # This is used for model dumping; it needs to return a string that eval()'s to this Block.
        # The default repr includes unnecessary default values, which make model dumps way larger
        # than they need to be.
        return (
            f"Block({repr(self.id)}"
            + (f",states={repr(self.states)}" if self.states else "")
            + (f",data={repr(self.data)}" if self.data else "")
            + (",needsLatePlacement=True" if self.needsLatePlacement else "")
            + ")"
        )


    @staticmethod
    def fromBlockCompound(blockCompound, rotation: int = 0, flip: bvec3 = bvec3()):
        """Parses a block compound into a Block."""
        # TODO: parse block entity NBT data
        block = Block(str(blockCompound["Name"]))
        if "Properties" in blockCompound:
            properties = blockCompound["Properties"]
            for key in properties:
                value = str(properties[key])
                if key in ["shape", "north", "east", "south", "west"]:
                    # This is a late property. We drop it, but set needs_late_placement to True
                    block.needsLatePlacement = True
                else:
                    block.states[str(key)] = value

        block.transform(rotation, flip)

        return block
