#!/usr/bin/env python3

"""
NOTE: This file is an old example script. Although it is no longer
      comprehensive, and it does not use the most modern features or best
      practices of GDPC, it still contains a good amount of information while
      performing a practical task.

      New users are advised to look at the scripts in tutorials/ first, and
      then come back here for a slightly outdated, but practical application.

---

Generate an emerald city.

This file contains a collection of functions designed
to introduce new coders to the GDMC HTTP client in Python.

The source code of this module contains examples for:
- How to structure a file neatly (search 'STRUCTURE')
- Requesting the build area (search 'BUILDAREA')
- Introduction to world slices (search 'WORLDSLICE')
- Introduction to basic heightmaps (search 'HEIGHTMAP')
- Introduction to basic geometric shapes (search 'geo')

NOTE: We recommend creating your own files instead of modifying or adding code
      to these pre-existing files.

NOTE: If part of the program is running to fast for you to understand, insert
      >>> from time import sleep
      and
      >>> sleep(0.1)
      at the appropriate locations for a delay of 1/10 of a second
      Alternatively, inserting
      >>> input("Waiting for user to press [Enter]")
      will pause the program at that point.

NOTE: This file will only be updated in the case of breaking changes
      and will not showcase new features!

NOTE: Should you have any questions regarding this software, feel free to visit
      the #ℹ-framework-support channel on the GDMC Discord Server
      (Invite link: https://discord.gg/ueaxuXj)

This file is not meant to be imported.
"""


# === STRUCTURE #1
# These are the modules (libraries) we will use in this code
# We are giving these modules shorter, but distinct, names for convenience

import logging
from random import randint

from termcolor import colored

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et


# Here, we set up Python's logging system.
# GDPC sometimes logs some errors that it cannot otherwise handle.
logging.basicConfig(format=colored("%(name)s - %(levelname)s - %(message)s", color="yellow"))


# === STRUCTURE #2
# These variables are global and can be read from anywhere in the code.
# NOTE: If you want to change a global value inside one of your functions,
#       you'll have to add a line of code. For an example, search 'GLOBAL'.

# Here we construct an Editor object
ED = Editor(buffering=True)

# Here we read start and end coordinates of our build area
BUILD_AREA = ED.getBuildArea()  # BUILDAREA
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

# WORLDSLICE
# Using the start and end coordinates we are generating a world slice
# It contains all manner of information, including heightmaps and biomes
# For further information on what information it contains, see
# https://minecraft.wiki/Chunk_format
#
# IMPORTANT: Keep in mind that a wold slice is a 'snapshot' of the world,
# and any changes you make later on will not be reflected in the world slice
WORLDSLICE = ED.loadWorldSlice(BUILD_AREA.toRect(), cache=True)  # this takes a while

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

    for x in range(STARTX, LASTX + 1):
        # The northern wall
        y = heights[(x - STARTX, 0)]
        geo.placeCuboid(ED, (x, y - 2, STARTZ), (x, y, STARTZ), Block("granite"))
        geo.placeCuboid(ED, (x, y + 1, STARTZ), (x, y + 4, STARTZ), Block("granite_wall"))
        # The southern wall
        y = heights[(x - STARTX, LASTZ - STARTZ)]
        geo.placeCuboid(ED, (x, y - 2, LASTZ), (x, y, LASTZ), Block("red_sandstone"))
        geo.placeCuboid(ED, (x, y + 1, LASTZ), (x, y + 4, LASTZ), Block("red_sandstone_wall"))

    print("Building north-south walls...")

    for z in range(STARTZ, LASTZ + 1):
        # The western wall
        y = heights[(0, z - STARTZ)]
        geo.placeCuboid(ED, (STARTX, y - 2, z), (STARTX, y, z), Block("sandstone"))
        geo.placeCuboid(ED, (STARTX, y + 1, z), (STARTX, y + 4, z), Block("sandstone_wall"))
        # The eastern wall
        y = heights[(LASTX - STARTX, z - STARTZ)]
        geo.placeCuboid(ED, (LASTX, y - 2, z), (LASTX, y, z), Block("prismarine"))
        geo.placeCuboid(ED, (LASTX, y + 1, z), (LASTX, y + 4, z), Block("prismarine_wall"))


def buildRoads():
    """Build a road from north to south and east to west."""
    xaxis = STARTX + (LASTX - STARTX) // 2  # Getting start + half the length
    zaxis = STARTZ + (LASTZ - STARTZ) // 2
    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    print("Calculating road height...")
    # Caclulating the average height along where we want to build our road
    y = heights[(xaxis - STARTX, zaxis - STARTZ)]
    for x in range(STARTX, LASTX + 1):
        newy = heights[(x - STARTX, zaxis - STARTZ)]
        y = (y + newy) // 2
    for z in range(STARTZ, LASTZ + 1):
        newy = heights[(xaxis - STARTX, z - STARTZ)]
        y = (y + newy) // 2

    # GLOBAL
    # By calling 'global ROADHEIGHT' we allow writing to ROADHEIGHT.
    # If 'global' is not called, a new, local variable is created.
    global ROADHEIGHT
    ROADHEIGHT = y

    print("Building east-west road...")

    geo.placeCuboid(ED, (xaxis - 2, y, STARTZ), (xaxis - 2, y, LASTZ), Block("end_stone_bricks"))
    geo.placeCuboid(ED, (xaxis - 1, y, STARTZ), (xaxis + 1, y, LASTZ), Block("gold_block"))
    geo.placeCuboid(ED, (xaxis + 2, y, STARTZ), (xaxis + 2, y, LASTZ), Block("end_stone_bricks"))
    geo.placeCuboid(ED, (xaxis - 1, y + 1, STARTZ), (xaxis + 1, y + 3, LASTZ), Block("air"))

    print("Building north-south road...")

    geo.placeCuboid(ED, (STARTX, y, zaxis - 2), (LASTX, y, zaxis - 2), Block("end_stone_bricks"))
    geo.placeCuboid(ED, (STARTX, y, zaxis - 1), (LASTX, y, zaxis + 1), Block("gold_block"))
    geo.placeCuboid(ED, (STARTX, y, zaxis + 2), (LASTX, y, zaxis + 2), Block("end_stone_bricks"))
    geo.placeCuboid(ED, (STARTX, y + 1, zaxis - 1), (LASTX, y + 3, zaxis + 1), Block("air"))


def buildCity():
    xaxis = STARTX + (LASTX - STARTX) // 2  # Getting center
    zaxis = STARTZ + (LASTZ - STARTZ) // 2
    y = ROADHEIGHT

    print("Building city platform...")
    # Building a platform and clearing a dome for the city to sit in
    geo.placeCylinder(ED, (xaxis, y,      zaxis), 39, 1, Block("end_stone_bricks"))
    geo.placeCylinder(ED, (xaxis, y,      zaxis), 37, 1, Block("gold_block"))
    geo.placeCylinder(ED, (xaxis, y +  1, zaxis), 37, 3, Block("air"))
    geo.placeCylinder(ED, (xaxis, y +  4, zaxis), 35, 2, Block("air"))
    geo.placeCylinder(ED, (xaxis, y +  6, zaxis), 33, 1, Block("air"))
    geo.placeCylinder(ED, (xaxis, y +  7, zaxis), 32, 1, Block("air"))
    geo.placeCylinder(ED, (xaxis, y +  8, zaxis), 27, 1, Block("air"))
    geo.placeCylinder(ED, (xaxis, y +  9, zaxis), 21, 1, Block("air"))
    geo.placeCylinder(ED, (xaxis, y + 10, zaxis), 13, 1, Block("air"))
    geo.placeCylinder(ED, (xaxis, y + 11, zaxis),  3, 1, Block("air"))

    for _ in range(50):
        buildTower(randint(xaxis - 20, xaxis + 20),
                   randint(zaxis - 20, zaxis + 20))

    # Place a book on a Lectern.
    # See the wiki for book formatting codes.
    ED.placeBlock((xaxis, y, zaxis), Block("emerald_block"))
    bookData = mt.bookData("This book has a page!")
    et.placeLectern(ED, (xaxis, y + 1, zaxis), bookData=bookData)


def buildTower(x, z):
    radius = 3
    diameter = 2*radius + 1
    y = ROADHEIGHT

    print(f"Building tower at {x}, {z}...")
    # If the blocks to the north, south, east and west aren't all gold
    if not (
            ED.getBlock((x - radius, y, z)).id == "minecraft:gold_block"
        and ED.getBlock((x + radius, y, z)).id == "minecraft:gold_block"
        and ED.getBlock((x, y, z - radius)).id == "minecraft:gold_block"
        and ED.getBlock((x, y, z + radius)).id == "minecraft:gold_block"
    ):
        return  # Return without building anything

    # Lay the foundation
    geo.placeCylinder(ED, (x, y, z), diameter, 1, Block("emerald_block"))

    # Build ground floor
    geo.placeCylinder(ED, (x, y + 1, z), diameter, 3, Block("lime_concrete"), tube=True)

    # Extend height
    height = randint(5, 20)
    geo.placeCylinder(ED, (x, y + 4, z), diameter, height, Block("lime_concrete"), tube=True)
    height += 4

    # Build roof
    geo.placeCylinder(ED, (x, y + height, z), diameter, 1, Block("emerald_block"))
    geo.placeCylinder(ED, (x, y + height + 1, z), diameter-2, 2, Block("emerald_block"))
    geo.placeCuboid(ED, (x, y + height, z), (x, y + height + 2, z), Block("lime_stained_glass"))
    ED.placeBlock((x, y + 1, z), Block("beacon"))

    # Trim sides and add windows and doors
    # NOTE: When placing doors, you only need to place the bottom block.
    geo.placeCuboid(ED, (x + radius, y + 1, z), (x + radius, y + height + 2, z), Block("air"))
    geo.placeCuboid(ED, (x + radius - 1, y + 1, z), (x + radius - 1, y + height + 2, z), Block("lime_stained_glass"))
    ED.placeBlock((x + radius - 1, y + 1, z), Block("warped_door", {"facing": "west"}))

    geo.placeCuboid(ED, (x - radius, y + 1, z), (x - radius, y + height + 2, z), Block("air"))
    geo.placeCuboid(ED, (x - radius + 1, y + 1, z), (x - radius + 1, y + height + 2, z), Block("lime_stained_glass"))
    ED.placeBlock((x - radius + 1, y + 1, z), Block("warped_door", {"facing": "east"}))

    geo.placeCuboid(ED, (x, y + 1, z + radius), (x, y + height + 2, z + radius), Block("air"))
    geo.placeCuboid(ED, (x, y + 1, z + radius - 1), (x, y + height + 2, z + radius - 1), Block("lime_stained_glass"))
    ED.placeBlock((x, y + 1, z + radius - 1), Block("warped_door", {"facing": "north"}))

    geo.placeCuboid(ED, (x, y + 1, z - radius), (x, y + height + 2, z - radius), Block("air"))
    geo.placeCuboid(ED, (x, y + 1, z - radius + 1), (x, y + height + 2, z - radius + 1), Block("lime_stained_glass"))
    ED.placeBlock((x, y + 1, z - radius + 1), Block("warped_door", {"facing": "south"}))


def main():
    try:
        buildPerimeter()
        buildRoads()
        buildCity()

        print("Done!")

    except KeyboardInterrupt: # useful for aborting a run-away program
        print("Pressed Ctrl-C to kill program.")


# === STRUCTURE #4
# The code in here will only run if we run the file directly (not imported).
# This prevents people from accidentally running your generator.
# It is recommended to directly call a function here, because any variables
# you declare outside a function will be global.
if __name__ == '__main__':
    main()
