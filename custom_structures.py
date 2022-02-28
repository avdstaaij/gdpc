#! /usr/bin/python3
"""### Generate a world of make-believe.

This file contains a comprehensive collection of functions designed
to introduce coders to the more involved aspects of the GDMC HTTP client.

This module contains examples for:
- Small and medium boats
- Burial mounds

If you haven't already, please take a look at Start_Here.py before continuing

NOTE: This file will be updated to reflect the latest features upon release
INFO: Should you have any questions regarding this software, feel free to visit
    the #ℹ-framework-support channel on the GDMC Discord Server
    (Invite link: https://discord.gg/V9MW65bD)

This file is not meant to be imported.
"""
__all__ = []
__author__ = "Blinkenlights"
__version__ = "v5.1_dev"
__date__ = "28 February 2022"

from random import choice

from gdmc import geometry as geo
from gdmc import interface as intf
from gdmc import lookup, toolbox


def place_small_boat(x, y, z, axis=None):
    if axis is None:
        axis = choice('x', 'z')

    if axis == 'x':
        geo.placeLine(x - 1, y - 1, z, x + 1, y - 1, z, 'dark_oak_planks')
        geo.placeLine(x - 1, y, z - 1, x + 1, y, z - 1,
                      'spruce_trapdoor'
                      '[facing=north, half=bottom, open=true]')
        geo.placeLine(x - 1, y, z + 1, x + 1, y, z + 1,
                      'spruce_trapdoor'
                      '[facing=south, half=bottom, open=true]')
        intf.placeBlock(x - 2, y, z,
                        'spruce_trapdoor'
                        '[facing=west, half=bottom, open=true]')
        intf.placeBlock(x + 2, y, z,
                        'spruce_trapdoor'
                        '[facing=east, half=bottom, open=true]')

        # pick a vector to place the entrance at
        entrance = lookup.AXIS2VECTOR('y') * choice([-1, 1])

    elif axis == 'y':
        geo.placeLine(x, y - 1, z - 1, x, y - 1, z + 1, 'dark_oak_planks')
        geo.placeLine(x - 1, y, z - 1, x - 1, y, z + 1,
                      'spruce_trapdoor'
                      '[facing=west, half=bottom, open=true]')
        geo.placeLine(x + 1, y, z - 1, x + 1, y, z + 1,
                      'spruce_trapdoor'
                      '[facing=east, half=bottom, open=true]')
        intf.placeBlock(x, y, z - 2,
                        'spruce_trapdoor'
                        '[facing=north, half=bottom, open=true]')
        intf.placeBlock(x, y, z + 2,
                        'spruce_trapdoor'
                        '[facing=south, half=bottom, open=true]')

        # pick a vector to place the entrance at
        entrance = lookup.AXIS2VECTOR['x'] * choice([-1, 1])

    else:
        print(f"{lookup.TCOLORS['red']}'{axis}' is not a valid axis!\n"
              "Small boat not placed")
        return None

    intf.placeBlock(x, y, z, 'dark_oak_fence')

    # TODO: place ominous banner on top

    return (x, y, z), entrance


def place_medium_boat(x, y, z, axis=None):
    """Longboat inspired by https://www.youtube.com/watch?v=YY_z5cZ9DtM."""
    # TODO:
    pass


def place_small_tumulus(x, y, z, axis=None, items=[], open=False):
    """Create a small ship burial mound."""
    floor = intf.getBlock(x, y, z)

    if axis is None:
        axis = choice('x', 'z')

    _, entrance = place_small_boat(x, y, z, axis)

    # Place chest containing remains
    casket = [
        (0, 0, 'emerald'), (0, 1, 'gold_ingot'), (0, 2, 'emerald'),
        (1, 1, 'skeleton_skull'),
        (2, 0, 'bone'), (2, 1, 'bone'), (2, 2, 'bone'),
        (3, 0, 'bone'), (3, 1, 'bone'), (3, 2, 'bone'),
        (4, 0, 'bone'), (4, 1, choice(items)), (4, 2, 'bone'),
        (5, 1, 'bone'),
        (6, 1, 'bone'),
        (7, 1, 'bone'),
        (8, 0, 'emerald'), (8, 1, 'gold_ingot'), (8, 2, 'emerald')
    ]
    toolbox.placeInventoryBlock(x, y, z, items=casket)

    # cover the cascet in cobblestone and some mossy cobblestone
    geo.placeJointedLine([(x - 3, y, z), (x, y, z - 3), (x + 3, y, z),
                          (x, y, z + 3), (x - 3, y, z),
                          (x - 2, y + 1, z), (x, y + 1, z - 2),
                          (x + 2, y + 1, z), (x, y + 1, z + 2),
                          (x - 2, y + 1, z),
                          (x - 1, y + 2, z), (x, y + 2, z - 1),
                          (x + 1, y + 2, z), (x, y + 2, z + 1),
                          (x - 1, y + 2, z),
                          ], 3 * ['cobblestone'] + ['mossy_cobblestone'])
    # cover the cobblestone with the ground if it is exposed to air
    geo.placeJointedLine([(x - 4, y, z), (x, y, z - 4), (x + 4, y, z),
                          (x, y, z + 4), (x - 4, y, z),
                          (x - 3, y + 1, z), (x, y + 1, z - 3),
                          (x + 3, y + 1, z), (x, y + 1, z + 3),
                          (x - 3, y + 1, z),
                          (x - 2, y + 2, z), (x, y + 2, z - 2),
                          (x + 2, y + 2, z), (x, y + 2, z + 2),
                          (x - 2, y + 2, z),
                          (x - 1, y + 3, z), (x, y + 3, z - 1),
                          (x + 1, y + 3, z), (x, y + 3, z + 1),
                          (x, y + 3, z),
                          ], floor, lookup.AIR)

    if open:
        dx, dy, dz = entrance
        facing = lookup.VECTOR2DIRECTION[entrance]
        geo.placeVolume(x + dx * 2, y, z + dz * 2,
                        x + dx * 3, y + 2, z + dz * 3, 'air')
        intf.placeBlock(x + dx * 3, y, z + dz * 3,
                        f'dark_oak_stairs[facing={facing}]')
        intf.placeBlock(x + dx * 2, y + 2, z + dz * 2,
                        f'wall_torch[facing={facing}]')


def place_large_tumulus():
    # TODO: captain's tumulus
    pass
