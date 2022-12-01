"""Provides the Block class"""


from typing import Any, Union, Optional, List
from dataclasses import dataclass
from glm import bvec3

from .block_state_util import transformAxisString, transformFacingString


@dataclass
class Block:
    """A Minecraft block.

    If self.name is a list, the instance represents a block palette.

    Block state can be stored in [otherState], and NBT data can be stored in [nbt] (excluding
    the outer braces).

    Some orientation-related block states need to be stored in explicitly named fields to ensure
    that the Block transforms correctly. These are:
    - axis
    - facing

    Other orientation-related block states are currently not supported by the transformation
    system."""

    # TODO: Known orientation-related block states that are currently not supported:
    # - type="bottom"/"top" (e.g. slabs)  (note that slabs can also have type="double"!)
    # - half="bottom"/"top" (e.g. stairs) ("half" is also used for other purposes, see e.g. doors)
    # - rotation=[0,16]     (e.g. signs)  (should probably be named "granularRotation" here to avoid confusion)

    name:       Union[str, List[str]] = "minecraft:stone"
    axis:       Optional[str]         = None
    facing:     Optional[str]         = None
    otherState: Optional[str]         = None
    nbt:        Optional[str]         = None
    needsLatePlacement: bool          = False # Whether the block needs to be placed after its neighbors


    def transform(self, rotation: int = 0, flip: bvec3 = bvec3()):
        """Transforms this block.\n
        Flips first, rotates second."""
        if not self.axis   is None: self.axis   = transformAxisString  (self.axis,   rotation)
        if not self.facing is None: self.facing = transformFacingString(self.facing, rotation, flip)


    def transformed(self, rotation: int = 0, flip: bvec3 = bvec3()):
        """Returns a transformed copy of this block.\n
        Flips first, rotates second."""
        return Block(
            name       = self.name,
            axis       = None if self.axis   is None else transformAxisString  (self.axis,   rotation),
            facing     = None if self.facing is None else transformFacingString(self.facing, rotation, flip),
            otherState = self.otherState,
            nbt        = self.nbt,
            needsLatePlacement = self.needsLatePlacement
        )


    def blockStateString(self, rotation: int = 0, flip: bvec3 = bvec3()):
        """Returns a string containing the block state of this block"""

        if self.axis is None and self.facing is None and self.otherState is None:
            return ""

        stateItems = []
        if not self.axis       is None: stateItems.append("axis="   + transformAxisString  (self.axis,   rotation))
        if not self.facing     is None: stateItems.append("facing=" + transformFacingString(self.facing, rotation, flip))
        if not self.otherState is None: stateItems.append(self.otherState)
        return "[" + ",".join(stateItems) + "]"


    def __str__(self):
        data_string = self.blockStateString() + (self.nbt if self.nbt else "")
        if isinstance(self.name, str):
            return "" if self.name == "" else self.name + data_string
        return ",".join([(name if name == "" else name + data_string) for name in self.name])


    def __repr__(self):
        # This is used for model dumping; it needs to return a string that eval()'s to this Block.
        # The default repr includes unnecessary default values, which make model dumps way larger
        # than they need to be.
        def optFieldStr(name: str, value: Any):
            return ("" if value is None else f",{name}={repr(value)}")
        return (
            f'Block("{self.name}"'
            + optFieldStr("axis",       self.axis)
            + optFieldStr("facing",     self.facing)
            + optFieldStr("otherState", self.otherState)
            + optFieldStr("nbt",        self.nbt)
            + (",needsLatePlacement=True" if self.needsLatePlacement else "")
            + ")"
        )


    @staticmethod
    def fromBlockCompound(blockCompound, rotation: int = 0, flip: bvec3 = bvec3()):
        """Parses a block compound into a Block."""
        # TODO: parse NBT data
        block = Block(str(blockCompound["Name"]))
        if "Properties" in blockCompound:
            properties = blockCompound["Properties"]
            stateItems = []
            for key in properties:
                value = str(properties[key])
                if key in ["shape", "north", "east", "south", "west"]:
                    # This is a late property. We drop it, but set needs_late_placement to True
                    block.needsLatePlacement = True
                elif key == "axis":
                    block.axis = value
                elif key == "facing":
                    block.facing = value
                else:
                    stateItems.append(str(key) + "=" + value)
            if stateItems:
                block.otherState = ",".join(stateItems)

        block.transform(rotation, flip)

        return block
