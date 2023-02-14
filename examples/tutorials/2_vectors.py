#!/usr/bin/env python3

"""
Use vector math and some of GDPC's various vector utilities.
"""

import sys

import numpy as np
from glm import ivec2, ivec3

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError
from gdpc.vector_tools import X, Y, Z, XZ, addY, dropY, loop2D, loop3D, perpendicular, toAxisVector


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


# GDPC's API is based on *vectors*: points in 2D or 3D space.
# In the placeBlock() call below, (0,80,0) is such a vector. It describes the position
# (x = 0, y = 80, z = 0).

editor.placeBlock((0,80,0), Block("red_concrete"))


# GDPC accepts any object that "behaves" like a vector as arguments to its functions. That means
# that the following calls all work:

editor.placeBlock((0,80,1),           Block("blue_concrete"))
editor.placeBlock([0,80,2],           Block("green_concrete"))
editor.placeBlock(np.array([0,80,3]), Block("yellow_concrete"))


# However, when a GDPC function returns a vector, it always returns a vector from the pyGLM
# package. These vectors allow you to use vector math operators, which can often simplify code.
# They also have handy .x, .y and .z attributes.

vecA = ivec3(0,15,0)
vecB = ivec3(0,50,4)
vecC = vecA * 2 + vecB

print(f"vecC: {tuple(vecC)}") # We convert to a tuple before printing for easier reading.
print(f"vecC.x: {vecC.x}, .y: {vecC.y}, .z: {vecC.z}")

editor.placeBlock(vecC, Block("purple_concrete"))


# If you prefer to work with separate x, y and z numbers, you can always "unpack" these vectors:

x, y, z = vecC
print(f"x: {x}, y: {y}, z: {z}")


# The pyGLM package provides all kinds of vector math functions. See https://pypi.org/project/PyGLM/
# for more details.
# GDPC provides a bunch of additional vector-related tools in the `vector_tools` module.
# Here are a few:

# addY() turns a 2D vector into a 3D one by adding a Y component.
vecD = ivec2(1,3)
vecE = addY(vecD, 2)
print(f"vecE: {tuple(vecE)}")

# dropY() does the reverse.
vecF = dropY(vecE)
print(f"vecF: {tuple(vecF)}")

# perpendicular() returns a vector that is perpendicular to the given one.
vecG = perpendicular((1,0))
print(f"vecG: {tuple(vecG)}")

# toAxisVector() returns the axis-aligned vector that is closest to the given one.
vecH = toAxisVector((11,2))
print(f"vecH: {tuple(vecH)}")

# loop2D() loops over a 2D area defined by two corners.
# You could use to to place a platform of blocks:
print("Placing platform...")
for vec in loop2D((1,0), (4,3)):
    print(tuple(vec))
    editor.placeBlock(addY(vec, 80), Block("orange_concrete"))

# loop3D() does the same, but in 3D:
print("Placing box...")
for vec in loop3D((1,80,3), (4,82,5)):
    print(tuple(vec))
    editor.placeBlock(vec, Block("light_blue_concrete"))


# GDPC also provides some convenient vector constants:

vecG = 2*X + 3*Y + 4*Z
print(f"vecG: {tuple(vecG)}")

vecH = vecG - 2*XZ
print(f"vecH: {tuple(vecH)}")


# Some final notes:
#
# Minecraft uses a right-handed coordinate system. This means that, when you face towards positive
# Z, positive X will be towards the *left*. If you think of Z as "forward" and X as "sideways",
# this may cause buildings to seem flipped, so keep this in mind.
#
# Most of GDPC's functions work with integer vectors. If you pass vector-like types of floating
# point numbers, they will be converted to integers. The requirements for vector-like parameters are
# documented using type hints. For example, a function that requires a vector-like of three integers
# will have the type hint `Vec3iLike`.
