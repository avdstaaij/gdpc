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
Use the Editor class's various optional performance features.
"""

import sys
import time

from glm import ivec2, ivec3

from gdpc import __url__, Editor, Block, Box
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY, dropY


# The minimum build area size in the XZ-plane for this example.
MIN_BUILD_AREA_SIZE = ivec2(21, 21)


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


buildRect = buildArea.toRect()


# The Editor class has a bunch of features that significantly improve performance, but are disabled
# by default because they can have unexpected side effects.


# ==================================================================================================
# Buffering
# ==================================================================================================

# By far the most important performance feature is the "buffering mode". When buffering is enabled
# blocks no longer get placed immediately, but are instead collected in a buffer until the buffer
# limit is reached. They are then sent to the GDMC HTTP interface all at once, in a single request.
# Buffering can be enabled by setting Editor.buffering to True.


print("Placing 512 blocks without buffering...")

# Time the placement of 512 blocks.
t1 = time.time()
for point in Box(addY(buildRect.center) + ivec3(-10, 100, -10), (8,8,8)).inner:
    editor.placeBlock(point, Block("stone"))
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds.")


# Enable buffering.
editor.buffering = True


print("\nPlacing 512 blocks with buffering...")

# Time the placement of 512 blocks.
t1 = time.time()
for point in Box(addY(buildRect.center) + ivec3(-10, 100, 3), (8,8,8)).inner:
    editor.placeBlock(point, Block("stone"))
editor.flushBuffer() # Explicitly flush the buffer, rather than waiting for it to fill up.
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds.")


# The buffer limit can be accessed and modified through Editor.bufferLimit:
editor.bufferLimit = 1024


# Buffering is completely transparent except for the fact that blocks may not get placed instantly:

editor.placeBlock(addY(buildRect.center) + ivec3(0, 107, 0), Block("red_concrete"))
block = editor.getBlock(addY(buildRect.center) + ivec3(0, 107, 0))
print(block) # Prints "red_concrete" even though the block is still in the buffer.


# It is highly recommended to enable buffering in your programs. The only reason why it is not
# enabled by default is to avoid confusion when blocks are not immediately placed.
# This optimization is so important, that when you call Editor.placeBlock() with an Iterable of
# positions rather than a single one, it is automatically temporarily enabled. The same holds for
# the functions in the geometry module.
# If you disable buffering or if you program ends, the buffer is automatically flushed.

editor.buffering = False


# ==================================================================================================
# Caching
# ==================================================================================================

# Another performance feature is the "caching mode". While buffering is about block *placement*,
# caching is about block *retrieval*. When caching is enabled, the editor caches the last
# retrieved blocks (up to the cache limit) so no request to the GDMC HTTP interface is necessary.
# Caching can be enabled by setting Editor.caching to True.

# Enable caching.
editor.caching = True

print("\nGetting 512 blocks for the first time...")

t1 = time.time()
for point in Box(addY(buildRect.center) + ivec3(-10, 100, -10), (8,8,8)).inner:
    editor.getBlock(point)
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds.")

print("\nGetting the same 512 blocks for the second time...")

t1 = time.time()
for point in Box(addY(buildRect.center) + ivec3(-10, 100, -10), (8,8,8)).inner:
    editor.getBlock(point)
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds.")

# Disable caching.
editor.caching = False


# The cache limit can be accessed and modified through Editor.cacheLimit:
editor.cacheLimit = 8192


# Note that buffered blocks also act as a sort of cache (to guarantee transparancy). This cache
# supersedes the cache of the caching mode.

# Also note that, if the world is modified by something other than the caching Editor (for example,
# by a player on the server), the cache will *not* reflect those changes, and retrieved blocks may
# be incorrect!

# Although caching can greatly improve performance when blocks are retrieved multiple times, you
# still need to pay the cost for the first retrieval. When you need to read many blocks, it is
# recommended to use a WorldSlice instead. That does lead us to the next performance option...


# ==================================================================================================
# WorldSlice caching
# ==================================================================================================

# It is also possible to use a WorldSlice as a cache. The caching option acts as a "sparse cache",
# containing only a limited amount of blocks but having no restrictions on their spatial distance.
# A WorldSlice, on the other hand acts as a "dense cache": it contains *all* blocks within its
# bounds, but none outside of it.

# To use a WorldSlice as a cache, use Editor.loadWorldSlice() with cache=True.
# We cannot easily compare its speed, because a WorldSlice always loads entire chunks (which span
# the entire height of the world).

print("\nLoading world slice...")

t1 = time.time()
editor.loadWorldSlice(buildRect.centeredSubRect((8,8)), cache=True)
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds.")


print("\nGetting 512 blocks with a world slice cache...")

t1 = time.time()
for point in buildRect.centeredSubRect((8,8)).toBox(100, 8).inner:
    editor.getBlock(point)
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds (exluding WorldSlice loading time).")


# Of course, since the WorldSlice is a "snapshot", it may get outdated as you edit the world. The
# editor maintains a boolean "decay" array that indicates which blocks have been changed since the
# WorldSlice was cached, and it only uses the cached WorldSlice for unchanged blocks.
# Do note that - like with the regular caching mode - if the world is modified by something other
# than the caching Editor, this array will not be updated, and retrieved blocks may be incorrect.

# You can retrieve the decay array as follows:
decay = editor.worldSliceDecay
print(f"\nDecay array shape: {decay.shape}")


# If you reload the Editor's WorldSlice, the decay array resets. There is a convenience method to
# reload the WorldSlice for the same area as the cached one:

print("\nReloading world slice...")
editor.updateWorldSlice()
print("Done.")


# Accessing cached WorldSlice via Editor.getBlock() is very fast, but there is still a slight amount
# of overhead involved (to check if a point is inside the WorldSlice and if it's not decayed).
# For maximum performance, you should use a WorldSlice directly. The cached WorldSlice can easily be
# accessed:

worldSlice = editor.worldSlice


# ==================================================================================================
# Multithreaded buffer flushing
# ==================================================================================================

# The Editor class has one more performance feature, but this one is a bit more dangerous: it can
# use multiple threads to perform buffer flushing. The speed impact of this feature seems to differ
# widely between systems. On some machines, it has no effect at all, while on others, the effect can
# be significant.

# Using multithreaded buffer flushing with only one worker thread (the default amount) is
# relatively safe, but usually does not improve performance. To use multithreaded buffer flushing,
# buffering itself must also be enabled.

editor.buffering = True
editor.bufferLimit = 512
editor.multithreading = True

print("\nPlacing 2048 blocks with a buffer limit of 512 and one worker thread...")

t1 = time.time()
for point in Box(addY(buildRect.center) + ivec3(3, 76, -10), (8,32,8)).inner:
    editor.placeBlock(point, Block("stone"))
editor.flushBuffer()        # Explicitly flush the buffer.
editor.awaitBufferFlushes() # Explicitly await all pending buffer flushes.
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds ({(t2-t1)/4:.3f}s per 512 blocks).")


# It is also possible to use more than one worker thread. On some systems, this has been shown to
# improve performance significantly. However, it comes with a **MAJOR** caveat: it will make the
# Editor unable to guarantee that blocks will be placed in the same order they were issued. If
# buffering or caching is used, this can also cause the caches to become inconsistent with the
# world, even if only the multithreading Editor is modifying it. While the speedup can be nice
# during development, is is therefore **NOT RECOMMENDED** for production code.
# If you enable multithreaded buffer flushing with more than one worker thread, the Editor will log
# this warning as well.

# Set the amount of worker threads to 4 (causing a warning to be logged).
print("\n---")
editor.multithreadingWorkers = 4
print("---")

print("\nPlacing 2048 blocks with a buffer limit of 512 and four worker threads...")

t1 = time.time()
for point in Box(addY(buildRect.center) + ivec3(3, 76, 3), (8,32,8)).inner:
    editor.placeBlock(point, Block("stone"))
editor.flushBuffer()        # Explicitly flush the buffer.
editor.awaitBufferFlushes() # Explicitly await all pending buffer flushes.
t2 = time.time()

print(f"Done in {t2-t1:.3f} seconds ({(t2-t1)/4:.3f}s per 512 blocks).")


# ==================================================================================================
# Final notes
# ==================================================================================================

# As a final note, you can also construct an Editor instance with certain features enabled
# immediately:

editor = Editor(buffering=True, caching=True, cacheLimit=1024)
