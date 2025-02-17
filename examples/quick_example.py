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


"""The quick example from the README"""


from gdpc import Editor, Block, geometry

editor = Editor(buffering=True)

# Get a block
block = editor.getBlock((0,48,0))

# Place a block
editor.placeBlock((0,80,0), Block("stone"))

# Build a cube
geometry.placeCuboid(editor, (0,80,2), (2,82,4), Block("oak_planks"))
