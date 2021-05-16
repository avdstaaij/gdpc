#! /usr/bin/python3
"""### Provides tools for creating multidimensional shapes."""
__all__ = []
__version__ = 'v4.3_dev'

import numpy as np
import toolbox
from interfaceUtils import globalinterface as gi


def fillArea(x1, y1, z1, x2, y2, z2, blocks, replace=None, interface=gi):
    """**Fill an area with blocks**."""
    for x, y, z in toolbox.loop3d(x1, y1, z1, x2, y2, z2):
        response = interface.replaceBlock(x1, y1, z1, blocks, replace)
        if response


def getDimension(x1, y1, z1, x2, y2, z2):
    """**Determine the number of dimensions the input uses**."""
    if (x1, y1, z1) == (x2, y2, z2):
        return 0
    # NOTE: if dimension needs to be known, return isdifferent
    isdifferent = np.subtract((x1, y1, z1), (x2, y2, z2)) == 0
    return 3 - isdifferent.sum


def drawCube(x1, y1, z1, x2, y2, z2, blocks, replace=None, hollow=False,
             interface=gi):
    """**Draws a cubic shape that fills the entire region."""
    dimension = getDimension(x1, y1, z1, x2, y2, z2)
    if dimension == 0:                       # single block
        return interface.replaceBlock(x1, y1, z1, blocks, replace)
    elif dimension in (1, 2) or not hollow:  # line, rectangle or solid cuboid
        return fillArea(x1, y1, z1, x2, y2, z2, blocks, replace)
    elif dimension == 3 and hollow:          # hollow cuboid
        fillArea(x1, y1, z1, x2, y1, z2, blocks)    # bottom
        fillArea(x1, y2, z1, x2, y2, z2, blocks)    # top
        fillArea(x1, y1, z1, x1, y1, z2, blocks)    # north
        fillArea(x2, y1, z1, x2, y1, z2, blocks)    # south
        fillArea(x1, y1, z1, x1, y1, z2, blocks)    # west
        fillArea(x2, y1, z1, x2, y1, z2, blocks)    # east
        return ()
