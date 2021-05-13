#! /usr/bin/python3
"""### Provides various small functions for the average workflow."""

__all__ = []
__version__ = "v4.2_dev"


import lookup
from interfaceUtils import getBlock


def loop2d(dx, dz):
    """**Return all coordinates in a region of size dx, dz**."""
    for x in range(dx):
        for z in range(dz):
            yield x, z


def loop3d(dx, dy, dz):
    """**Return all coordinates in a region of size dx, dy, dz**."""
    for x in range(dx):
        for y in range(dy):
            for z in range(dz):
                yield x, y, z


def placeSign(x, y, z, text1="", text2="", text3="", text4="", attach=False):
    """**Place a written sign in the world**."""
    getOptimalDirection(x, y, z)


def getOptimalDirection(x, y, z, diagonal=False):
    """**Return the least obstructed direction to have something facing**."""
    north = identifyObtrusiveness(getBlock(x, y, z - 1))
    east = identifyObtrusiveness(getBlock(x + 1, y, z))
    south = identifyObtrusiveness(getBlock(x, y, z + 1))
    west = identifyObtrusiveness(getBlock(x - 1, y, z))


def identifyObtrusiveness(blockStr):
    """**Return the percieved obtrusiveness of a given block**."""
    if blockStr in lookup.INVISIBLE:
        return 'invisible'
    if blockStr in lookup.UNOBTRUSIVE:
        return 'unobtrusive'
    if blockStr in lookup.FILTERING:
        return 'filtering'
    return 'opaque'
