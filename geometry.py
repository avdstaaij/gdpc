#! /usr/bin/python3
"""### Provides tools for creating multidimensional shapes."""
__all__ = ['placeLine', 'placeArea', 'placeCuboid', 'placefromList']
__version__ = 'v4.3_dev'

import lookup
import numpy as np
import toolbox
from interfaceUtils import globalinterface as gi


def placeLine(x1, y1, z1, x2, y2, z2, blocks, replace=None, interface=gi):
    """**Draw a line from point to point efficiently**."""
    dimension = getDimension(x1, y1, z1, x2, y2, z2)
    if dimension == 0:
        return interface.placeBlock(x1, y1, z1, blocks, replace)
    elif dimension == 1:
        return placeArea(x1, y1, z1, x2, y2, z2, blocks, replace, interface)
    elif dimension < 4:
        return placefromList(bresenhamLine(x1, y1, z1, x2, y2, z2),
                             blocks, replace, interface)


def placeArea(x1, y1, z1, x2, y2, z2, blocks, replace=None, interface=gi):
    """**Fill an area with blocks**."""
    return placefromList(toolbox.loop3d(x1, y1, z1, x2, y2, z2),
                         blocks, replace, interface)


def placeCuboid(x1, y1, z1, x2, y2, z2, blocks, replace=None,
                hollow=False, interface=gi):
    """**Draw a cubic shape that fills the entire region."""
    dimension = getDimension(x1, y1, z1, x2, y2, z2)

    if dimension == 0:                       # single block
        return interface.placeBlock(x1, y1, z1, blocks, replace)

    elif dimension in (1, 2) or not hollow:  # line, rectangle or solid cuboid
        return placeArea(x1, y1, z1, x2, y2, z2, blocks, replace, interface)

    elif dimension == 3 and hollow:                         # hollow cuboid
        bottom = placeArea(x1, y1, z1, x2, y1, z2, blocks,
                           replace, interface)              # bottom
        top = placeArea(x1, y2, z1, x2, y2, z2, blocks,
                        replace, interface)                 # top
        north = placeArea(x1, y1, z1, x1, y2, z2,
                          blocks, replace, interface)       # north
        south = placeArea(x2, y1, z1, x2, y2, z2,
                          blocks, replace, interface)       # south
        west = placeArea(x1, y1, z1, x1, y2, z2, blocks,
                         replace, interface)                # west
        east = placeArea(x2, y1, z1, x2, y2, z2, blocks,
                         replace, interface)                # east
        try:
            return bottom + top + north + south + west + east
        except TypeError:
            return f'{lookup.TCOLORS["orange"]}Errors while drawing hollow ' \
                + f'cuboid:\n\tTop {top}\n\tBottom {bottom}\n\t' \
                + f'North {north}\n\tSouth {south}\n\t' \
                + f'West {west}\n\tEast {east}'


def placefromList(list, blocks, replace=None, interface=gi):
    """**Replace all blocks at coordinates in list with blocks**."""
    result = 0
    ERRORMESSAGE = (f"\n{lookup.TCOLORS['orange']}"
                    "Fails:\n{lookup.TCOLORS['gray']}")
    errors = ERRORMESSAGE
    for x, y, z in list:
        response = interface.placeBlock(x, y, z, blocks, replace)
        if response.isnumeric():
            result += int(response)
        else:
            errors += response + '\n'
    if errors is not ERRORMESSAGE:
        result = str(result) + errors
    return result

# ========================================================= calculations


def getDimension(x1, y1, z1, x2, y2, z2):
    """**Determine the number of dimensions the input uses**."""
    if (x1, y1, z1) == (x2, y2, z2):
        return 0
    # NOTE: if dimension needs to be known, return isdifferent
    isdifferent = np.subtract((x1, y1, z1), (x2, y2, z2)) == 0
    return 3 - isdifferent.sum()


def bresenhamLine(x1, y1, z1, x2, y2, z2):
    """**Return coordinates for a line from point to point**.

    With 'inspiration' from
    https://www.geeksforgeeks.org/bresenhams-algorithm-for-3-d-line-drawing/
    """

    def if_greater_pos_else_neg(a, b):
        return 1 if a > b else -1

    def bresenham_line_next_point(x, y, z, xs, ys, zs, dx, dy, dz, p1, p2):
        x += xs
        if (p1 >= 0):
            y += ys
            p1 -= 2 * dx
        if (p2 >= 0):
            z += zs
            p2 -= 2 * dx
        p1 += 2 * dy
        p2 += 2 * dz
        return x, y, z, p1, p2

    points = []
    points.append((x1, y1, z1))
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dz = abs(z2 - z1)
    xs = if_greater_pos_else_neg(x2, x1)
    ys = if_greater_pos_else_neg(y2, y1)
    zs = if_greater_pos_else_neg(z2, z1)

    # Driving axis is X-axis"
    if (dx >= dy and dx >= dz):
        p1 = 2 * dy - dx
        p2 = 2 * dz - dx
        while (x1 != x2):
            x1, y1, z1, p1, p2 = bresenham_line_next_point(x1, y1, z1,
                                                           xs, ys, zs,
                                                           dx, dy, dz,
                                                           p1, p2)
            # x1 += xs
            # if (p1 >= 0):
            #     y1 += ys
            #     p1 -= 2 * dx
            # if (p2 >= 0):
            #     z1 += zs
            #     p2 -= 2 * dx
            # p1 += 2 * dy
            # p2 += 2 * dz
            points.append((x1, y1, z1))

    # Driving axis is Y-axis"
    elif (dy >= dx and dy >= dz):
        p1 = 2 * dx - dy
        p2 = 2 * dz - dy
        while (y1 != y2):
            y1, x1, z1, p1, p2 = bresenham_line_next_point(y1, x1, z1,
                                                           ys, xs, zs,
                                                           dy, dx, dz,
                                                           p1, p2)
            # y1 += ys
            # if (p1 >= 0):
            #     x1 += xs
            #     p1 -= 2 * dy
            # if (p2 >= 0):
            #     z1 += zs
            #     p2 -= 2 * dy
            # p1 += 2 * dx
            # p2 += 2 * dz
            points.append((x1, y1, z1))

    # Driving axis is Z-axis"
    else:
        p1 = 2 * dy - dz
        p2 = 2 * dx - dz
        while (z1 != z2):
            z1, x1, y1, p1, p2 = bresenham_line_next_point(z1, x1, y1,
                                                           zs, xs, ys,
                                                           dz, dx, dy,
                                                           p1, p2)
            # z1 += zs
            # if (p1 >= 0):
            #     y1 += ys
            #     p1 -= 2 * dz
            # if (p2 >= 0):
            #     x1 += xs
            #     p2 -= 2 * dz
            # p1 += 2 * dy
            # p2 += 2 * dx
            points.append((x1, y1, z1))

    return points
