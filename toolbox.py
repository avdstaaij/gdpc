#! /usr/bin/python3
"""### Provides various small functions for the average workflow."""

__all__ = []
__version__ = "v4.2_dev"


from random import choice

import lookup
from interfaceUtils import getBlock
from interfaceUtils import globalinterface as gi
from interfaceUtils import runCommand


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


def placeSign(x, y, z, facing=None, rotation=None,
              text1="", text2="", text3="", text4="",
              wood='oak', wall=False):
    """**Place a written sign in the world**.

    Facing is for wall placement, rotation for ground placement
    If there is no supporting wall the sign will revert to ground placement
    By default the sign will attempt to orient itself to be most legible

    Note: If you are experiencing performance issues provide your own facing
        and rotation values to reduce the required calculations
    """
    if wood not in lookup.WOODS:
        raise ValueError(f"{wood} is not a valid wood type!")

    if facing is not None and facing not in lookup.DIRECTIONS:
        print(f"{facing} is not a valid direction.\n"
              "Working with default behaviour.")
        facing = None
    try:
        if not (int(rotation) >= 0 and int(rotation) <= 15):
            raise TypeError
    except TypeError:
        if rotation is not None:
            print(f"{rotation} is not a valid rotation.\n"
                  "Working with default behaviour.")
        rotation = None

    if facing is None and rotation is None:
        facing = getOptimalDirection(x, y, z)

    if wall:
        wall = False
        for direction in facing:
            inversion = lookup.INVERTDIRECTION[direction]
            dx, dz = lookup.DIRECTIONTOVECTOR[inversion]
            if getBlock(x + dx, y, z + dz) in lookup.TRANSPARENT:
                break
            wall = True
            gi.placeBlock(
                x, y, z, f"{wood}_wall_sign[facing={choice(facing)}]")

    if not wall:
        if rotation is None:
            reference = {'north': 0, 'east': 4, 'south': 8, 'west': 12}
            if len(facing) == 1:
                rotation = reference[lookup.INVERTDIRECTION[facing[0]]]
            else:
                rotation = 0
                for direction in facing:
                    rotation += reference[lookup.INVERTDIRECTION[direction]]
                rotation //= 2

                print(f"{facing, rotation}")

                if rotation == 6 and 'north' not in facing:
                    rotation = 14
                if rotation % 4 != 2:
                    rotation = reference[facing[0]]
        gi.placeBlock(x, y, z, f"{wood}_sign[rotation={rotation}]")

    data = "{" + f'Text1:\'{{"text":"{text1}"}}\','
    data += f'Text2:\'{{"text":"{text2}"}}\','
    data += f'Text3:\'{{"text":"{text3}"}}\','
    data += f'Text4:\'{{"text":"{text4}"}}\'' + "}"
    runCommand(f"data merge block {x} {y} {z} {data}")


def getOptimalDirection(x, y, z):
    """**Return the least obstructed direction to have something facing**."""
    north = (identifyObtrusiveness(getBlock(x, y, z - 1)), 'north')
    east = (identifyObtrusiveness(getBlock(x + 1, y, z)), 'east')
    south = (identifyObtrusiveness(getBlock(x, y, z + 1)), 'south')
    west = (identifyObtrusiveness(getBlock(x - 1, y, z)), 'west')

    min_obstruction = min(north[0], east[0], south[0], west[0])
    max_obstruction = max(north[0], east[0], south[0], west[0])

    surrounding = [north, east, south, west]

    while surrounding[0][0] != max_obstruction:
        surrounding.append(surrounding.pop(0))

    directions = []
    while len(directions) == 0:
        if min_obstruction == max_obstruction:
            return lookup.DIRECTIONS

        print(f"{min_obstruction, max_obstruction, directions}")

        if surrounding[2][0] == min_obstruction:
            directions.append(surrounding[2][1])
        if (surrounding[1][0] == min_obstruction
                and surrounding[3][0] != min_obstruction):
            directions.append(surrounding[1][1])
        elif (surrounding[3][0] == min_obstruction
                and surrounding[1][0] != min_obstruction):
            directions.append(surrounding[3][1])
        elif len(directions) == 0:
            directions.append(surrounding[1][1])
            directions.append(surrounding[3][1])

        min_obstruction += 1

    return directions


def identifyObtrusiveness(blockStr):
    """**Return the percieved obtrusiveness of a given block**.

    Returns a numeric weight from 0 (invisible) to 4 (opaque)
    """
    if blockStr in lookup.INVISIBLE:
        return 0
    if blockStr in lookup.FILTERING:
        return 1
    if blockStr in lookup.UNOBTRUSIVE:
        return 2
    if blockStr in lookup.OBTRUSIVE:
        return 3
    return 4
