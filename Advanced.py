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
from dataclasses import dataclass
from enum import Enum, auto
from time import time
from typing import List
from random import randrange

from gdpc import geometry as geo
from gdpc import interface as intf
from gdpc import lookup
from gdpc.interface import globalinterface as gi
from gdpc.toolbox import loop2d, loop3d
from gdpc.interface_toolbox import flood_search_3D

PREP_TIME = 120      # permitted preparation time in seconds (2 min)
ALLOWED_TIME = 600  # permitted processing time in seconds (10 min)

# world settings set when generator starts
WORLDDIFFICULTY = "peaceful"
GAMEMODE = "creative"
GAMERULES = ("commandBlockOutput false", "doDaylightCycle true",
             "doEntityDrops true", "doFireTick false",
             "doInsomnia false", "doMobLoot false", "doTileDrops false"
             "doWeatherCycle false", "mobGriefing false", "spawnRadius 1")
WORLDTIME = 22300
WORLDWEATHER = "clear"

# the grid resolution of sub-chunk searches
SUB_CHUNK_RES = 4

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

# blocks that are occupied by something else (key is 3D coords)
# value may anything (e.g. reason for avoidance), since only the key is checked
occupied = {}

# waterways for checking connectivity to ocean and other bodies
# key is a position while value is the name (e.g. ocean, named river or lake)
# waterbody_info stores the biomes which it passes (key is identifier)
# e.g. 'ocean':{'connections': [], 'biomes_touching': [], 'biome_adjacent': []}
# waterbody_names is a lookup for the names of connected chunkwise bodies
# waterfalls stores the locations of waterfalls
RIVER_NAMES = ('Vindur', 'Slidr', 'Mjoll', 'Lifingr', 'Elyitsar', 'Moch',
               'Kerlnosar')
LAKE_NAMES = ()
FOREST_LAKE_NAMES = ()

waterways = dict()
waterbody_info = dict()
waterbody_names = dict()
waterfalls = []

# cave_entrances stores location of cave entrances
cave_entrances = []


class Dimension(Enum):
    """Available dimensions."""
    OVERWORLD = auto()
    NETHER = auto()
    END = auto()


@dataclass
class Position():
    """Represents a location in the world."""
    x: int = 0
    y: int = 65
    z: int = 0
    dimension: Dimension = Dimension.OVERWORLD

    def __add__(self, b):
        if self.dimension != b.dimension:
            raise NotImplementedError("Cannot add Positions "
                                      "with different dimensions.")
        return Position(self.x+b.x, self.y+b.y, self.z+b.z)

    def __sub__(self, b):
        if self.dimension != b.dimension:
            raise NotImplementedError("Cannot subtract Positions "
                                      "with different dimensions.")
        return Position(self.x-b.x, self.y-b.y, self.z-b.z)


@dataclass
class EventType():
    """Describes a type of Event."""
    name: str
    short: str
    long: str


EVENTS = {
    "birth": EventType("{subj.name}'s birth", "{subj.short} was born",
                       "{subj.long} was born in {obj}"),
    "death": EventType("{subj.name}'s death", "{subj.short} has died",
                       "{subj.long} has died of {obj}"),
    "acquiral, unique": EventType("aquiral of {subj.name}",
                                  "{obj.name} aquired {subj.name}",
                                  "{subj.long} had been aquired by {obj.short}"
                                  ),
    "acquiral, gross": EventType("aquiral of {subj.name}",
                                 "{obj.name} aquired {amount} {subj.name}",
                                 "{amount} {subj.long} had been aquired by "
                                 "{obj.short}"),
    "starvation": EventType(*3*"starvation"),
    "food": EventType(*3*"food"),
}


@dataclass
class Event():
    """Stores a specific event."""
    date: int
    subj: None
    obj: None
    text: EventType
    amount: int = 1


class Village():

    def __init__(self, resources: dict, food=10, villagers=10):
        self.resources = {k: (0, v) for k, v in resources.items()}
        self.food = food
        self.villagers = [Person()]
        self.time = 0


class Person():
    """Represents an inhabitant."""
    village: Village
    name: str = None
    position: Position = Position()
    age: int = 0
    history: List(Event) = []

    def live(self):
        event = None
        if self.village.food < 1:
            return self.die(EVENTS["starvation"])
        elif self.village.food < len(self.village.people):
            return self.forage()
        # TODO: add more actions
        return event

    def die(self, reason: EventType):
        event = Event(self.village.time,
                      EVENTS[self.name], reason, EVENTS["death"])
        self.history.append(event)
        return event

    def forage(self):
        event = Event(self.village.time, EVENTS["food"], EVENTS[self.name],
                      EVENTS['acquiral, gross'], randrange(0, 4))
        self.history.append(event)
        return event


def setup_world():
    """Run commands to guarantee player experience is as expected."""
    xcenter = STARTX + (ENDX - STARTX) / 2
    zcenter = STARTZ + (ENDZ - STARTZ) / 2

    # sets world difficulty to peaceful
    intf.runCommand(f"difficulty {WORLDDIFFICULTY}")
    # sets default and all current player's gamemode to survival
    intf.runCommand(f"defaultgamemode {GAMEMODE}")
    intf.runCommand(f"gamemode {GAMEMODE} @a")
    # forced all chunks in build area to remain loaded to prevent generation
    #   issues onvery large maps
    intf.runCommand(f"forceload {STARTX} {STARTZ} {ENDX} {ENDZ}")

    # implements all game rules as previously defined
    for rule in GAMERULES:
        intf.runCommand(f"gamerule {rule}")

    # sets spawnpoint to center of build area
    intf.runCommand(f"setworldspawn {xcenter} 255 {zcenter}")

    # sets world time and weather
    intf.runCommand(f"time set {WORLDTIME}")
    intf.runCommand(f"weather set {WORLDWEATHER}")

    # centers and resizes worldborder to match build area and makes it harmless
    intf.runCommand(f"worldborder center {xcenter} {zcenter}")
    intf.runCommand(f"worldborder set {max(ENDX-STARTX, ENDZ-STARTZ)} 5")
    intf.runCommand("worldborder damage amount 0")


def chunk_biome_analysis():
    """Loop through all chunks in build area and identify biome traits."""
    for x, z in loop2d(XCHUNKSPAN, ZCHUNKSPAN):
        chunk_info[x][z]['primary_biome'] = GLOBALSLICE.getPrimaryBiomeNear(
            STARTX + x * 16, 0, STARTZ + z * 16)
        chunk_info[x][z]['biomes'] = GLOBALSLICE.getBiomesNear(STARTX + x * 16,
                                                               0,
                                                               STARTZ + z * 16)

        chunk_info[x][z]['designations'] = []

        # mark modifiers based on biomes (quicker than singular blocks)
        if 'frozen' in chunk_info[x][z]['biomes']:
            chunk_info[x][z]['designations'].append('frozen_water')

        if ('ocean' in chunk_info[x][z]['primary_biome']
            or 'beach' in chunk_info[x][z]['biomes']
                or 'shore' in chunk_info[x][z]['biomes']):
            chunk_info[x][z]['designations'].append('briny_water')

        elif 'swamp' in chunk_info[x][z]['biomes']:
            chunk_info[x][z]['designations'].append('swamp_water')

        elif 'river' in chunk_info[x][z]['biomes']:
            chunk_info[x][z]['designations'].append('fresh_water')

        if 'snowy' in chunk_info[x][z]['primary_biome']:
            chunk_info[x][z]['designations'].append('snowy')

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

        elif ('plains' in chunk_info[x][z]['primary_biome']
              or 'meadow' in chunk_info[x][z]['primary_biome']
              or 'fields' in chunk_info[x][z]['primary_biome']
              or 'sparse' in chunk_info[x][z]['primary_biome']
              or 'plateau' in chunk_info[x][z]['primary_biome']
                or 'desert' in chunk_info[x][z]['primary_biome']):
            chunk_info[x][z]['designations'].append('flat')


def detect_structures(x, y, z, cx, cz, start_boundries, end_boundries,
                      observed=[]):
    """Detect structures connected to coordinates."""
    global occupied
    global chunk_info

    if 'structure' not in chunk_info[cx][cz]['designations']:
        chunk_info[cx][cz]['designations'].append('structure')
    result, newly_obs = flood_search_3D(x, y, z,
                                        *start_boundries,
                                        *end_boundries,
                                        lookup.ARTIFICIAL,
                                        observed=observed,
                                        diagonal=True)
    observed.update(newly_obs)
    for rx, ry, rz in result:
        occupied[(rx, ry, rz)] = "Artificial structure detected"
    return observed


def detect_water(x, y, z, cx, cz, start_boundries, end_boundries, observed=[]):
    global chunk_info
    if ('briny_water' not in chunk_info[cx][cz]['designations']
        and 'fresh_water' not in chunk_info[cx][cz]['designations']
        and 'swamp_water' not in chunk_info[cx][cz]['designations']
        and 'frozen_water'
            not in chunk_info[cx][cz]['designations']
        and 'stagnant_water'
            not in chunk_info[cx][cz]['designations']):
        chunk_info[cx][cz]['designations'].append('stagnant_water')

    # optimisation for ocean chunks
    if (set('ocean') == set([b[-5:] for b in chunk_info[cx][cz]['biomes']])):
        observed = result = set([p for p
                                 in loop3d(*start_boundries, *end_boundries)])
    else:
        result, newly_obs = flood_search_3D(x, y, z,
                                            *start_boundries,
                                            *end_boundries,
                                            lookup.FLUID,
                                            vectors=lookup.VECTORS[2:],
                                            observed=observed)
        observed.update(newly_obs)

    if 'briny_water' in chunk_info[cx][cz]['designations']:
        name = f'ocean-{cx}-{cz}'
    elif 'fresh_water' in chunk_info[cx][cz]['designations']:
        name = f'river-{cx}-{cz}'
    elif 'swamp_water' in chunk_info[cx][cz]['designations']:
        name = f'swamp-{cx}-{cz}'
    else:
        if len(result) < 256:
            name = f'pond-{cx}-{cz}'
        else:
            name = f'lake-{cx}-{cz}'

    waterbody_info[name] = {'connections': [],
                            'biomes_touching': [],
                            'biome_adjacent': []}
    for rx, ry, rz in result:
        if (rx, ry, rz) in waterways:
            if (waterways[(rx, ry, rz)]
                    not in waterbody_info[name]['connections']):
                waterbody_info[name]['connections'].extend(
                    waterways[(rx, ry, rz)])
        else:
            try:
                waterways[(rx, ry, rz)] = name
                biomes = chunk_info[cx][cz]['biomes']
                waterbody_info[name]['biomes_touching'] = biomes
                surrounding = []

                surrounding.append(chunk_info[cx + 1][cz + 1]['primary_biome'])
                surrounding.append(chunk_info[cx - 1][cz + 1]['primary_biome'])
                surrounding.append(chunk_info[cx + 1][cz - 1]['primary_biome'])
                surrounding.append(chunk_info[cx - 1][cz - 1]['primary_biome'])
            except IndexError as e:
                if (cx != 0 and cz != 0
                    and cx != len(chunk_info) - 1
                        and cz != len(chunk_info[0]) - 1):
                    raise e
    return observed


def detect_cave(x, y, z, cx, cz, start_boundries, end_boundries, observed=[]):
    global chunk_info
    global cave_entrances

    if 'cave_entrance' not in chunk_info[cx][cz]['designations']:
        chunk_info[cx][cz]['designations'].append('cave_entrance')

    # # CAVE NETWORK DETECTION
    # result, newly_obs = flood_search_3D(x, y, z,
    #                                     *start_boundries,
    #                                     *end_boundries,
    #                                     'minecraft:cave_air',
    #                                     observed=observed)
    # observed.update(newly_obs)
    #
    # for rx, ry, rz in result:
    #     cave_entrances.append(x, y, z)
    return observed


def calculateTreelessHeightmap(worldSlice=GLOBALSLICE, interface=gi):
    heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    area = worldSlice.rect

    for x, z in loop2d(area[2], area[3]):
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
                      'briny_water': 'prismarine',
                      'frozen_water': 'packed_ice',
                      'fresh_water': 'light_blue_wool',
                      'swamp_water': 'stripped_warped_hyphae',
                      'stagnant_water': 'light_blue_shulker_box',
                      'harsh': 'stone', 'flat': 'grass_block',
                      'structure': 'emerald_block',
                      'cave_entrance': 'spruce_trapdoor'}

        for x, z in loop2d(len(chunk_info), len(chunk_info[0])):
            blocks = [conversion[d] for d in chunk_info[x][z]['designations']]
            if blocks == []:
                blocks = 'redstone_block'
            geo.placeVolume(STARTX + x * 16 + 5, 250, STARTZ + z * 16 + 5,
                            STARTX + x * 16 + 8, 250, STARTZ + z * 16 + 8,
                            blocks)

        input('Enter to clear')
        geo.placeVolume(STARTX, 250, STARTZ, ENDX - 1, 250, ENDZ - 1, 'air')

    def simulate():
        """Simulate the passing of a day."""
        pass

    setup_world()

    # simulate civilisation
    cycle = 0
    people = []

    while time() - start <= PREP_TIME:
        cycle += 1
        simulate()

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

    # 16x16 chunk resolution analyses
    chunk_biome_analysis()

    # fine terrain analysis
    heightmap = calculateTreelessHeightmap()

    # 4x4-resolution block analysis for every chunk
    for cx, cz in loop2d(len(chunk_info), len(chunk_info[0])):
        print((cx, cz))
        chunkstart = intf.buildlocal2global(cx * 16, 0, cz * 16)
        chunkend = intf.buildlocal2global(cx * 16 + 16, 255, cz * 16 + 16)
        overlap_chunkstart = chunkstart[0] - \
            1, chunkstart[1], chunkstart[2] - 1
        overlap_chunkend = chunkend[0], chunkend[1], chunkend[2]
        obs_struc = set()
        obs_fluid = set()
        obs_cave = set()

        # scan through the corner of every subchunk
        for jx, jz in loop2d(SUB_CHUNK_RES, SUB_CHUNK_RES):
            localx = cx * 16 + jx * SUB_CHUNK_RES
            localz = cz * 16 + jz * SUB_CHUNK_RES
            globalx, _, globalz = intf.buildlocal2global(localx, 0, localz)
            y = heightmap[localx][localz]

            # STRUCTURE DETECTION
            if (intf.getBlock(globalx, y, globalz) in lookup.ARTIFICIAL
                    and (globalx, y, globalz) not in occupied):
                obs_struc = detect_structures(globalx, y, globalz, cx, cz,
                                              chunkstart, chunkend, obs_struc)
            # WATER DETECTION
            elif (intf.getBlock(globalx, y, globalz) in lookup.FLUID
                    and (globalx, y, globalz) not in waterways):
                obs_fluid = detect_water(globalx, y, globalz, cx, cz,
                                         overlap_chunkstart, overlap_chunkend,
                                         obs_fluid)
            # CAVE DETECTION
            elif intf.getBlock(globalx, y, globalz) == 'minecraft:cave_air':
                obs_cave = detect_cave(globalx, y, globalz, cx, cz,
                                       overlap_chunkstart, overlap_chunkend,
                                       obs_cave)

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
