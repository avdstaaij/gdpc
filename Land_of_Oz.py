#! /usr/bin/python3
"""### Generate a world of make-believe.

This file contains a comprehensive collection of functions designed
to introduce coders to the more involved aspects of the GDMC HTTP client.

The source code of this module contains examples for:
*
If you haven't already, please take a look at Start_Here.py before continuing

NOTE: This file will be updated to reflect the latest features upon release
INFO: Should you have any questions regarding this software, feel free to visit
    the #ℹ-framework-support channel on the GDMC Discord Server
    (Invite link: https://discord.gg/V9MW65bD)

This file is not meant to be imported.
"""
__all__ = []
__author__ = "Blinkenlights"
__version__ = "v4.3_dev"
__date__ = "09 February 2022"

import numpy as np
from gdpc import geometry as geo
from gdpc import interface as intf
from gdpc import lookup, toolbox
from gdpc import worldLoader as wl
from gdpc.interface import globalinterface as gi

# custom default build area with override
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = 0, 0, 0, 999, 255, 999
if intf.requestBuildArea() != [0, 0, 0, 127, 255, 127]:
    STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = intf.requestBuildArea()

WORLDSLICE = wl.WorldSlice(STARTX, STARTZ, ENDX, ENDZ)
XCHUNKSPAN, ZCHUNKSPAN = WORLDSLICE.chunkRect[2], WORLDSLICE.chunkRect[3]

POLITICAL_REGIONS = np.array((XCHUNKSPAN, ZCHUNKSPAN))

CITY_SIZE = 128


def analyzeChunks():
    """Analyze chunks in the build area to determine geographic layout."""
    # replace with getBiomesAt

    intf.setBuffering(True)
    intf.setBufferLimit(4096)

    geo.placeCuboid(STARTX, 254, STARTZ, ENDX, 255, ENDZ, "air")
    intf.sendBlocks()

    for x in range(WORLDSLICE.chunkRect[2]):
        for z in range(WORLDSLICE.chunkRect[3]):
            chunkID = x + z * WORLDSLICE.chunkRect[2]
            chunkData = WORLDSLICE.nbtfile['Chunks'][chunkID]['Level']
            biomes = chunkData['Biomes']
            biomes = list(set(biomes))
            biomes = str([lookup.BIOMES[i] for i in biomes])
            if ("ocean" in biomes or "river" in biomes):
                xstart = chunkData['xPos'].value * 16
                xend = xstart + 15
                zstart = chunkData['zPos'].value * 16
                zend = zstart + 15
                geo.placeCuboid(xstart, 200, zstart, xend,
                                200, zend, "snow_block")
                intf.sendBlocks()


def calculateTreelessHeightmap(worldSlice, interface=gi):
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    area = worldSlice.rect

    for x, z in toolbox.loop2d(area[2], area[3]):
        while True:
            y = heightmap[x, z]
            block = interface.getBlock(area[0] + x, y - 1, area[1] + z)
            if block[-4:] == '_log':
                heightmap[x, z] -= 1
            else:
                break

    return heightmap


def buildCity():
    """Build the Emerald City and set the spawn there."""


if __name__ == '__main__':
    analyzeChunks()
