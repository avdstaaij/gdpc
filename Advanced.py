#! /usr/bin/python3
"""### Generate a world of make-believe.

This file contains a comprehensive collection of functions designed
to introduce coders to the more involved aspects of the GDMC HTTP client.

The source code of this module contains examples for:

World Analysis:
- Global slices
- Biomes
- Obtrusiveness and optimal direction
- Versions
- Block categories

World manipulation:
- Interfaces
- Running commands
- Manipulating build area
- Placing blocks (advanced)
- Placing geometric shapes (advanced)
- Placing lecterns, signs, blocks with inventory

Utilities:
- 2D/3D loops
- Book writing

Optimisation:
- Keeping time
- Block caching
- Block buffering
- LRU Cache

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
__date__ = "27 February 2022"

from random import choice
from time import time

import numpy as np
from gdpc import geometry as geo
from gdpc import interface as intf
from gdpc import lookup, toolbox
from gdpc import worldLoader as wl
from gdpc.interface import globalinterface as gi

ALLOWED_TIME = 600  # permitted processing time in seconds (10 min)

# custom default build area with override
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = 0, 0, 0, 999, 255, 999
if intf.requestBuildArea() != [0, 0, 0, 127, 255, 127]:
    STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = intf.requestBuildArea()

WORLDSLICE = wl.WorldSlice(STARTX, STARTZ, ENDX, ENDZ)
XCHUNKSPAN, ZCHUNKSPAN = WORLDSLICE.chunkRect[2], WORLDSLICE.chunkRect[3]


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


burial_site(population):
    """Generate the burial site based on the population size"""

    small_tumulus(x, y, z, axis=None, items=[], open=False):
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
            # place ominous banner on top of chest
            # TODO: cover boat in cobble and earth, optionally make entrance

    large_tumulus():
        """Longboat inspired by https://www.youtube.com/watch?v=YY_z5cZ9DtM"""


docks():
    """"""

    place_boat():

    place_ship():
    """Inspired by https://www.youtube.com/watch?v=YY_z5cZ9DtM"""


if __name__ == '__main__':
    start = time()  # the time this code started in seconds

    # define regions
    # - landing site/docks (ocean, river bank, hills/mountains, forest)
    # - burial grounds (flat chunks, edge of village)
    # - village center
    # - forestry
    # - quarry/mine
    # - agriculture (soil, water or irrigation)
    # - special points (highest, lava)

    # start construction
    troglo_cave_coords = troglo_cave()

    center_coords = village_center()
    camp_coords = camp()
    mine_coords = mine()

    # generate more until 60 seconds remain
    while time() - start <= ALLOWED_TIME - 60:
        pass

    # cleanup and presentation

    troglo_grave_coords = burial_site(population)

    if docks_coords is None:
        landing_site()

    chronicle()
