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
__date__ = "01 March 2022"

from copy import deepcopy
from time import time

from gdpc import geometry as geo
from gdpc import interface as intf
from gdpc import lookup, toolbox
from gdpc.interface import globalinterface as gi

ALLOWED_TIME = 600  # permitted processing time in seconds (10 min)

# custom default build area with override
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = 0, 0, 0, 999, 255, 999
if intf.requestBuildArea() != [0, 0, 0, 127, 255, 127]:
    STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = intf.requestBuildArea()

GLOBALSLICE = intf.makeGlobalSlice()
XCHUNKSPAN, ZCHUNKSPAN = GLOBALSLICE.chunkRect[2], GLOBALSLICE.chunkRect[3]

chunk_info_template = {'designations': [], 'primary_biome': None, 'biomes': []}
chunk_info = [[deepcopy(chunk_info_template)
               for _ in range(ZCHUNKSPAN)]
              for _ in range(XCHUNKSPAN)]

# blocks to avoid (key is 3D coords)
# value may anything (e.g. reason for avoidance), since only the key is checked
to_avoid = {}

for x, z in toolbox.loop2d(XCHUNKSPAN, ZCHUNKSPAN):
    chunk_info[x][z]['primary_biome'] = GLOBALSLICE.getPrimaryBiomeNear(
        STARTX + x * 16, 0, STARTZ + z * 16)
    chunk_info[x][z]['biomes'] = GLOBALSLICE.getBiomesNear(STARTX + x * 16, 0,
                                                           STARTZ + z * 16)

    chunk_info[x][z]['designations'] = []

    # mark modifiers based on biomes (quicker than inspecting singular blocks)
    if 'snowy' in chunk_info[x][z]['primary_biome']:
        chunk_info[x][z]['designations'].append('snowy')

    if ('forest' in chunk_info[x][z]['primary_biome']
        or 'taiga' in chunk_info[x][z]['primary_biome']
        or 'grove' in chunk_info[x][z]['primary_biome']
            or 'wooded' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('forest')

    if ('ocean' in chunk_info[x][z]['primary_biome']
            or 'swamp' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('water')

    elif ('beach' in chunk_info[x][z]['primary_biome']
          or 'river' in chunk_info[x][z]['primary_biome']
          or 'shore' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('water-adjacent')

    if ('peaks' in chunk_info[x][z]['primary_biome']
        or 'hills' in chunk_info[x][z]['primary_biome']
        or 'mountains' in chunk_info[x][z]['primary_biome']
        or 'windswept' in chunk_info[x][z]['primary_biome']
            or 'eroded' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('harsh')

    elif ('plains' in chunk_info[x][z]['primary_biome']
          or 'meadow' in chunk_info[x][z]['primary_biome']
          or 'fields' in chunk_info[x][z]['primary_biome']
          or 'sparse' in chunk_info[x][z]['primary_biome']
          or 'plateau' in chunk_info[x][z]['primary_biome']
            or 'desert' in chunk_info[x][z]['primary_biome']):
        chunk_info[x][z]['designations'].append('flat')


def calculateTreelessHeightmap(worldSlice=GLOBALSLICE, interface=gi):
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    area = worldSlice.rect

    for x, z in toolbox.loop2d(area[2], area[3]):
        while True:
            y = heightmap[x, z]
            block = interface.getBlock(area[0] + x, y, area[1] + z)
            if (block[-4:] == '_log' or block[-7:] == '_leaves'
                    or block in lookup.AIR):
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

    def debug_chunk_info():
        conversion = {'snowy': 'snow_block', 'forest': 'oak_log',
                      'water': 'lapis_block', 'water-adjacent': 'lapis_ore',
                      'harsh': 'stone', 'flat': 'grass_block',
                      'structure': 'gold_block'}

        for x, z in toolbox.loop2d(len(chunk_info), len(chunk_info[0])):
            blocks = [conversion[d] for d in chunk_info[x][z]['designations']]
            if blocks == []:
                blocks = 'redstone_block'
            geo.placeVolume(STARTX + x * 16 + 7, 250, STARTZ + z * 16 + 7,
                            STARTX + x * 16 + 10, 250, STARTZ + z * 16 + 10,
                            blocks)

        input('Enter to clear')
        geo.placeVolume(STARTX, 250, STARTZ, ENDX - 1, 250, ENDZ - 1, 'air')

    # define regions
    # - landing site/docks (ocean, river bank, hills/mountains, forest)
    # - burial grounds (flat chunks, edge of village)
    # - village center
    # - forestry
    # - quarry/mine
    # - agriculture (soil, water or irrigation)
    # - special points (highest, lava)

    # activate block caching to speed up requests
    gi.setCaching(True)

    # fine terrain analysis
    heightmap = calculateTreelessHeightmap()

    # for every chunk:
    for cx, cz in toolbox.loop2d(len(chunk_info), len(chunk_info[0])):
        chunkstart = intf.buildlocal2global(cx * 16, 0, cz * 16)
        chunkend = intf.buildlocal2global(cx * 16 + 16, 0, cz * 16 + 16)
        observed = []

        # scan through every fourth block
        for jx, jz in toolbox.loop2d(4, 4):
            localx, localz = cx * 16 + jx * 4, cz * 16 + jz * 4
            globalx, _, globalz = intf.buildlocal2global(localx, 0, localz)
            y = heightmap[localx][localz]
            if (intf.getBlock(globalx, y, globalz) in lookup.ARTIFICIAL
                    and (globalx, y, globalz) not in to_avoid):
                if 'structure' not in chunk_info[cx][cz]['designations']:
                    chunk_info[cx][cz]['designations'] += ['structure']
                result, newly_obs = toolbox.flood_search_3D(globalx, y,
                                                            globalz,
                                                            *chunkstart,
                                                            *chunkend,
                                                            lookup.ARTIFICIAL,
                                                            observed=observed,
                                                            diagonal=True)
                observed += newly_obs
                for rx, ry, rz in result:
                    to_avoid[(rx, ry, rz)] = "Artificial structure detected"

        input('next chunk...')

    debug_chunk_info()

    gi.setCaching(False)

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
