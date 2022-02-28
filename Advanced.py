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
__date__ = "28 February 2022"

from copy import deepcopy
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

chunk_info_template = {'designations': [], 'primary_biome': None, 'biomes': []}
chunk_info = [[deepcopy(chunk_info_template) for _ in range(ZCHUNKSPAN)]
              for _ in range(XCHUNKSPAN)]

for x, z in toolbox.loop2d(XCHUNKSPAN, ZCHUNKSPAN):
    chunk_info[x][z]['primary_biome'] = WORLDSLICE.getPrimaryBiomeNear(
        STARTX + x * 16, 0, STARTZ + z * 16)
    chunk_info[x][z]['biomes'] = WORLDSLICE.getBiomesNear(STARTX + x * 16, 0,
                                                          STARTZ + z * 16)

    chunk_info[x][z]['designations'] = []

    # mark modifiers based on biomes (quicker than inspecting singular blocks)
    if 'snowy' in chunk_info[x][z]['primary_biome']:
        chunk_info[x][z]['designations'].append('snowy')

    if ('ocean' in chunk_info[x][z]['primary_biome']
        or 'river' in chunk_info[x][z]['primary_biome']
            or 'swamp' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('water')

    elif ('beach' in chunk_info[x][z]['primary_biome']
          or 'shore' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('water-adjacent')

    if ('forest' in chunk_info[x][z]['primary_biome']
        or 'taiga' in chunk_info[x][z]['primary_biome']
        or 'grove' in chunk_info[x][z]['primary_biome']
            or 'wooded' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('forest')

    if ('peaks' in chunk_info[x][z]['primary_biome']
        or 'hills' in chunk_info[x][z]['primary_biome']
        or 'mountains' in chunk_info[x][z]['primary_biome']
        or 'windswept' in chunk_info[x][z]['primary_biome']
            or 'eroded' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('harsh')

    if ('plains' in chunk_info[x][z]['primary_biome']
        or 'meadow' in chunk_info[x][z]['primary_biome']
        or 'fields' in chunk_info[x][z]['primary_biome']
        or 'sparse' in chunk_info[x][z]['primary_biome']
        or 'plateau' in chunk_info[x][z]['primary_biome']
            or 'desert' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('flat')


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


def burial_site(population):
    """Generate the burial site based on the population size."""
    # TODO: Place tumuli in burial grounds based on population
    pass


def docks():
    # TODO: Docks with ships out at sea
    pass


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

    conversion = {'snowy': 'snow_block',
                  'water': 'lapis_block', 'water-adjacent': 'lapis_ore',
                  'forest': 'oak_log', 'harsh': 'stone',
                  'flat': 'grass_block'}

    for x, z in toolbox.loop2d(len(chunk_info), len(chunk_info[0])):
        blocks = [conversion[d] for d in chunk_info[x][z]['designations']]
        if blocks == []:
            blocks = 'redstone_block'
        geo.placeVolume(STARTX + x * 16 + 7, 200, STARTZ + z * 16 + 7,
                        STARTX + x * 16 + 10, 200, STARTZ + z * 16 + 10,
                        blocks)

    # # start construction
    # troglo_cave_coords = troglo_cave()
    #
    # center_coords = village_center()
    # camp_coords = camp()
    # mine_coords = mine()

    # generate more until 60 seconds remain
    while time() - start <= ALLOWED_TIME - 60:
        break

    # cleanup and presentation

    population = 0
    troglo_grave_coords = burial_site(population)

    # if docks_coords is None:
    #     landing_site()
    #
    # chronicle()
