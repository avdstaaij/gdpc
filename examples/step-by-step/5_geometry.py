#!/usr/bin/env python3

"""
Use the geometry module to place geometrical regions of blocks.
"""

import sys

import numpy as np
from glm import ivec2, ivec3

from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import Y, addY, dropY, line3D, circle, fittingCylinder


# The minimum build area size in the XZ-plane for this example.
MIN_BUILD_AREA_SIZE = ivec2(35, 35)


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


# Get a world slice
print("Loading world slice...")
buildRect = buildArea.toRect()
worldSlice = editor.loadWorldSlice(buildRect)
print("World slice loaded!")


# Often, you will want to place large geometrical sections of blocks instead of placing them one
# by one. GDPC's geometry module contains all kinds of functions for this.
# These functions all take an Editor instance as their first argument.

# Place an outline around the build area
geometry.placeRectOutline(editor, buildRect, 100, Block("red_concrete"))

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
meanHeight = np.mean(heightmap)
groundCenter = addY(buildRect.center, meanHeight)

# Place a cuboid shape
geometry.placeCuboid(
    editor,
    groundCenter + ivec3(- 3, -10, - 3), # Corner 1
    groundCenter + ivec3(-10,  30, -10), # Corner 2
    Block("blue_concrete")
)

# Place a cylinder
geometry.placeFittingCylinder(
    editor,
    groundCenter + ivec3(- 3, -10,   3), # Corner 1
    groundCenter + ivec3(-10,  30,  10), # Corner 2
    Block("lime_concrete")
)

# Place a diagonal line
geometry.placeLine(
    editor,
    groundCenter + ivec3(  3, 20, - 3), # Endpoint 1
    groundCenter + ivec3( 10, 27, -10), # Endpoint 1
    Block("yellow_concrete"),
    width=1
)

# Place a cuboid that is striped along the X axis (axis 0)
geometry.placeStripedCuboid(
    editor,
    groundCenter + ivec3(  3, -10,   3), # Corner 1
    groundCenter + ivec3( 10,  30,  10), # Corner 2
    Block("purple_concrete"),
    Block("magenta_concrete"),
    axis=0
)


# For most of the geometry functions, it is also possible to get the points at which they place
# blocks directly. Various point-generating functions, not unlike loop2D and loop3D, can be found in
# the vector_tools module.

print("Line points:")
for point in line3D((0,0,0), (1,3,5)):
    print(tuple(point))

print("Circle points:")
for point in circle((0,0), 5):
    print(tuple(point))


# It is worth noting that Editor.placeBlock() can actually be called with sequence (technically
# speaking, an Iterable) of points instead of just one. This is slightly more efficient than
# calling Editor.placeBlock() in a loop, making it a good way to define your own geometry functions.
#
# Do note that the functions from the geometry module use a few more optimization tricks, so they
# should be preferred over this method where possible.

cylinder = fittingCylinder(
    groundCenter + ivec3(-17, 15, -17),
    groundCenter + ivec3( 17, 16,  17),
    tube=True
)

editor.placeBlock(cylinder, Block("orange_concrete"))
