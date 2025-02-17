#!/usr/bin/env python3

# ==============================================================================
#
# THE EXAMPLES ARE DEPRECATED!
#
# All in-repository examples are deprecated and will be removed in a future
# version of GDPC. They have been replaced by the new documentation website:
# https://gdpc.readthedocs.io/en/stable/.
#
# The examples are longer maintained and may be incompatible with the latest
# version of GDPC.
#
# ==============================================================================


"""
Get the specified build area and use it to place a block inside the bounds.
"""

import sys

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError


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


# The GDPC HTTP interface includes a so-called build area. This is a 3D box that can be set in-game
# which defines the bounds in which you should place blocks.
#
# The Generative Design in Minecraft Competition (GDMC) uses this build area to communicate to
# generator algorithms where they need to build. It can also be useful to you to control where your
# generator builds during development.
#
# In GDPC, the build area is merely a suggestion: its bounds are not enforced. It is up to you to
# request the build area and adhere to it. Future versions of the GDMC HTTP interface may however
# add enforcement.


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


# buildArea is a Box object, which is defined by an offset and a size.
print(f"Build area offset: {tuple(buildArea.offset)}")
print(f"Build area size:   {tuple(buildArea.size)}")

# The Box class has many convenience methods and properties. Here are a few.
print(f"Build area end:    {tuple(buildArea.end)}")
print(f"Build area last:   {tuple(buildArea.last)}") # Last is inclusive, end is exclusive.
print(f"Build area center: {tuple(buildArea.center)}")

# Place a block in the middle of the build area.
print(f"\nPlacing a block at {tuple(buildArea.center)}...")
editor.placeBlock(buildArea.center, Block("red_concrete"))
