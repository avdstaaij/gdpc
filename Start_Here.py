#! /usr/bin/python3
"""### Generate a simple example village.

This file contains a comprehensive collection of functions designed
to introduce new coders to the GDMC HTTP client in Python.

The source code of this module contains examples for:
* How to structure a file neatly (search 'STRUCTURE')
* Requesting the build area (search 'BUILDAREA')
* Introduction to world slices (search 'WORLDSLICE')
* Introduction to basic heightmaps (search 'HEIGHTMAP')

NOTE: We recommend creating your own files instead of modifying or adding code
    to these pre-existing files.
NOTE: If part of the program is running to fast for you to understand, insert
    >>> time.sleep(0.1)
    at the appropriate location for a delay of 1/10 of a second
INFO: Should you have any questions regarding this software, feel free to visit
    the #gdmc-http-discussion-help channel on the GDMC Discord Server
    (Invite link: https://discord.gg/zkdaEMBCmd)

This file is not meant to be imported.
"""

# === STRUCTURE #0
# These are technical values, you may ignore them or add them in your own files
__all__ = []
__author__ = "Blinkenlights"
__version__ = "v4.2_dev"
__date__ = "22 April 2021"

# === STRUCTURE #1
# These are the modules (libraries) we will use in this code
# We are giving these modules shorter, but distinct, names for convenience
import interfaceUtils as IU
import worldLoader as WL

# === STRUCTURE #2
# These variables are global and can be read from anywhere in the code
# I like to write them in capitals so I know they're global
# NOTE: if you want to change this value inside one of your functions,
#   you'll have to add a line of code. For an example search 'GLOBAL'
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = IU.requestBuildArea()  # BUILDAREA

# WORLDSLICE
# Using the start and end coordinates we are generating a world slice
# It contains all manner of information, including heightmaps and biomes
# For further information on what information it contains, see
#     https://minecraft.fandom.com/wiki/Chunk_format
#
# IMPORTANT: Keep in mind that a wold slice is a 'snapshot' of the world,
#   and any changes you make later on will not be reflected in the world slice
WORLDSLICE = WL.WorldSlice(STARTX, STARTZ, ENDX + 1,
                           ENDZ + 1)  # this takes a while


# === STRUCTURE #3
# Here we are defining all of our functions to keep our code organised
# They are:
# - buildPerimeter()
# - buildRoads()
# - placeCenterStones()

def buildPerimeter():
    """Build a wall along the build area border.

    In this function we're building a simple wall around the build area
    """
    # HEIGHTMAP
    # Heightmaps are an easy way to get the uppermost block at any coordinate
    # There are four types available in a world slice:
    # - 'WORLD_SURFACE': The top non-air blocks
    # - 'MOTION_BLOCKING': The top blocks with a hitbox or fluid
    # - 'MOTION_BLOCKING_NO_LEAVES': Like MOTION_BLOCKING but ignoring leaves
    # - 'OCEAN_FLOOR': The top solid blocks
    heights = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

    # building the east-west walls
    for x in range(STARTX, ENDX + 1):

        # the northern wall
        y = heights[(x, STARTZ)]
        IU.fill(x, y - 2, STARTZ, x, y, STARTZ, "granite")
        IU.fill(x, y + 1, STARTZ, x, y + 4, STARTZ, "granite_wall")

        # the southern wall
        y = heights[(x, ENDZ)]
        IU.fill(x, y - 2, ENDZ, x, y, ENDZ, "red_sandstone")
        IU.fill(x, y + 1, ENDZ, x, y + 4, ENDZ, "red_sandstone_wall")

    # building the north-south walls
    for z in range(STARTZ, ENDZ + 1):
        # the western wall
        y = heights[(STARTX, z)]
        IU.fill(STARTX, y - 2, z, STARTX, y, z, "sandstone")
        IU.fill(STARTX, y + 1, z, STARTX, y + 4, z, "sandstone_wall")
        # the eastern wall
        y = heights[(ENDX, z)]
        IU.fill(ENDX, y - 2, z, ENDX, y, z, "prismarine")
        IU.fill(ENDX, y + 1, z, ENDX, y + 4, z, "prismarine_wall")


def buildRoads():
    pass


def placeCenterStones():
    pass


# ===STRUCTURE #4
# The code in here will only run if we run the file directly (not imported)
# This prevents people from accidentally running your generator
if __name__ == '__main__':
    # NOTE: It is a good idea to keep this bit of the code as simple as
    #     possible so you can find mistakes more easily

    buildPerimeter()
    buildRoads()
    placeCenterStones()
