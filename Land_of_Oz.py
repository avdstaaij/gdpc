#! /usr/bin/python3
"""### Generate a world of make-believe.

This file contains a comprehensive collection of functions designed
to introduce coders to the more involved aspects of the GDMC HTTP client.

The source code of this module contains examples for:
*
If you haven't already, please take a look at Start_Here.py before continuing

NOTE: This file will be updated to reflect the latest features upon release
INFO: Should you have any questions regarding this software, feel free to visit
    the #gdmc-http-discussion-help channel on the GDMC Discord Server
    (Invite link: https://discord.gg/zkdaEMBCmd)

This file is not meant to be imported.
"""
__all__ = []
__author__ = "Blinkenlights"
__version__ = "v4.2_dev"
__date__ = "23 April 2021"

from random import choice, randint

import interfaceUtils as IU
import numpy as np
import worldLoader as WL

# custom default build area with override
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = 0, 0, 0, 999, 255, 999
if IU.requestBuildArea() != [0, 0, 0, 127, 255, 127]:
    STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = IU.requestBuildArea()

WORLDSLICE = WL.WorldSlice(STARTX, STARTZ, ENDX, ENDZ)
XCHUNKSPAN, ZCHUNKSPAN = WORLDSLICE.chunkRect[2], WORLDSLICE.chunkRect[3]

POLITICAL_REGIONS = np.array((XCHUNKSPAN, ZCHUNKSPAN))

CITY_SIZE = 128


def analyzeChunks():
    """Analyze chunks in the build area to determine geographic layout."""
    # replace with getBiomesAt

    IU.setBuffering(True)
    IU.setBufferLimit(4096)

    IU.fill(STARTX, 255, STARTZ, ENDX, 255, ENDZ, "air")
    IU.sendBlocks()

    for x in range(WORLDSLICE.chunkRect[2]):
        for z in range(WORLDSLICE.chunkRect[3]):
            chunkID = x + z * WORLDSLICE.chunkRect[2]
            biomes = WORLDSLICE.nbtfile['Chunks'][chunkID]['Level']['Biomes']
            biomes = list(set(biomes))
            print(biomes)
            if (0 in biomes or 7 in biomes or 24 in biomes or 44 in biomes
                    or 45 in biomes or 46 in biomes or 47 in biomes
                    or 48 in biomes or 49 in biomes or 50 in biomes):
                xstart = WORLDSLICE.nbtfile['Chunks'][chunkID]['Level']['xPos'].value * 16
                xend = xstart + 15
                zstart = WORLDSLICE.nbtfile['Chunks'][chunkID]['Level']['zPos'].value * 16
                zend = zstart + 15
                print(f"filling {xstart, zstart, xend, zend}")
                IU.fill(xstart, 255, zstart, xend,
                        255, zend, "snow_block")
                IU.sendBlocks()
                print("filling done.")


def buildCity():
    """Build the Emerald City and set the spawn there."""


if __name__ == '__main__':
    analyzeChunks()
