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
__date__ = "22 April 2021"

from random import choice, randint

import interfaceUtils as IU
import numpy as np
import worldLoader as WL

# custom default build area with override
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = 0, 0, 0, 255, 255, 255
if IU.requestBuildArea() != [0, 0, 0, 127, 255, 127]:
    STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = IU.requestBuildArea()

WORLDSLICE = WL.WorldSlice(STARTX, ENDX, STARTZ, ENDZ)
XCHUNKSPAN, ZCHUNKSPAN = WORLDSLICE.chunkRect[2], WORLDSLICE.chunkRect[3]

POLITICAL_REGIONS = np.array((XCHUNKSPAN, ZCHUNKSPAN))


def analyzeChunks():
    """Analyze chunks in the build area to determine geographic layout."""


if __name__ == '__main__':
    analyzeChunks()
