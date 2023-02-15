#!/usr/bin/env python3

"""
Place blocks with block states and block entity data, and use block palettes.
"""

import sys

from glm import ivec2, ivec3

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY, dropY
from gdpc.minecraft_tools import signBlock
from gdpc.editor_tools import placeContainerBlock
from gdpc.geometry import placeBox, placeCuboid


# The minimum build area size in the XZ-plane for this example.
MIN_BUILD_AREA_SIZE = ivec2(6, 9)


# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()


# Check if the editor can connect to the GDMC HTTP interface.
try:
    editor.checkConnection()
except InterfaceConnectionError:
    print(
        f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
        "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
        "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
        f"See {__url__}/README.md for more information."
    )
    sys.exit(1)


# Get the build area.
try:
    buildArea = editor.getBuildArea()
except BuildAreaNotSetError:
    print(
        "Error: failed to get the build area!\n"
        "Make sure to set the build area with the /setbuildarea command in-game.\n"
        "For example: /setbuildarea ~0 0 ~0 ~64 200 ~64"
    )
    sys.exit(1)


# Check if the build area is large enough in the XZ-plane.
if any(dropY(buildArea.size) < MIN_BUILD_AREA_SIZE):
    print(
        "Error: the build area is too small for this example!\n"
        f"It should be at least {tuple(MIN_BUILD_AREA_SIZE)} blocks large in the XZ-plane."
    )
    sys.exit(1)


# Build a floating 5x9 platform in the middle of the build area.
buildRect = buildArea.toRect()
platformRect = buildRect.centeredSubRect((6,9))
placeBox(editor, platformRect.toBox(100,  1), Block("sandstone"))
placeBox(editor, platformRect.toBox(101, 10), Block("air")) # Clear some space


# So far, we have only placed blocks that are defined fully by their id (like "minecraft:stone").
# However, some blocks in Minecraft have additional information attached to them. In general, a
# Minecraft block is defined by:
#
# - Its (namespaced) id. For example: "minecraft:stone".
#   In GDPC, the namespace "minecraft:" can usually be omitted.
#
# - Its *block states* or *block properties*. These are simple key-value properties that usually
#   denote basic variations in the state of a block. For example, a stairs block can be facing
#   in one of six possible directions (north, south, east, west, up, down). GDPC uses the term
#   "block states". Note, however, that the combination (block id, block states) is sometimes also
#   called a "BlockState". Yes, the terminology is confusing.
#   A full list of all block states can be found at https://minecraft.fandom.com/wiki/Block_states.
#
# - Its *block entity data*. A few blocks have particularly complex data attached to them, such as
#   the items in a chest or the text on a sign. Minecraft stores this kind of data in a so-called
#   "block entity" (also known as a "tile entity"). This data is stored in the NBT format (Named
#   Binary Tag), a binary data structure. NBT also has a human-readable text representation called
#   SNBT (Stringified NBT). The GDMC HTTP Interface and GDPC both use this SNBT format.
#   A full list of all blocks with block entities can be found at
#   https://minecraft.fandom.com/wiki/Block_entity.
#   For more information about the NBT and SNBT formats, see
#   https://minecraft.fandom.com/wiki/NBT_format.


# GDPC's Block class represents a Minecraft block, consisting of a block id, optional block states
# and optional block entity data. Here are some examples:

# An oak_log block with the block state axis=z
log = Block("oak_log", {"axis": "z"})

# A stone_brick_stairs block with the block states facing=east and half=top
stairs = Block("stone_brick_stairs", {"facing": "east", "half": "top"})

# A chest block with an apple in the middle slot
chest = Block("chest", data='{Items: [{Slot: 13b, id: "apple", Count: 1b}]}')

# A sign block with the block state rotation=5 and the text "Lorem ipsum"
sign = Block("oak_sign", {"rotation": "5"}, data="{Text1: '{\"text\": \"Lorem ipsum\"}'}")

# Place the blocks on the platform
editor.placeBlock(addY(platformRect.offset) + ivec3(3,101,1), log)
editor.placeBlock(addY(platformRect.offset) + ivec3(3,101,3), stairs)
editor.placeBlock(addY(platformRect.offset) + ivec3(3,101,5), chest)
editor.placeBlock(addY(platformRect.offset) + ivec3(3,101,7), sign)


# The three parts of a block can be accessed using its .id, .states and .data attributes.

print()
print(f"Chest id:     {chest.id}")
print(f"Chest states: {chest.states}")
print(f"Chest data:   {chest.data}")


# Converting a block to a string (or printing it) will yield its in-game string representation
# (as used by, for example, the /setblock command).

print()
print(f"Log:    {log}")      # minecraft:oak_log[axis=z]{}
print(f"Stairs: {stairs}")   # minecraft:stone_brick_stairs[facing=east,half=top]{}
print(f"Chest:  {chest}")    # minecraft:chest{Items: [{Slot: 13b, id: "apple" , Count:1b}]}
print(f"Sign:   {sign}")     # minecraft:oak_sign[rotation=5]{Text1:'{"text": "Lorem ipsum"}'}


# GDPC provides various general-purpose utilities in the minecraft_tools and editor_tools modules
# (the latter contains tools that require an Editor and the former contains tools that don't). These
# include functions to more easily work with certain types of blocks. Here are a few:

sign2 = signBlock(
    "spruce", wall=False, rotation=3,
    line2="Lorem ipsum", line3="dolor sit amet", color="orange", isGlowing=True
)
editor.placeBlock(addY(platformRect.offset) + ivec3(1,101,3), sign2)

placeContainerBlock(
    editor,
    addY(platformRect.offset) + ivec3(1,101,5),
    Block("minecraft:barrel", {"facing": "up"}),
    [((3,1), "wheat"), ((5,1), "egg")]
)


# One more GDPC feature related to blocks is *block palettes*. Most of GDPC's block placing
# functions work not only with a single Block, but also with a sequence of Blocks. If a sequence is
# passed, blocks are sampled randomly. This feature can be extremely useful for building textured
# structures.

# The code below builds a wall using a palette of primarily stone bricks with some cobblestone and
# polished andesite mixed in. The wall will look different every time you run this example.

wallPalette = [Block(id) for id in 3*["stone_bricks"] + ["cobblestone", "polished_andesite"]]

placeCuboid(
    editor,
    addY(platformRect.offset) + ivec3(5,101,0),
    addY(platformRect.offset) + ivec3(5,103,8),
    wallPalette
)
