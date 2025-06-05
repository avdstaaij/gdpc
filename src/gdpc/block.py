"""Provides the :class:`.Block` class, which represents a Minecraft block."""


from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Sequence, cast

from nbt import nbt
from pyglm.glm import bvec3

from .block_state_tools import transformAxis, transformFacing, transformHalf, transformRotation
from .nbt_tools import nbtToSnbt


if TYPE_CHECKING:
    from .vector_tools import Vec3bLike


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
    - half
    - rotation

    Other orientation-related block states are currently not supported by the transformation
    system, but support may be added in a future version.
    """

    # TODO: Known orientation-related block states that are currently not supported:
    # - type="bottom"/"top" (e.g. slabs)  (note that slabs can also have type="double"!)

    id:     str | None     = "minecraft:stone" #: Block ID
    states: dict[str, str] = field(default_factory=lambda: cast("dict[str, str]", dict)) #: Block states
    data:   str | None     = None #: Block entity data

    # We explicitly add this method instead of using @dataclass so that it looks better in the docs
    # and we can add a docstring.
    def __init__(
        self,
        id: str | None = "minecraft:stone", # pylint: disable=redefined-builtin
        states: dict[str, str] | None = None,
        data: str | None = None,
    ) -> None:
        """Constructs a Block instance with the given properties."""
        self.id     = id
        self.states = states if states is not None else {}
        self.data   = data


    def transform(self, rotation: int = 0, flip: Vec3bLike | None = None) -> None:
        """Transforms this block.\n
        Flips first, rotates second."""
        if flip is None:
            flip = bvec3()
        axisState     = self.states.get("axis")
        facingState   = self.states.get("facing")
        rotationState = self.states.get("rotation")
        halfState     = self.states.get("half")
        if axisState     is not None: self.states["axis"]     = transformAxis    (axisState,     rotation)
        if facingState   is not None: self.states["facing"]   = transformFacing  (facingState,   rotation, flip)
        if rotationState is not None: self.states["rotation"] = transformRotation(rotationState, rotation, flip)
        if halfState     is not None: self.states["half"]     = transformHalf    (halfState,               flip)


    def transformed(self, rotation: int = 0, flip: Vec3bLike | None = None) -> Block:
        """Returns a transformed copy of this block.\n
        Flips first, rotates second."""
        if flip is None:
            flip = bvec3()
        block = deepcopy(self)
        block.transform(rotation, flip)
        return block


    def stateString(self) -> str:
        """Returns a string containing the block states of this block, including the outer brackets."""
        stateString = ",".join([f"{key}={value}" for key, value in self.states.items()])
        return "" if stateString == "" else f"[{stateString}]"


    def __str__(self) -> str:
        """Returns a string representation in the technical "block state" format.\n
        For example: "minecraft:oak_log[axis=z]"\n
        More info: https://minecraft.wiki/w/Argument_types#block_state."""
        if not self.id:
            return ""
        return self.id + self.stateString() + (self.data if self.data else "")


    def __repr__(self) -> str:
        """Returns a string representation that is guaranteed to `eval()` to this Block."""
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
    def fromBlockStateTag(blockStateTag: nbt.TAG_Compound, blockEntityTag: nbt.TAG_Compound | None = None) -> Block:
        """Parses a block state compound tag (as found in chunk palettes) into a Block.\n
        If ``blockEntityTag`` is provided, it is parsed into the Block's :attr:`.data` attribute."""
        block = Block(str(blockStateTag["Name"]))

        if "Properties" in blockStateTag:
            for tag in cast("list[nbt.TAG_String]", cast("nbt.TAG_Compound", blockStateTag["Properties"]).tags):
                block.states[str(tag.name)] = str(tag.value)

        if blockEntityTag is not None:
            cleanBlockEntityTag = nbt.TAG_Compound()
            for tag in blockEntityTag.tags:
                if tag.name not in {"x", "y", "z", "id", "keepPacked"}:
                    cleanBlockEntityTag.tags.append(tag)
            block.data = nbtToSnbt(cleanBlockEntityTag)

        return block


def transformedBlockOrPalette(block: Block | Sequence[Block], rotation: int, flip: Vec3bLike) -> Block | Sequence[Block]:
    """Convenience function that transforms a block or a palette of blocks."""
    if isinstance(block, Block):
        return block.transformed(rotation, flip)
    return [b.transformed(rotation, flip) for b in block]
