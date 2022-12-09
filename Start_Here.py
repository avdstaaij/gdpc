#! /usr/bin/python3
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

# === STRUCTURE #0
# These are technical values, you may ignore them or add them in your own files
__all__ = []
__author__ = "Blinkenlights"
__version__ = "v5.0"
__date__ = "17 February 2022"


# === STRUCTURE #1
# These are the modules (libraries) we will use in this code
# We are giving these modules shorter, but distinct, names for convenience
from random import randint

from gdpc import geometry as GEO
from gdpc import interface as INTF
from gdpc import toolbox as TB
from gdpc import worldLoader as WL

# === STRUCTURE #2
# These variables are global and can be read from anywhere in the code
# I like to write them in capitals so I know they're global
# NOTE: if you want to change this value inside one of your functions,
#   you'll have to add a line of code. For an example search 'GLOBAL'

# Here we read start and end coordinates of our build area
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = INTF.requestBuildArea()  # BUILDAREA

# WORLDSLICE
# Using the start and end coordinates we are generating a world slice
# It contains all manner of information, including heightmaps and biomes
# For further information on what information it contains, see
#     https://minecraft.fandom.com/wiki/Chunk_format
#
# IMPORTANT: Keep in mind that a wold slice is a 'snapshot' of the world,
#   and any changes you make later on will not be reflected in the world slice
WORLDSLICE = WL.WorldSlice(STARTX, STARTZ,
                           ENDX + 1, ENDZ + 1)  # this takes a while

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
        y = heights[(x, STARTZ)]
        GEO.placeCuboid(x, y - 2, STARTZ, x, y, STARTZ, "granite")
        GEO.placeCuboid(x, y + 1, STARTZ, x, y + 4, STARTZ, "granite_wall")
        # the southern wall
        y = heights[(x, ENDZ)]
        GEO.placeCuboid(x, y - 2, ENDZ, x, y, ENDZ, "red_sandstone")
        GEO.placeCuboid(x, y + 1, ENDZ, x, y + 4, ENDZ, "red_sandstone_wall")

    print("Building north-south walls...")
    # building the north-south walls
    for z in range(STARTZ, ENDZ + 1):
        # the western wall
        y = heights[(STARTX, z)]
        GEO.placeCuboid(STARTX, y - 2, z, STARTX, y, z, "sandstone")
        GEO.placeCuboid(STARTX, y + 1, z, STARTX, y + 4, z, "sandstone_wall")
        # the eastern wall
        y = heights[(ENDX, z)]
        GEO.placeCuboid(ENDX, y - 2, z, ENDX, y, z, "prismarine")
        GEO.placeCuboid(ENDX, y + 1, z, ENDX, y + 4, z, "prismarine_wall")


def buildRoads():
    """Build a road from north to south and east to west."""
    xaxis = STARTX + (ENDX - STARTX) // 2  # getting start + half the length
    zaxis = STARTZ + (ENDZ - STARTZ) // 2
    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    print("Calculating road height...")
    # caclulating the average height along where we want to build our road
    y = heights[(xaxis, zaxis)]
    for x in range(STARTX, ENDX + 1):
        newy = heights[(x, zaxis)]
        y = (y + newy) // 2
    for z in range(STARTZ, ENDZ + 1):
        newy = heights[(xaxis, z)]
        y = (y + newy) // 2

    # GLOBAL
    # By calling 'global ROADHEIGHT' we allow writing to ROADHEIGHT
    # If 'global' is not called, a new, local variable is created
    global ROADHEIGHT
    ROADHEIGHT = y

    print("Building east-west road...")
    # building the east-west road
    GEO.placeCuboid(xaxis - 2, y, STARTZ,
                    xaxis - 2, y, ENDZ, "end_stone_bricks")
    GEO.placeCuboid(xaxis - 1, y, STARTZ,
                    xaxis + 1, y, ENDZ, "gold_block")
    GEO.placeCuboid(xaxis + 2, y, STARTZ,
                    xaxis + 2, y, ENDZ, "end_stone_bricks")
    GEO.placeCuboid(xaxis - 1, y + 1, STARTZ,
                    xaxis + 1, y + 3, ENDZ, "air")

    print("Building north-south road...")
    # building the north-south road
    GEO.placeCuboid(STARTX, y, zaxis - 2,
                    ENDX, y, zaxis - 2, "end_stone_bricks")
    GEO.placeCuboid(STARTX, y, zaxis - 1,
                    ENDX, y, zaxis + 1, "gold_block")
    GEO.placeCuboid(STARTX, y, zaxis + 2,
                    ENDX, y, zaxis + 2, "end_stone_bricks")
    GEO.placeCuboid(STARTX, y + 1, zaxis - 1,
                    ENDX, y + 3, zaxis + 1, "air")


def buildCity():
    xaxis = STARTX + (ENDX - STARTX) // 2  # getting center
    zaxis = STARTZ + (ENDZ - STARTZ) // 2
    y = ROADHEIGHT

    print("Building city platform...")
    # Building a platform and clearing a dome for the city to sit in
    GEO.placeCenteredCylinder(xaxis, y, zaxis, 1, 21, "end_stone_bricks")
    GEO.placeCenteredCylinder(xaxis, y, zaxis, 1, 20, "gold_block")
    GEO.placeCenteredCylinder(xaxis, y + 1, zaxis, 3, 20, "air")
    GEO.placeCenteredCylinder(xaxis, y + 4, zaxis, 2, 19, "air")
    GEO.placeCenteredCylinder(xaxis, y + 6, zaxis, 1, 18, "air")
    GEO.placeCenteredCylinder(xaxis, y + 7, zaxis, 1, 17, "air")
    GEO.placeCenteredCylinder(xaxis, y + 8, zaxis, 1, 15, "air")
    GEO.placeCenteredCylinder(xaxis, y + 9, zaxis, 1, 12, "air")
    GEO.placeCenteredCylinder(xaxis, y + 10, zaxis, 1, 8, "air")
    GEO.placeCenteredCylinder(xaxis, y + 11, zaxis, 1, 3, "air")

    for i in range(50):
        buildTower(randint(xaxis - 20, xaxis + 20),
                   randint(zaxis - 20, zaxis + 20))

    # Place a book on a Lectern
    # See the wiki for book formatting codes
    INTF.placeBlock(xaxis, y, zaxis, "emerald_block")
    bookData = TB.writeBook("This book has a page!")
    TB.placeLectern(xaxis, y + 1, zaxis, bookData)


def buildTower(x, z):
    radius = 3
    y = ROADHEIGHT

    print(f"Building tower at {x}, {z}...")
    # if the blocks to the north, south, east and west aren't all gold
    if not (INTF.getBlock(x - radius, y, z) == "minecraft:gold_block"
            and INTF.getBlock(x + radius, y, z) == "minecraft:gold_block"
            and INTF.getBlock(x, y, z - radius) == "minecraft:gold_block"
            and INTF.getBlock(x, y, z + radius) == "minecraft:gold_block"):
        return  # return without building anything

    # lay the foundation
    GEO.placeCenteredCylinder(x, y, z, 1, radius, "emerald_block")

    # build ground floor
    GEO.placeCenteredCylinder(x, y + 1, z, 3, radius,
                              "lime_concrete", tube=True)

    # extend height
    height = randint(5, 20)
    GEO.placeCenteredCylinder(
        x, y + 4, z, height, radius, "lime_concrete", tube=True)
    height += 4

    # build roof
    GEO.placeCenteredCylinder(x, y + height, z, 1, radius, "emerald_block")
    GEO.placeCenteredCylinder(x, y + height + 1, z, 1,
                              radius - 1, "emerald_block")
    GEO.placeCenteredCylinder(x, y + height + 2, z, 1,
                              radius - 2, "emerald_block")
    GEO.placeCuboid(x, y + height, z, x, y + height
                    + 2, z, "lime_stained_glass")
    INTF.placeBlock(x, y + 1, z, "beacon")

    # trim sides and add windows and doors
    # GEO.placeCuboid(x + radius, y + 1, z, x + radius, y + height + 2, z, "air")
    GEO.placeCuboid(x + radius - 1, y + 1, z,
                    x + radius - 1, y + height + 2, z, "lime_stained_glass")
    # NOTE: When placing doors you need to place two blocks,
    #   the upper block defines the direction
    INTF.placeBlock(x + radius - 1, y + 1, z, "warped_door")
    INTF.placeBlock(x + radius - 1, y + 2, z,
                    "warped_door[facing=west, half=upper]")

    GEO.placeCuboid(x - radius, y + 1, z, x - radius, y + height + 2, z, "air")
    GEO.placeCuboid(x - radius + 1, y + 1, z,
                    x - radius + 1, y + height + 2, z, "lime_stained_glass")
    INTF.placeBlock(x - radius + 1, y + 1, z, "warped_door")
    INTF.placeBlock(x - radius + 1, y + 2, z,
                    "warped_door[facing=east, half=upper]")

    GEO.placeCuboid(x, y + 1, z + radius, x, y + height + 2, z + radius, "air")
    GEO.placeCuboid(x, y + 1, z + radius - 1,
                    x, y + height + 2, z + radius - 1, "lime_stained_glass")
    INTF.placeBlock(x, y + 1, z + radius - 1, "warped_door")
    INTF.placeBlock(x, y + 2, z + radius - 1,
                    "warped_door[facing=south, half=upper]")

    GEO.placeCuboid(x, y + 1, z - radius, x, y + height + 2, z - radius, "air")
    GEO.placeCuboid(x, y + 1, z - radius + 1,
                    x, y + height + 2, z - radius + 1, "lime_stained_glass")
    INTF.placeBlock(x, y + 1, z - radius + 1, "warped_door")
    INTF.placeBlock(x, y + 2, z - radius + 1,
                    "warped_door[facing=north, half=upper]")


# === STRUCTURE #4
# The code in here will only run if we run the file directly (not imported)
# This prevents people from accidentally running your generator
if __name__ == '__main__':
    # NOTE: It is a good idea to keep this bit of the code as simple as
    #     possible so you can find mistakes more easily

    try:
        height = WORLDSLICE.heightmaps["MOTION_BLOCKING"][(STARTX, STARTY)]
        INTF.runCommand(f"tp @a {STARTX} {height} {STARTZ}")
        print(f"/tp @a {STARTX} {height} {STARTZ}")
        buildPerimeter()
        buildRoads()
        buildCity()

        print("Done!")
    except KeyboardInterrupt:   # useful for aborting a run-away program
        print("Pressed Ctrl-C to kill program.")
