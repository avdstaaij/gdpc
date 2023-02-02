#!/usr/bin/env python3

"""
Get the specified build area and use it to place a block.
"""

import sys
from gdpc import Editor, Block, exceptions, __url__


# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()


# Check if the editor can connect to the GDMC HTTP interface.
try:
    editor.checkConnection()
except exceptions.InterfaceConnectionError:
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
except exceptions.BuildAreaNotSetError:
    print(
        "Error: failed to get the build area!\n"
        "Make sure to set the build area with the /setbuildarea command in-game.\n"
        "For example: /setbuildarea ~0 0 ~0 ~128 200 ~128"
    )
    sys.exit(1)


# buildArea is a Box object, which is defined by an offset and a size.
print(f"Build area offset: {buildArea.offset}")
print(f"Build area size:   {buildArea.size}")

# The Box class has many convenience methods and properties. Here are a few.
print(f"Build area end:    {buildArea.end}")
print(f"Build area last:   {buildArea.last}")
print(f"Build area center: {buildArea.center}")

# Place a block in the middle of the build area.
print(f"\nPlacing a block at {buildArea.center}...")
editor.placeBlock(buildArea.center, Block("red_concrete"))
