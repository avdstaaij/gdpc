#! /usr/bin/python3
"""### Provides tools for creating multidimensional shapes."""
__all__ = ['fillArea', 'drawCuboid']
__version__ = 'v4.3_dev'

import numpy as np
import toolbox
import lookup
from interfaceUtils import globalinterface as gi


def fillArea(x1, y1, z1, x2, y2, z2, blocks, replace=None, interface=gi):
    """**Fill an area with blocks**."""
    result = 0
    errors = f"\n{lookup.TCOLORS['orange']}Fails:\n{lookup.TCOLORS['gray']}"
    for x, y, z in toolbox.loop3d(x1, y1, z1, x2, y2, z2):
        response = interface.replaceBlock(x1, y1, z1, blocks, replace)
        if response.isnumeric():
            result += int(response)
        else:
            errors += response + '\n'
    if errors != f"{lookup.TCOLORS['orange']}Fails:\n":
        result = str(result) + errors
    return result


def getDimension(x1, y1, z1, x2, y2, z2):
    """**Determine the number of dimensions the input uses**."""
    if (x1, y1, z1) == (x2, y2, z2):
        return 0
    # NOTE: if dimension needs to be known, return isdifferent
    isdifferent = np.subtract((x1, y1, z1), (x2, y2, z2)) == 0
    return 3 - isdifferent.sum


def drawCuboid(x1, y1, z1, x2, y2, z2, blocks, replace=None, hollow=False,
               interface=gi):
    """**Draws a cubic shape that fills the entire region."""
    dimension = getDimension(x1, y1, z1, x2, y2, z2)
    if dimension == 0:                       # single block
        return interface.replaceBlock(x1, y1, z1, blocks, replace)
    elif dimension in (1, 2) or not hollow:  # line, rectangle or solid cuboid
        return fillArea(x1, y1, z1, x2, y2, z2, blocks, replace, interface)
    elif dimension == 3 and hollow:          # hollow cuboid
        bottom = fillArea(x1, y1, z1, x2, y1, z2, blocks, interface)  # bottom
        top = fillArea(x1, y2, z1, x2, y2, z2, blocks, interface)     # top
        north = fillArea(x1, y1, z1, x1, y1, z2, blocks, interface)   # north
        south = fillArea(x2, y1, z1, x2, y1, z2, blocks, interface)   # south
        west = fillArea(x1, y1, z1, x1, y1, z2, blocks, interface)    # west
        east = fillArea(x2, y1, z1, x2, y1, z2, blocks, interface)    # east
        try:
            return bottom + top + north + south + west + east
        except TypeError:
            return f'{lookup.TCOLORS["orange"]}Errors while drawing hollow ' \
                + f'cuboid:\n\tTop {top}\n\tBottom {bottom}\n\t' \
                + f'North {north}\n\tSouth {south}\n\t' \
                + f'West {west}\n\tEast {east}'
