"""Provides the Block class"""


from typing import Any, Union, Optional, Dict, Sequence
from dataclasses import dataclass, field
from copy import copy, deepcopy
import random

from glm import bvec3
from nbt import nbt

from .vector_tools import Vec3bLike
from .nbt_tools import nbtToPythonObject, pythonObjectToSnbt
from .block_state_tools import transformAxis, transformFacing, transformRotation


@dataclass
class Block:
    """A Minecraft block.

    Block states can be stored in .states, and block entity NBT data can be stored in .data.

    Block entity NBT data should be specified as a JSON-like structure of built-in Python objects
    (dict, list, int, etc.). For example: `{"Key1": [1, 2, 3], "Key2": "foobar"}`

    If .id is a sequence, the instance represents a palette of blocks that share the same
    block states and block entity NBT data.

    If (an element of) .id is an empty string or None, that element represents "no placement":
    placing such a block has no effect.

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

    id:     Union[Optional[str], Sequence[Optional[str]]] = "minecraft:stone"
    states: Dict[str, str]                                = field(default_factory=dict)
    data:   Any                                           = None


    def chooseId(self):
        """Returns a copy of this block with a single ID.\n
        If .id is a sequence, one ID is chosen at random."""
        result = copy(self)
        if not isinstance(self.id, str):
            self.id = random.choice(self.id)
        return result


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


    def dataString(self):
        """Returns this block's block entity NBT data as an SNBT string."""
        return pythonObjectToSnbt(self.data) if self.data else ""


    def __str__(self):
        statesAndData = self.stateString() + self.dataString()
        if isinstance(self.id, str):
            return self.id + statesAndData
        return ",".join(id + statesAndData for id in self.id if id is not None)


    def __repr__(self):
        # This is used for model dumping; it needs to return a string that eval()'s to this Block.
        # The default repr includes unnecessary default values, which make model dumps way larger
        # than they need to be.
        return (
            f"Block({repr(self.id)}"
            + (f",states={repr(self.states)}" if self.states else "")
            + (f",data={repr(self.data)}" if self.data is not None else "")
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
            block.data = nbtToPythonObject(blockEntityTag)
            del block.data['x']
            del block.data['y']
            del block.data['z']
            del block.data['id']
            del block.data['keepPacked']

        return block
