#!/usr/bin/env python3

"""### Generate a simple example village.

This file contains a comprehensive collection of functions designed
to introduce new coders to the GDMC HTTP client in Python.

The source code of this module contains examples for:
* How to structure a file neatly (search 'STRUCTURE')
* Requesting the build area (search 'BUILDAREA')
* Introduction to world slices (search 'WORLDSLICE')
* Introduction to basic heightmaps (search 'HEIGHTMAP')
* Introduction to basic geometric shapes (search 'GEO')

NOTE: We recommend creating your own files instead of modifying or adding code
    to these pre-existing files.
NOTE: If part of the program is running to fast for you to understand, insert
    >>> from time import sleep
    and
    >>> sleep(0.1)
    at the appropriate locations for a delay of 1/10 of a second
    Alternatively, inserting
    >>> input("Waiting for user to press [Enter]")
    will pause the program at the point.
NOTE: This file will only be updated in the case of breaking changes
    and will not showcase new features!

INFO: Should you have any questions regarding this software, feel free to visit
    the #ℹ-framework-support channel on the GDMC Discord Server
    (Invite link: https://discord.gg/V9MW65bD)

This file is not meant to be imported.
"""

# === STRUCTURE #1
# These are the modules (libraries) we will use in this code
# We are giving these modules shorter, but distinct, names for convenience
from random import randint

from glm import ivec3

from gdpc.block import Block
from gdpc import vector_util as VU
from gdpc import geometry as GEO
from gdpc import interface as ITF
from gdpc import toolbox as TB
from gdpc import interface_toolbox as ITB
from gdpc import worldLoader as WL


# === STRUCTURE #2
# These variables are global and can be read from anywhere in the code
# I like to write them in capitals so I know they're global
# NOTE: if you want to change this value inside one of your functions,
#   you'll have to add a line of code. For an example search 'GLOBAL'

# Here we read start and end coordinates of our build area
BUILD_AREA = ITF.getBuildArea()  # BUILDAREA
STARTX, STARTY, STARTZ = BUILD_AREA.begin
ENDX, ENDY, ENDZ = BUILD_AREA.end

# Here we construct an Interface object
ED = ITF.Editor()

# WORLDSLICE
# Using the start and end coordinates we are generating a world slice
# It contains all manner of information, including heightmaps and biomes
# For further information on what information it contains, see
#     https://minecraft.fandom.com/wiki/Chunk_format
#
# IMPORTANT: Keep in mind that a wold slice is a 'snapshot' of the world,
#   and any changes you make later on will not be reflected in the world slice
WORLDSLICE = WL.WorldSlice(STARTX, STARTZ, ENDX, ENDZ)  # this takes a while

ROADHEIGHT = 0

# === STRUCTURE #3
# Here we are defining all of our functions to keep our code organised
# They are:
# - buildPerimeter()
# - buildRoads()
# - buildCity()


def buildPerimeter():
    """Build a wall along the build area border.

    In this function we're building a simple wall around the build area
        pillar-by-pillar, which means we can adjust to the terrain height
    """
    # HEIGHTMAP
    # Heightmaps are an easy way to get the uppermost block at any coordinate
    # There are four types available in a world slice:
    # - 'WORLD_SURFACE': The top non-air blocks
    # - 'MOTION_BLOCKING': The top blocks with a hitbox or fluid
    # - 'MOTION_BLOCKING_NO_LEAVES': Like MOTION_BLOCKING but ignoring leaves
    # - 'OCEAN_FLOOR': The top solid blocks
    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    print("Building east-west walls...")
    # building the east-west walls

    for x in range(STARTX, ENDX + 1):
        # the northern wall
        y = heights[(x - STARTX, 0)]
        GEO.placeCuboid(ED, ivec3(x, y - 2, STARTZ), ivec3(x, y, STARTZ), Block("granite"))
        GEO.placeCuboid(ED, ivec3(x, y + 1, STARTZ), ivec3( x, y + 4, STARTZ), Block("granite_wall"))
        # the southern wall
        y = heights[(x - STARTX, ENDZ - STARTZ)]
        GEO.placeCuboid(ED, ivec3(x, y - 2, ENDZ), ivec3( x, y, ENDZ), Block("red_sandstone"))
        GEO.placeCuboid(ED, ivec3(x, y + 1, ENDZ), ivec3( x, y + 4, ENDZ), Block("red_sandstone_wall"))

    print("Building north-south walls...")
    # building the north-south walls
    for z in range(STARTZ, ENDZ + 1):
        # the western wall
        y = heights[(0, z - STARTZ)]
        GEO.placeCuboid(ED, ivec3(STARTX, y - 2, z), ivec3( STARTX, y, z), Block("sandstone"))
        GEO.placeCuboid(ED, ivec3(STARTX, y + 1, z), ivec3( STARTX, y + 4, z), Block("sandstone_wall"))
        # the eastern wall
        y = heights[(ENDX - STARTX, z - STARTZ)]
        GEO.placeCuboid(ED, ivec3(ENDX, y - 2, z), ivec3( ENDX, y, z), Block("prismarine"))
        GEO.placeCuboid(ED, ivec3(ENDX, y + 1, z), ivec3( ENDX, y + 4, z), Block("prismarine_wall"))


def buildRoads():
    """Build a road from north to south and east to west."""
    xaxis = STARTX + (ENDX - STARTX) // 2  # getting start + half the length
    zaxis = STARTZ + (ENDZ - STARTZ) // 2
    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    print("Calculating road height...")
    # caclulating the average height along where we want to build our road
    y = heights[(xaxis - STARTX, zaxis - STARTZ)]
    for x in range(STARTX, ENDX + 1):
        newy = heights[(x - STARTX, zaxis - STARTZ)]
        y = (y + newy) // 2
    for z in range(STARTZ, ENDZ + 1):
        newy = heights[(xaxis - STARTX, z - STARTZ)]
        y = (y + newy) // 2

    # GLOBAL
    # By calling 'global ROADHEIGHT' we allow writing to ROADHEIGHT
    # If 'global' is not called, a new, local variable is created
    global ROADHEIGHT
    ROADHEIGHT = y

    print("Building east-west road...")
    # building the east-west road
    GEO.placeCuboid(ED, ivec3(xaxis - 2, y, STARTZ), ivec3(xaxis - 2, y, ENDZ), Block("end_stone_bricks"))
    GEO.placeCuboid(ED, ivec3(xaxis - 1, y, STARTZ), ivec3(xaxis + 1, y, ENDZ), Block("gold_block"))
    GEO.placeCuboid(ED, ivec3(xaxis + 2, y, STARTZ), ivec3(xaxis + 2, y, ENDZ), Block("end_stone_bricks"))
    GEO.placeCuboid(ED, ivec3(xaxis - 1, y + 1, STARTZ), ivec3(xaxis + 1, y + 3, ENDZ), Block("air"))

    print("Building north-south road...")
    # building the north-south road
    GEO.placeCuboid(ED, ivec3(STARTX, y, zaxis - 2), ivec3(ENDX, y, zaxis - 2), Block("end_stone_bricks"))
    GEO.placeCuboid(ED, ivec3(STARTX, y, zaxis - 1), ivec3(ENDX, y, zaxis + 1), Block("gold_block"))
    GEO.placeCuboid(ED, ivec3(STARTX, y, zaxis + 2), ivec3(ENDX, y, zaxis + 2), Block("end_stone_bricks"))
    GEO.placeCuboid(ED, ivec3(STARTX, y + 1, zaxis - 1), ivec3(ENDX, y + 3, zaxis + 1), Block("air"))


def buildCity():
    xaxis = STARTX + (ENDX - STARTX) // 2  # getting center
    zaxis = STARTZ + (ENDZ - STARTZ) // 2
    y = ROADHEIGHT

    print("Building city platform...")
    # Building a platform and clearing a dome for the city to sit in
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y, zaxis), 1, 21, Block("end_stone_bricks"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y, zaxis), 1, 20, Block("gold_block"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 1, zaxis), 3, 20, Block("air"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 4, zaxis), 2, 19, Block("air"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 6, zaxis), 1, 18, Block("air"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 7, zaxis), 1, 17, Block("air"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 8, zaxis), 1, 15, Block("air"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 9, zaxis), 1, 12, Block("air"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 10, zaxis), 1, 8, Block("air"))
    GEO.placeCenteredCylinder(ED, ivec3(xaxis, y + 11, zaxis), 1, 3, Block("air"))

    for i in range(50):
        buildTower(randint(xaxis - 20, xaxis + 20),
                   randint(zaxis - 20, zaxis + 20))

    # Place a book on a Lectern
    # See the wiki for book formatting codes
    ED.placeBlock(ivec3(xaxis, y, zaxis), Block("emerald_block"))
    bookData = TB.writeBook("This book has a page!")
    ITB.placeLectern(ED, xaxis, y + 1, zaxis, bookData)


def buildTower(x, z):
    radius = 3
    y = ROADHEIGHT

    print(f"Building tower at {x}, {z}...")
    # if the blocks to the north, south, east and west aren't all gold
    if not (
            ED.getBlock(ivec3(x - radius, y, z)).id == "minecraft:gold_block"
        and ED.getBlock(ivec3(x + radius, y, z)).id == "minecraft:gold_block"
        and ED.getBlock(ivec3(x, y, z - radius)).id == "minecraft:gold_block"
        and ED.getBlock(ivec3(x, y, z + radius)).id == "minecraft:gold_block"
    ):
        return  # return without building anything

    # lay the foundation
    GEO.placeCenteredCylinder(ED, ivec3(x, y, z), 1, radius, Block("emerald_block"))

    # build ground floor
    GEO.placeCenteredCylinder(ED, ivec3(x, y + 1, z), 3, radius, Block("lime_concrete"), tube=True)

    # extend height
    height = randint(5, 20)
    GEO.placeCenteredCylinder(ED, ivec3(x, y + 4, z), height, radius, Block("lime_concrete"), tube=True)
    height += 4

    # build roof
    GEO.placeCenteredCylinder(ED, ivec3(x, y + height, z), 1, radius, Block("emerald_block"))
    GEO.placeCenteredCylinder(ED, ivec3(x, y + height + 1, z), 1, radius - 1, Block("emerald_block"))
    GEO.placeCenteredCylinder(ED, ivec3(x, y + height + 2, z), 1, radius - 2, Block("emerald_block"))
    GEO.placeCuboid(ED, ivec3(x, y + height, z), ivec3(x, y + height + 2, z), Block("lime_stained_glass"))
    ED.placeBlock(ivec3(x, y + 1, z), Block("beacon"))

    # trim sides and add windows and doors
    # GEO.placeCuboid(ED, ivec3(x + radius, y + 1, z), ivec3( x + radius, y + height + 2, z), Block("air"))
    GEO.placeCuboid(ED, ivec3(x + radius - 1, y + 1, z), ivec3(x + radius - 1, y + height + 2, z), Block("lime_stained_glass"))
    # NOTE: When placing doors you need to place two blocks,
    #   the upper block defines the direction
    ED.placeBlock(ivec3(x + radius - 1, y + 1, z), Block("warped_door"))
    ED.placeBlock(ivec3(x + radius - 1, y + 2, z), Block("warped_door", {"facing": "west", "half": "upper"}))

    GEO.placeCuboid(ED, ivec3(x - radius, y + 1, z), ivec3( x - radius, y + height + 2, z), Block("air"))
    GEO.placeCuboid(ED, ivec3(x - radius + 1, y + 1, z), ivec3(x - radius + 1, y + height + 2, z), Block("lime_stained_glass"))
    ED.placeBlock(ivec3(x - radius + 1, y + 1, z), Block("warped_door"))
    ED.placeBlock(ivec3(x - radius + 1, y + 2, z), Block("warped_door", {"facing": "east", "half": "upper"}))

    GEO.placeCuboid(ED, ivec3(x, y + 1, z + radius), ivec3( x, y + height + 2, z + radius), Block("air"))
    GEO.placeCuboid(ED, ivec3(x, y + 1, z + radius - 1), ivec3(x, y + height + 2, z + radius - 1), Block("lime_stained_glass"))
    ED.placeBlock(ivec3(x, y + 1, z + radius - 1), Block("warped_door"))
    ED.placeBlock(ivec3(x, y + 2, z + radius - 1), Block("warped_door", {"facing": "south", "half": "upper"}))

    GEO.placeCuboid(ED, ivec3(x, y + 1, z - radius), ivec3( x, y + height + 2, z - radius), Block("air"))
    GEO.placeCuboid(ED, ivec3(x, y + 1, z - radius + 1), ivec3(x, y + height + 2, z - radius + 1), Block("lime_stained_glass"))
    ED.placeBlock(ivec3(x, y + 1, z - radius + 1), Block("warped_door"))
    ED.placeBlock(ivec3(x, y + 2, z - radius + 1), Block("warped_door", {"facing": "north", "half": "upper"}))


# === STRUCTURE #4
# The code in here will only run if we run the file directly (not imported)
# This prevents people from accidentally running your generator
if __name__ == '__main__':
    # NOTE: It is a good idea to keep this bit of the code as simple as
    #     possible so you can find mistakes more easily

    try:
        # height = WORLDSLICE.heightmaps["MOTION_BLOCKING"][(STARTX, STARTY)]
        height = WORLDSLICE.heightmaps["MOTION_BLOCKING"][(0, 0)]
        # INTF.runCommand(f"tp @a {STARTX} {height} {STARTZ}")
        # print(f"/tp @a {STARTX} {height} {STARTZ}")
        buildPerimeter()
        buildRoads()
        buildCity()

        print("Done!")
    except KeyboardInterrupt:   # useful for aborting a run-away program
        print("Pressed Ctrl-C to kill program.")
