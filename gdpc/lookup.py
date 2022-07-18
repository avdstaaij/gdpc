#! /usr/bin/python3
"""### Store lists of various information on blocks, biomes and more."""

# __all__ = []  # everything is available for import
__version__ = "v5.1_dev"

from typing import Set
import os
import sys
from .toolbox import isSequence

# to translate a string of regular names
# into the appropriate list of minecraft block IDs
# >>> def f(string):
# >>>     return ["minecraft:" + i.strip().lower().replace(" ", "_")
# >>>         for i in string.split(", ")]

# to translate a 255 RGB to hex RGB value
# >>> def f(r, g, b): return "0x"+(hex(r)+hex(g)+hex(b)).replace("0x", "")

# See https://minecraft.fandom.com/wiki/Data_version#List_of_data_versions
SUPPORTS = 2566  # Supported Minecraft version code

# all major Minecraft version codes
VERSIONS = {
    2860: "1.18",
    2865: "1.18.1",
    2724: "1.17",
    2730: "1.17.1",
    2566: "1.16",
    2567: "1.16.1",
    2578: "1.16.2",
    2580: "1.16.3",
    2584: "1.16.4",
    2586: "1.16.5",
    2225: "1.15",
    2227: "1.15.1",
    2230: "1.15.2",
    1952: "1.14",
    1957: "1.14.1",
    1963: "1.14.2",
    1968: "1.14.3",
    1976: "1.14.4",
    1519: "1.13",
    1628: "1.13.1",
    1631: "1.13.2",
    1139: "1.12",
    1241: "1.12.1",
    1343: "1.12.2",
    819: "1.11",
    921: "1.11.1",
    922: "1.11.2",
    510: "1.10",
    511: "1.10.1",
    512: "1.10.2",
    169: "1.9",
    175: "1.9.1",
    176: "1.9.2",
    183: "1.9.3",
    184: "1.9.4",
    0: "Pre-1.9",
}
VERSIONIDS = dict([(value, key) for key, value in VERSIONS.items()])


# ========================================================= custom values


AXES = ("x", "y", "z")
DIRECTIONS = ("top", "bottom", "north", "east", "south", "west")
VECTORS = ((0, 1, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0))
DIAGONALVECTORS = (
    (1, 1, 0),
    (1, 0, 1),
    (0, 1, 1),
    (1, -1, 0),
    (1, 0, -1),
    (0, 1, -1),
    (-1, 1, 0),
    (-1, 0, 1),
    (0, -1, 1),
    (-1, -1, 0),
    (-1, 0, -1),
    (0, -1, -1),
    (1, 1, 1),
    (1, 1, -1),
    (1, -1, 1),
    (-1, 1, 1),
    (1, -1, -1),
    (-1, -1, 1),
    (-1, 1, -1),
    (-1, -1, -1),
)
INVERTDIRECTION = {
    "top": "bottom",
    "bottom": "top",
    "north": "south",
    "east": "west",
    "south": "north",
    "west": "east",
}
DIRECTION2VECTOR = {
    "top": (0, 1, 0),
    "bottom": (0, -1, 0),
    "north": (0, 0, -1),
    "east": (1, 0, 0),
    "south": (0, 0, 1),
    "west": (-1, 0, 0),
}
VECTOR2DIRECTION = dict([(val, key) for key, val in DIRECTION2VECTOR.items()])
AXIS2VECTOR = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}
VECTOR2AXIS = dict([(val, key) for key, val in AXIS2VECTOR.items()])

# ========================================================= materials


def variate(variations, extensions=None, isprefix=False,
            namespace="minecraft:", separator="_", ns_separator=":") -> set:
    """Generate block variations.

    TODO: documentation
    TODO: refactor to take optional suffix and prefix, replace named types
    """
    if not isSequence(variations):
        # TODO: improve error message
        raise ValueError()
    joined = None
    if extensions is None:
        joined = variations
    elif isinstance(extensions, str):
        combinations = {(v, extensions) for v in variations}
    elif isSequence(extensions):
        combinations = {(v, e) for v in variations for e in extensions}
    if isprefix:
        combinations = {(e, v) for v, e in combinations}
    if namespace is None:
        namespace, ns_separator = "", ""
    elif ns_separator is None:
        ns_separator = ""
    if separator is None:
        separator = ""

    if joined is None:
        joined = {separator.join(c) for c in combinations}
    return {f"{namespace}{ns_separator}{j}" for j in joined}


# COLOURS
# based on https://minecraft.fandom.com/wiki/Dye#Color_values
#   and https://minecraft.fandom.com/wiki/Block_colors
DYE_COLORS = {
    "white": "0xF9FFFE",
    "orange": "0xF9801D",
    "magenta": "0xC74EBD",
    "light_blue": "0x3AB3DA",
    "yellow": "0xFED83D",
    "lime": "0x80C71F",
    "pink": "0xF38BAA",
    "gray": "0x474F52",
    "light_gray": "0x9D9D97",
    "cyan": "0x169C9C",
    "purple": "0x8932B8",
    "blue": "0x3C44AA",
    "brown": "0x835432",
    "green": "0x5E7C16",
    "red": "0xB02E26",
    "black": "0x1D1D21",
}
GRASS_COLORS = {
    "generic": "0x8EB971",
    "desert": "0xBFB755",
    "badlands": "0x90814D",
    "plains": "0x91BD59",
    "taiga": "0x86B783", "pine_taiga": "0x86B87F",
    "meadow": "0x83BB6D",
    "snowy": "0x80B497", "snowy_beach": "0x83B593",
    "forest": "0x79C05A", "birch_forest": "0x88BB67",
    "dark_forest": "0x507A32",
    "sparse_jungle": "0x64C73F", "jungle": "0x59C93C",
    "mushroom_fields": "0x55C93F",
    "stony_peaks": "0x9ABE4B",
    "windswept": "0x8AB689",
    "swamp_brown": "0x6A7039", "swamp_green": "0x4C763C",
}
FOLIAGE_COLORS = {
    "generic": "0x71A74D",
    "desert": "0xAEA42A",
    "badlands": "0x9E814D",
    "plains": "0x77AB2F",
    "taiga": "0x68A464", "pine_taiga": "0x68A55F",
    "meadow": "0x63A948",
    "snowy": "0x60A17B", "snowy_beach": "0x64A278",
    "forest": "0x59AE30", "birch_forest": "0x6BA941",
    "sparse_jungle": "0x3EB80F", "jungle": "0x30BB0B",
    "mushroom_fields": "0x2BBB0F",
    "stony_peaks": "0x82AC1E",
    "windswept": "0x6DA36B",
    "swamp": "0x6A7039",
}
WATER_COLORS = {
    "generic": "0x3F76E4",
    "meadow": "0x0E4ECF",
    "warm": "0x43D5EE",
    "lukewarm": "0x45ADF2",
    "cold": "0x3D57D6",
    "frozen": "0x3938C9",
    "swamp": "0x617B64",
}
REDSTONE_COLORS = {
    "0": "0x4B0000",
    "1": "0x6F0000",
    "2": "0x790000",
    "3": "0x820000",
    "4": "0x8C0000",
    "5": "0x970000",
    "6": "0xA10000",
    "7": "0xAB0000",
    "8": "0xB50000",
    "9": "0xBF0000",
    "10": "0xCA0000",
    "11": "0xD30000",
    "12": "0xDD0000",
    "13": "0xE70600",
    "14": "0xF11B00",
    "15": "0xFC3100",
}

# SHADES
# alternative terms that directly correlate with a dye color
CORAL_SHADES = {"tube": "blue", "brain": "pink", "bubble": "purple",
                "fire": "red", "horn": "yellow", "dead": "grey"}

# TERMINOLOGY
# words used to describe categorically similar types
CRIMSON_WORDS = {"crimson", "wart", "weeping", }
WARPED_WORDS = {"warped", "sprouts", "twisted"}


# MATERIAL TYPES
SAND_TYPES = {None, "red", }
IGNEOUS_TYPES = {"andesite", "diorite", "granite", }
STONE_TYPES = {"stone", "cobblestone", }
COBBLESTONE_TYPES = {None, "mossy", }

ORE_TYPES = {"coal", "lapis", "iron", "gold",
             "redstone", "diamond", "emerald", }
NETHER_ORE_TYPES = {"gold", "quartz", }

LIMITED_SANDSTONE_TYPES = {None, "smooth", }
SANDSTONE_TYPES = {"cut", "chiseled", } | LIMITED_SANDSTONE_TYPES
BASALT_TYPES = {None, "smooth", "polished", }
OBSIDIAN_TYPES = {None, "crying", }
STEMFRUIT_TYPES = {"pumpkin", "melon", }

AIR_TYPES = {None, "void", "cave", }
FIRE_TYPES = {None, "soul", }

ICE_TYPES = {None, "blue", "packed", "frosted"}
LIQUID_TYPES = {None, "flowing", }

WOOD_TYPES = {"oak", "birch", "spruce", "jungle",
              "dark_oak", "acacia", }
MUSHROOM_TYPES = {"brown", "red", }
WART_TYPES = {"nether", "warped", }
FUNGUS_TYPES = {"crimson", "warped", }
FUNGUS_VINE_TYPES = {"weeping", "twisting", }

TULIP_TYPES = {"red", "orange", "white", "pink"}
SMALL_FLOWER_TYPES = {"dandelion", "poppy", "blue_orchid", "allium",
                      "azure_bluet", "oxeye_daisy", "cornflower",
                      "lily_of_the_valley", "wither_rose"} \
    | variate(TULIP_TYPES, "tulip", namespace=None)
TALL_FLOWER_TYPES = {"sunflower", "lilac", "rose_bush", "peony"}

LIVE_CORAL_TYPES = set(CORAL_SHADES) - {"dead"}
DEAD_CORAL_TYPES = variate(LIVE_CORAL_TYPES, "dead",
                           isprefix=True, namespace=None)
CORAL_TYPES = LIVE_CORAL_TYPES | DEAD_CORAL_TYPES

WOODY_TYPES = WOOD_TYPES | FUNGUS_TYPES

LIMITED_STONE_BRICK_TYPES = {None, "mossy", }
STONE_BRICK_TYPES = {"cracked", "chiseled", } | LIMITED_STONE_BRICK_TYPES

NETHER_BRICK_TYPES = {None, "red", }

QUARTZ_TYPES = {None, "smooth", }
QUARTZ_BLOCK_TYPES = {"block", "pillar", "bricks", }
POLISHED_BLACKSTONE_TYPES = {None, "bricks", }
POLISHED_BLACKSTONE_BRICK_TYPES = {None, "cracked", }
SMOOTH_SANDSTONE_TYPES = variate(SAND_TYPES, "smooth",
                                 isprefix=True, namespace=None)
CUT_SANDSTONE_TYPES = variate(SAND_TYPES, "cut",
                              isprefix=True, namespace=None)
PRISMARINE_TYPES = {None, "dark", }
NETHER_BRICK_TYPES = {None, "red", "cracked", "chiseled", }
PURPUR_TYPES = {"block", "pillar", }

ANVIL_TYPES = {None, "chipped", "damaged", }
CHEST_TYPES = {None, "trapped", "end", }
CAULDRON_TYPES = {None, "lave", "powder_snow", "water", }

SPONGE_TYPES = {None, "wet", }
HEAD_TYPES = {"skeleton", "wither_skeleton", "zombie", "player", "creeper",
              "dragon", }

WEIGHTED_PRESSURE_PLATE_TYPES = {"heavy", "light", }
SENSOR_RAIL_TYPES = {"detector", }
ACTUATOR_RAIL_TYPES = {None, "activator", "powered", }
PISTON_TYPES = {None, "sticky", }
COMMAND_BLOCK_TYPES = {None, "chain", "repeating", }

# NAMED MATERIAL TYPES
# for usage as an extension
NAMED_STONE_BRICK_TYPES = variate(STONE_BRICK_TYPES, "stone_brick",
                                  namespace=None)
NAMED_WOOD_TYPES = variate(WOOD_TYPES, "wood", namespace=None)
NAMED_LOG_TYPES = variate(WOOD_TYPES, "log", namespace=None)
NAMED_STEM_TYPES = variate(FUNGUS_TYPES, "stem", namespace=None)
NAMED_HYPHAE_TYPES = variate(FUNGUS_TYPES, "hyphae", namespace=None)

NAMED_LIVE_CORAL_TYPES = variate(LIVE_CORAL_TYPES, "coral", namespace=None)
NAMED_DEAD_CORAL_TYPES = variate(DEAD_CORAL_TYPES, "coral", namespace=None)
NAMED_CORAL_TYPES = NAMED_LIVE_CORAL_TYPES | NAMED_DEAD_CORAL_TYPES

NAMED_POLISHED_BLACKSTONE_TYPES = \
    variate(POLISHED_BLACKSTONE_TYPES, "polished_blackstone",
            isprefix=True, namespace=None)
NAMED_POLISHED_IGNEOUS_TYPES = variate(IGNEOUS_TYPES, "polished",
                                       isprefix=True, namespace=None)
NAMED_PRISMARINE_TYPES = variate(PRISMARINE_TYPES, "prismarine",
                                 namespace=None)

# ========================================================= grouped by model

# natural
# minerals
OVERWORLD_ORES = variate(ORE_TYPES, "ore")

NETHERRACK_ORES = variate(NETHER_ORE_TYPES, "ore")
NETHER_ORES = {"minecraft:gilded_blackstone", } | NETHERRACK_ORES

END_ORES: Set[str] = set()

ORES = OVERWORLD_ORES | NETHER_ORES | END_ORES

MINERAL_BLOCKS = {"minecraft:quartz_block", } \
    | variate(ORE_TYPES, "block")

# soils
SPREADING_DIRTS = {"minecraft:mycelium", "minecraft:grass_block", }
DIRTS = {"minecraft:coarse_dirt", "minecraft:dirt",
         "minecraft:dirt_path", "minecraft:farmland", "minecraft:podzol", } \
    | SPREADING_DIRTS
SANDS = variate(SAND_TYPES, "sand")
GRANULARS = {"minecraft:gravel", } | SANDS
RIVERBED_SOILS = {"minecraft:dirt", "minecraft:clay",
                  "minecraft:sand", "minecraft:gravel", }
OVERWORLD_SOILS = DIRTS | GRANULARS | RIVERBED_SOILS

NYLIUMS = variate(FUNGUS_TYPES, "nylium")
NETHERRACKS = {"minecraft:netherrack", } | NYLIUMS | NETHERRACK_ORES
SOUL_SOILS = {"minecraft:soul_sand", "minecraft:soul_soil", }
NETHER_SOILS = NYLIUMS | SOUL_SOILS

END_SOILS: Set[str] = set()

SOILS = OVERWORLD_SOILS | NETHER_SOILS | END_SOILS

# stones
IGNEOUS = variate(IGNEOUS_TYPES)
OBSIDIANS = variate(OBSIDIAN_TYPES, "obsidian")
COBBLESTONES = variate(COBBLESTONE_TYPES, "cobblestone")
INFESTED = variate(STONE_TYPES | NAMED_STONE_BRICK_TYPES, "infested",
                   isprefix=True)
RAW_SANDSTONES = variate(SAND_TYPES, "sandstone")
TERRACOTTAS = {{None, } | set(DYE_COLORS), "terracotta"}
OVERWORLD_STONES = {"minecraft:stone", } | IGNEOUS | OBSIDIANS | COBBLESTONES \
    | INFESTED | RAW_SANDSTONES | TERRACOTTAS

BASALTS = variate(BASALT_TYPES, "basalt")
NETHER_STONES = {"minecraft:blackstone", }

END_STONES = {"minecraft:end_stone", }

VOLCANIC = {"minecraft:magma_block", } | BASALTS | OBSIDIANS
STONES = {"minecraft:bedrock", } | VOLCANIC \
    | OVERWORLD_STONES | NETHER_STONES | END_STONES

# liquids
SNOWS = {"minecraft:powder_snow", "minecraft:snow", "minecraft:snow_block", }
ICES = variate(ICE_TYPES, "ice")
WATERS = variate(LIQUID_TYPES, "water")
WATER_BASED = {"minecraft:bubble_column", } | SNOWS | ICES | WATERS
LAVAS = variate(LIQUID_TYPES, "lava")
LAVA_BASED = VOLCANIC | LAVAS
LIQUIDS = WATERS | LAVAS
LIQUID_BASED = WATER_BASED | LAVA_BASED

# non-physical
AIRS = variate(AIR_TYPES, "air")
FLUIDS = LIQUIDS | AIRS
FIRES = variate(FIRE_TYPES, "fire")

# life
# fungals (mushrooms and fungi)
SMALL_MUSHROOMS = variate(MUSHROOM_TYPES, "mushroom")
MUSHROOM_CAPS = variate(MUSHROOM_TYPES, "mushroom_block")
MUSHROOM_STEMS = {"minecraft:mushroom_stem", }
MUSHROOM_BLOCKS = MUSHROOM_CAPS | MUSHROOM_STEMS
MUSHROOMS = SMALL_MUSHROOMS | MUSHROOM_BLOCKS

SMALL_DECORATIVE_FUNGI = {"minecraft:nether_sprout", } \
    | variate(FUNGUS_TYPES, "fungus")
SMALL_FARMABLE_FUNGI = {"minecraft:nether_wart", } \
    | variate(FUNGUS_TYPES, "roots")
SMALL_FUNGI = SMALL_DECORATIVE_FUNGI | SMALL_FARMABLE_FUNGI
WART_BLOCKS = variate(WART_TYPES, "wart_block")
FUNGUS_VINES = variate(FUNGUS_VINE_TYPES, "vines")

BARKED_FUNGUS_STEMS = variate(FUNGUS_TYPES, "stem")
BARKED_FUNGUS_HYPHAE = variate(FUNGUS_TYPES, "hyphae")
BARKED_FUNGUS_STALKS = BARKED_FUNGUS_STEMS | BARKED_FUNGUS_HYPHAE
STRIPPED_FUNGUS_STEMS = variate(NAMED_STEM_TYPES, "stripped", isprefix=True)
STRIPPED_FUNGUS_HYPHAE = variate(NAMED_HYPHAE_TYPES, "stripped", isprefix=True)
STRIPPED_FUNGUS_STALKS = STRIPPED_FUNGUS_STEMS | STRIPPED_FUNGUS_HYPHAE
FUNGUS_STEMS = BARKED_FUNGUS_STEMS | STRIPPED_FUNGUS_STEMS
FUNGUS_HYPHAE = BARKED_FUNGUS_HYPHAE | STRIPPED_FUNGUS_HYPHAE
FUNGUS_STALKS = FUNGUS_STEMS | FUNGUS_HYPHAE
FUNGUS_GROWTH_BLOCKS = {"minecraft:shroomlight", } \
    | WART_BLOCKS | FUNGUS_STALKS
FUNGI = SMALL_FUNGI | FUNGUS_GROWTH_BLOCKS

SMALL_FUNGALS = SMALL_MUSHROOMS | SMALL_FUNGI
FUNGAL_CAPS = MUSHROOM_CAPS | WART_BLOCKS
FUNGAL_STEMS = MUSHROOM_STEMS | FUNGUS_STEMS
FUNGAL_BLOCKS = MUSHROOM_BLOCKS | FUNGUS_GROWTH_BLOCKS
FUNGALS = SMALL_FUNGALS | FUNGAL_BLOCKS

VINES = {"minecraft:vines", } | FUNGUS_VINES

# trees
SAPLINGS = variate(WOOD_TYPES, "sapling")
LEAVES = variate(WOOD_TYPES, "leaves")
FOLIAGE = {"minecraft:vines", } | LEAVES

BARKED_LOGS = variate(WOOD_TYPES, "log")
BARKED_WOODS = variate(WOOD_TYPES, "wood")
BARKED_TRUNKS = BARKED_LOGS | BARKED_WOODS
STRIPPED_LOGS = variate(NAMED_LOG_TYPES, "stripped", isprefix=True)
STRIPPED_WOODS = variate(NAMED_WOOD_TYPES, "stripped", isprefix=True)
STRIPPED_TRUNKS = STRIPPED_LOGS | STRIPPED_WOODS
WOODS = BARKED_TRUNKS | STRIPPED_WOODS
LOGS = BARKED_LOGS | STRIPPED_LOGS
TRUNKS = BARKED_TRUNKS | STRIPPED_TRUNKS

BARKED_TREE_BLOCKS = LEAVES | BARKED_WOODS | BARKED_LOGS
TREE_BLOCKS = LEAVES | WOODS | LOGS
TREES = SAPLINGS | TREE_BLOCKS

# grasses
TRUE_GRASSES = {"minecraft:grass_block",
                "minecraft:grass", "minecraft:tall_grass", }
FERNS = {"minecraft:fern", "minecraft:large_fern", }
BAMBOOS = {"minecraft:bamboo", "minecraft:bamboo_sapling", }

GRASS_BLOCKS = {"minecraft:grass_block", }
SHORT_GRASSES = {"minecraft:grass", "minecraft:fern", }
TALL_GRASSES = {"minecraft:tall_grass", "minecraft:large_fern", }
CANE_GRASSES = {"minecraft:sugar_cane", } | BAMBOOS

GRASS_PLANTS = SHORT_GRASSES | TALL_GRASSES | CANE_GRASSES
GRASSES = GRASS_BLOCKS | GRASS_PLANTS

# crops
PUMPKINS = {"minecraft:pumpkin", "minecraft:carved_pumpkin", }
BLOCK_CROP_STEMS = variate(STEMFRUIT_TYPES, "stem")
BLOCK_CROP_FRUITS = variate(STEMFRUIT_TYPES)
BLOCK_CROPS = BLOCK_CROP_STEMS | BLOCK_CROP_FRUITS

FARMLAND_CROPS = {"minecraft:wheat", "minecraft:carrots",
                  "minecraft:potatoes", "minecraft:beetroots", } \
    | BLOCK_CROP_STEMS
WILD_CROPS = {"minecraft:cocoa", "minecraft:sweet_berry_bush", }

CROPS = BLOCK_CROPS | FARMLAND_CROPS | WILD_CROPS

# flowers
TULIPS = variate(TULIP_TYPES, "tulip")
SMALL_FLOWERS = variate(SMALL_FLOWER_TYPES)
TALL_FLOWERS = variate(TALL_FLOWER_TYPES)
FLOWERS = SMALL_FLOWERS | TALL_FLOWERS

# aquatic flora
SEAGRASSES = {"minecraft:seagrass", "minecraft:tall_seagrass", }
KELP = {"minecraft:kelp_plant", "minecraft:kelp", }
WATER_PLANTS = {"minecraft:lily_pad", } | SEAGRASSES | KELP

OVERWORLD_PLANT_BLOCKS = MUSHROOM_BLOCKS | TREE_BLOCKS
OVERWORLD_PLANTS = {"minecraft:cactus", "minecraft:dead_bush", } \
    | MUSHROOMS | FOLIAGE | TREES | GRASSES | CROPS | FLOWERS | WATER_PLANTS

NETHER_PLANT_BLOCKS = FUNGUS_GROWTH_BLOCKS
NETHER_PLANTS = FUNGI

CHORUS = {"minecraft:chorus_plant", "minecraft:chorus_flower", }
END_PLANT_BLOCKS: Set[str] = set()
END_PLANTS = CHORUS

PLANT_BLOCKS = OVERWORLD_PLANT_BLOCKS | NETHER_PLANT_BLOCKS | END_PLANT_BLOCKS
PLANTS = OVERWORLD_PLANTS | NETHER_PLANTS | END_PLANTS

# marine life
LIVE_CORAL_BLOCKS = variate(NAMED_LIVE_CORAL_TYPES, "block")
LIVE_CORAL_COLONY = variate(LIVE_CORAL_TYPES, "coral")
LIVE_CORAL_FANS = variate(NAMED_LIVE_CORAL_TYPES, "fan")
LIVE_CORALS = LIVE_CORAL_BLOCKS | LIVE_CORAL_COLONY | LIVE_CORAL_FANS
DEAD_CORAL_BLOCKS = variate(NAMED_DEAD_CORAL_TYPES, "block")
DEAD_CORAL_COLONY = variate(DEAD_CORAL_TYPES, "coral")
DEAD_CORAL_FANS = variate(NAMED_DEAD_CORAL_TYPES, "fan")
DEAD_CORALS = DEAD_CORAL_BLOCKS | DEAD_CORAL_COLONY | DEAD_CORAL_FANS
CORAL_BLOCKS = LIVE_CORAL_BLOCKS | DEAD_CORAL_BLOCKS
CORAL_COLONY = LIVE_CORAL_COLONY | DEAD_CORAL_COLONY
CORAL_FANS = LIVE_CORAL_FANS | DEAD_CORAL_FANS

CORALS = LIVE_CORALS | DEAD_CORALS

MARINE_ANIMALS = {"minecraft:sea_pickle", } | CORALS
MARINE_LIFE = WATER_PLANTS | MARINE_ANIMALS

OVERWORLD_ANIMALS = MARINE_ANIMALS
NETHER_ANIMALS: Set[str] = set()
END_ANIMALS: Set[str] = set()
ANIMALS = OVERWORLD_ANIMALS | NETHER_ANIMALS | END_ANIMALS

# animal product
EGGS = {"minecraft:dragon_egg", "minecraft:turtle_egg", }
BEE_NESTS = {"minecraft:beehive", "minecraft:bee_nest", }
NESTS = {"minecraft:bee_nest", "minecraft:cobweb", }
REMAINS = {"minecraft:bone_block", }

OVERWORLD_ANIMAL_PRODUCTS = {"minecraft:turtle_egg", "honeycomb_block"} \
    | EGGS | NESTS
NETHER_ANIMAL_PRODUCTS: Set[str] = set()
END_ANIMAL_PRODUCTS = {"minecraft:dragon_egg", }
ANIMAL_PRODUCTS = REMAINS \
    | OVERWORLD_ANIMAL_PRODUCTS | NETHER_ANIMAL_PRODUCTS | END_ANIMAL_PRODUCTS

OVERWORLD_LIFE = OVERWORLD_PLANTS | OVERWORLD_ANIMALS
NETHER_LIFE = NETHER_PLANTS | NETHER_ANIMALS
END_LIFE = END_PLANTS | END_ANIMALS
LIFE = OVERWORLD_LIFE | NETHER_LIFE | END_LIFE

# building
# decoration
WOOLS = variate(DYE_COLORS, "wool")
CARPETS = variate(DYE_COLORS, "carpet")

STAINED_GLASS_BLOCKS = variate(DYE_COLORS, "stained_glass")
GLASS_BLOCKS = {"minecraft:glass", } | STAINED_GLASS_BLOCKS
STAINED_GLASS_PANES = variate(DYE_COLORS, "stained_glass_panes")
GLASS_PANES = {"minecraft:glass_pane", } | STAINED_GLASS_PANES
STAINED_GLASS = STAINED_GLASS_BLOCKS | STAINED_GLASS_PANES
PLAIN_GLASS = {"minecraft:glass", "minecraft:glass_pane", }
GLASS = GLASS_BLOCKS | GLASS_PANES

# slabs
WOOD_SLABS = variate(WOOD_TYPES, "slab")
FUNGUS_SLABS = variate(FUNGUS_TYPES, "slab")
WOODY_SLABS = WOOD_SLABS | FUNGUS_SLABS
STONE_SLABS = {"minecraft:stone_slab", "minecraft:smooth_stone_slab", }
RAW_IGNEOUS_SLABS = variate(IGNEOUS_TYPES, "slab")
POLISHED_IGNEOUS_SLABS = variate(NAMED_POLISHED_IGNEOUS_TYPES, "slab")
IGNEOUS_SLABS = RAW_IGNEOUS_SLABS | POLISHED_IGNEOUS_SLABS
COBBLESTONE_SLABS = variate(COBBLESTONE_TYPES, "cobblestone_slab")
STONE_BRICK_SLABS = variate(LIMITED_STONE_BRICK_TYPES, "stone_brick_slab")
RAW_SANDSTONE_SLABS = variate(SAND_TYPES, "sandstone_slab")
SMOOTH_SANDSTONE_SLABS = variate(SMOOTH_SANDSTONE_TYPES, "sandstone_slab")
CUT_SANDSTONE_SLABS = variate(CUT_SANDSTONE_TYPES, "sandstone_slab")
SANDSTONE_SLABS = RAW_SANDSTONE_SLABS | SMOOTH_SANDSTONE_SLABS \
    | CUT_SANDSTONE_SLABS
PRISMARINE_SLABS = {"minecraft:prismarine_brick_slab", } \
    | variate(NAMED_PRISMARINE_TYPES, "slab")
NETHER_BRICK_SLABS = variate(NETHER_BRICK_TYPES, "nether_brick_slab")
QUARTZ_SLABS = variate(QUARTZ_TYPES, "quartz_slab")
BLACKSTONE_SLABS = {"minecraft:blackstone_slab", } \
    | variate(NAMED_POLISHED_BLACKSTONE_TYPES, "_slab")
OVERWORLD_SLABS = {"minecraft:brick_slab", }
NETHER_SLABS = NETHER_BRICK_SLABS | QUARTZ_SLABS | BLACKSTONE_SLABS
END_SLABS = {"minecraft:end_stone_brick_slab", "minecraft:purpur_slab", }
SLABS = OVERWORLD_SLABS | NETHER_SLABS | END_SLABS

# stairs
WOOD_STAIRS = variate(WOOD_TYPES, "stairs")
FUNGUS_STAIRS = variate(FUNGUS_TYPES, "stairs")
WOODY_STAIRS = WOOD_STAIRS | FUNGUS_STAIRS
STONE_STAIRS = {"minecraft:stone_stairs", }
RAW_IGNEOUS_STAIRS = variate(IGNEOUS_TYPES, "stairs")
POLISHED_IGNEOUS_STAIRS = variate(NAMED_POLISHED_IGNEOUS_TYPES, "stairs")
IGNEOUS_STAIRS = RAW_IGNEOUS_STAIRS | POLISHED_IGNEOUS_STAIRS
COBBLESTONE_STAIRS = variate(COBBLESTONE_TYPES, "cobblestone_stairs")
STONE_BRICK_STAIRS = variate(LIMITED_STONE_BRICK_TYPES, "stone_brick_stairs")
RAW_SANDSTONE_STAIRS = variate(SAND_TYPES, "sandstone_stairs")
SMOOTH_SANDSTONE_STAIRS = variate(SMOOTH_SANDSTONE_TYPES, "sandstone_stairs")
SANDSTONE_STAIRS = RAW_SANDSTONE_STAIRS | SMOOTH_SANDSTONE_STAIRS
PRISMARINE_STAIRS = {"minecraft:prismarine_brick_stairs", } \
    | variate(NAMED_PRISMARINE_TYPES, "stairs")
NETHER_BRICK_STAIRS = variate(NETHER_BRICK_TYPES, "nether_brick_stairs")
QUARTZ_STAIRS = variate(QUARTZ_TYPES, "quartz_stairs")
BLACKSTONE_STAIRS = {"minecraft:blackstone_stairs", } \
    | variate(NAMED_POLISHED_BLACKSTONE_TYPES, "_stairs")
OVERWORLD_STAIRS = {"minecraft:brick_stairs", }
NETHER_STAIRS = NETHER_BRICK_STAIRS | QUARTZ_STAIRS | BLACKSTONE_STAIRS
END_STAIRS = {"minecraft:end_stone_brick_stairs", "minecraft:purpur_stairs", }
STAIRS = OVERWORLD_STAIRS | NETHER_STAIRS | END_STAIRS


# barriers
WOOD_FENCES = variate(WOOD_TYPES, "fence")
FUNGUS_FENCES = variate(FUNGUS_TYPES, "fence")
WOODY_FENCES = WOOD_FENCES | FUNGUS_FENCES
OVERWORLD_FENCES = WOOD_FENCES
NETHER_FENCES = {"minecraft:nether_brick_fence", } | FUNGUS_FENCES
END_FENCES: Set[str] = set()
FENCES = OVERWORLD_FENCES | NETHER_FENCES | END_FENCES

COBBLESTONE_WALLS = variate(COBBLESTONE_TYPES, "cobblestone_wall")
STONE_BRICK_WALLS = variate(LIMITED_STONE_BRICK_TYPES, "stone_brick_wall")
IGNEOUS_WALLS = variate(IGNEOUS_TYPES, "wall")
SANDSTONE_WALLS = variate(SAND_TYPES, "sandstone_wall")
NETHER_BRICK_WALLS = variate(NETHER_BRICK_TYPES, "nether_brick_wall")
BLACKSTONE_WALLS = {"minecraft:blackstone_wall", } \
    | variate(NAMED_POLISHED_BLACKSTONE_TYPES, "wall")
OVERWORLD_WALLS = {"minecraft:prismarine_wall", } \
    | COBBLESTONE_WALLS | STONE_BRICK_WALLS | IGNEOUS_WALLS | SANDSTONE_WALLS
NETHER_WALLS = NETHER_BRICK_WALLS | BLACKSTONE_WALLS
END_WALLS = {"end_stone_brick_wall", }
WALLS = OVERWORLD_WALLS | NETHER_BRICK_WALLS | END_WALLS

OVERWORLD_BARRIERS = OVERWORLD_FENCES | OVERWORLD_WALLS
NETHER_BARRIERS = NETHER_FENCES | NETHER_WALLS
END_BARRIERS = END_FENCES | END_WALLS
BARRIERS = FENCES | WALLS

# entryways
WOOD_DOORS = variate(WOOD_TYPES, "door")
FUNGUS_DOORS = variate(FUNGUS_TYPES, "door")
WOODY_DOORS = WOOD_DOORS | FUNGUS_DOORS
METAL_DOORS = {"minecraft:iron_door", }
OVERWORLD_DOORS = WOOD_DOORS | METAL_DOORS
NETHER_DOORS = FUNGUS_DOORS | METAL_DOORS
END_DOORS = METAL_DOORS
DOORS = OVERWORLD_DOORS | NETHER_DOORS | END_DOORS

WOOD_GATES = variate(WOOD_TYPES, "fence_gate")
FUNGUS_GATES = variate(FUNGUS_TYPES, "fence_gate")
WOODY_GATES = WOOD_GATES | FUNGUS_GATES
METAL_GATES: Set[str] = set()
OVERWORLD_GATES = WOOD_GATES | METAL_GATES
NETHER_GATES = FUNGUS_GATES | METAL_GATES
END_GATES = METAL_GATES
GATES = OVERWORLD_GATES | NETHER_GATES | END_GATES

WOOD_TRAPDOORS = variate(WOOD_TYPES, "trapdoor")
FUNGUS_TRAPDOORS = variate(FUNGUS_TYPES, "trapdoor")
WOODY_TRAPDOORS = WOOD_TRAPDOORS | FUNGUS_TRAPDOORS
METAL_TRAPDOORS = {"minecraft:iron_trapdoor", }
OVERWORLD_TRAPDOORS = WOOD_TRAPDOORS | METAL_TRAPDOORS
NETHER_TRAPDOORS = FUNGUS_TRAPDOORS | METAL_TRAPDOORS
END_TRAPDOORS = METAL_TRAPDOORS
TRAPDOORS = OVERWORLD_TRAPDOORS | NETHER_TRAPDOORS | END_TRAPDOORS

WOOD_ENTRYWAYS = WOOD_DOORS | WOOD_GATES | WOOD_TRAPDOORS
FUNGUS_ENTRYWAYS = FUNGUS_DOORS | FUNGUS_GATES | FUNGUS_TRAPDOORS
WOODY_ENTRYWAYS = WOODY_DOORS | WOODY_GATES | WOODY_TRAPDOORS
METAL_ENTRYWAYS = METAL_DOORS | METAL_GATES | METAL_TRAPDOORS

OVERWORLD_ENTRYWAYS = OVERWORLD_DOORS | OVERWORLD_GATES | OVERWORLD_TRAPDOORS
NETHER_ENTRYWAYS = NETHER_DOORS | NETHER_GATES | NETHER_TRAPDOORS
END_ENTRYWAYS = END_DOORS | END_GATES | END_TRAPDOORS
ENTRYWAYS = OVERWORLD_ENTRYWAYS | NETHER_ENTRYWAYS | END_ENTRYWAYS

# structural
WOOD_PLANKS = variate(WOOD_TYPES, "planks")
FUNGUS_PLANKS = variate(FUNGUS_TYPES, "planks")
PLANKS = WOOD_PLANKS | FUNGUS_PLANKS

POLISHED_IGNEOUS = variate(IGNEOUS_TYPES, "polished", isprefix=True)

STONE_BRICKS = {"minecraft:smooth_stone", } \
    | variate(STONE_BRICK_TYPES, "stone_bricks")
POLISHED_BLACKSTONE_BRICKS = \
    variate(POLISHED_BLACKSTONE_TYPES, "polished_blackstone_bricks")
NETHER_BRICK_BRICKS = variate(NETHER_BRICK_TYPES, "nether_bricks")

OVERWORLD_BRICKS = {"minecraft:bricks", "minecraft:prismarine_bricks"} \
    | STONE_BRICKS
NETHER_DIMENSION_BRICKS = POLISHED_BLACKSTONE_BRICKS | NETHER_BRICK_BRICKS
END_BRICKS = {"minecraft:end_stone_bricks", }
BRICKS = OVERWORLD_BRICKS | NETHER_DIMENSION_BRICKS | END_BRICKS

CONCRETES = variate(DYE_COLORS, "concrete")
CONCRETE_POWDERS = variate(DYE_COLORS, "concrete_powder")

REGULAR_SANDSTONES = variate(SANDSTONE_TYPES, "sandstone")
RED_SANDSTONES = variate(SANDSTONE_TYPES, "red_sandstone")
SANDSTONES = REGULAR_SANDSTONES | RED_SANDSTONES

PRISMARINES = {"minecraft:prismarine_bricks", } \
    | variate(PRISMARINE_TYPES, "prismarine")

POLISHED_BLACKSTONES = {"minecraft:polished_blackstone",
                        "minecraft_chiseled_polished_blackstone"} \
    | POLISHED_BLACKSTONE_BRICKS
QUARTZES = variate("minecraft:smooth_quartz", "minecraft_chiseled quartz",
                   "minecraft:quartz_block", "minecraft_quartz_brick",
                   "minecraft:quartz_pillar")
PURPURS = variate(PURPUR_TYPES, "purpur", isprefix=True)

OVERWORLD_STRUCTURE_BLOCKS = {"minecraft:hay_bale", "minecraft:bookshelf",
                              "minecraft:chain", "minecraft:iron bars", } \
    | WOOD_PLANKS | SANDSTONES | OVERWORLD_BRICKS \
    | CONCRETES | CONCRETE_POWDERS | PRISMARINES
NETHER_STRUCTURE_BLOCKS = FUNGUS_PLANKS | NETHER_DIMENSION_BRICKS \
    | POLISHED_BLACKSTONES | QUARTZES
END_STRUCTURE_BLOCKS = PURPURS
STRUCTURE_BLOCKS = OVERWORLD_STRUCTURE_BLOCKS | NETHER_STRUCTURE_BLOCKS \
    | END_STRUCTURE_BLOCKS

# lights
TORCHES = variate(FIRE_TYPES, "torch")
LANTERNS = variate(FIRE_TYPES, "lantern")
BLOCK_LIGHTS = {"minecraft:glowstone", "minecraft:jack_o_lantern",
                "minecraft:sea_lantern", }
LIGHTS = {"minecraft:end_rod"} | TORCHES | LANTERNS | BLOCK_LIGHTS


# interactable
WOOD_FLOOR_SIGNS = variate(WOOD_TYPES, "sign")
FUNGUS_FLOOR_SIGNS = variate(FUNGUS_TYPES, "sign")
WOODY_FLOOR_SIGNS = WOOD_FLOOR_SIGNS | FUNGUS_FLOOR_SIGNS
FLOOR_SIGNS = WOODY_FLOOR_SIGNS
WOOD_WALL_SIGNS = variate(WOOD_TYPES, "wall_sign")
FUNGUS_WALL_SIGNS = variate(FUNGUS_TYPES, "wall_sign")
WOODY_WALL_SIGNS = WOOD_WALL_SIGNS | FUNGUS_WALL_SIGNS
WALL_SIGNS = WOODY_WALL_SIGNS
WOOD_SIGNS = WOOD_FLOOR_SIGNS | WOOD_WALL_SIGNS
FUNGUS_SIGNS = FUNGUS_FLOOR_SIGNS | FUNGUS_WALL_SIGNS
SIGNS = FLOOR_SIGNS | WALL_SIGNS

CAULDRONS = variate(CAULDRON_TYPES, "cauldron")
FURNACES = {"minecraft:blast_furnace", "minecraft:furnace",
            "minecraft:smoker", }
ANVILS = variate(ANVIL_TYPES, "anvil")
JOB_SITE_BLOCKS = {"minecraft:barrel", "minecraft:blast_furnace",
                   "minecraft:brewing_stand", "minecraft:cartography_table",
                   "minecraft:composter",
                   "minecraft:fletching_table", "minecraft:grindstone",
                   "minecraft:lectern", "minecraft:loom",
                   "minecraft:smithing_table", "minecraft:stonecutter", } \
    | CAULDRONS

SHULKER_BOXES = variate({None, } | set(DYE_COLORS), "shulker_box")
CHESTS = variate(CHEST_TYPES, "chest")
UI_BLOCKS = {"minecraft:beacon",
             "minecraft:crafting_bench", "minecraft:enchanting_table", } \
    | SIGNS | FURNACES | ANVILS | JOB_SITE_BLOCKS | CHESTS | SHULKER_BOXES

BANNERS = variate(DYE_COLORS, "banner")
BEDS = variate(DYE_COLORS, "beds")
CAMPFIRES = variate(FIRE_TYPES, "campfire")

OVERWORLD_PORTALS: Set[str] = set()
OVERWORLD_PORTAL_BLOCKS = OVERWORLD_PORTALS
NETHER_PORTALS = {"minecraft:nether_portal", }
NETHER_PORTAL_BLOCKS = NETHER_PORTALS | OBSIDIANS
END_PORTALS = {"minecraft:end_gateway", "minecraft:end_portal", }
END_PORTAL_BLOCKS = {"minecraft:end_portal_block", "minecraft:bedrock"} \
    | END_PORTALS
PORTALS = OVERWORLD_PORTALS | NETHER_PORTALS | END_PORTALS
PORTAL_BLOCKS = OVERWORLD_PORTAL_BLOCKS | NETHER_PORTAL_BLOCKS \
    | END_PORTAL_BLOCKS

SPONGES = variate(SPONGE_TYPES, "sponge")

WOOD_BUTTONS = variate(WOOD_TYPES, "button")
FUNGUS_BUTTONS = variate(FUNGUS_TYPES, "button")
WOODY_BUTTONS = WOOD_BUTTONS | FUNGUS_BUTTONS
BUTTONS = {"minecraft:stone_button"} | WOODY_BUTTONS
SWITCHES = {"minecraft:lever"} | BUTTONS

# interaction has an immediate effect (no UI)
USABLE_BLOCKS = {"minecraft:bell", "minecraft:cake", "minecraft:conduit",
                 "minecraft:flower_pot", "minecraft:jukebox",
                 "minecraft:lodestone", "minecraft:respawn_anchor",
                 "minecraft:spawner", "minecraft:tnt"} \
    | BEE_NESTS | CAMPFIRES | CAULDRONS | SWITCHES

INTERACTABLE_BLOCKS = USABLE_BLOCKS | UI_BLOCKS

SENSOR_RAILS = variate(SENSOR_RAIL_TYPES, "rail")
ACTUATOR_RAILS = variate(ACTUATOR_RAIL_TYPES, "rail")
RAILS = {"minecraft:rail", } | SENSOR_RAILS | ACTUATOR_RAILS

WOOD_PRESSURE_PLATES = variate(WOOD_TYPES, "pressure_plate")
FUNGUS_PRESSURE_PLATES = variate(FUNGUS_TYPES, "pressure_plate")
WOODY_PRESSURE_PLATES = WOOD_PRESSURE_PLATES | FUNGUS_PRESSURE_PLATES
STONE_PRESSURE_PLATES = {"minecraft:stone_pressure_plate",
                         "minecraft:polished_blackstone_pressure_plate"}
WEIGHTED_PRESSURE_PLATES = variate(WEIGHTED_PRESSURE_PLATE_TYPES,
                                   "weighted_pressure_plate")
PRESSURE_PLATES = WOODY_PRESSURE_PLATES | STONE_PRESSURE_PLATES \
    | WEIGHTED_PRESSURE_PLATES

SENSORS = {"minecraft:daylight_sensor", "minecraft:target", "minecraft:"} \
    | SENSOR_RAILS | SWITCHES | PRESSURE_PLATES

PISTON_BODIES = variate(PISTON_TYPES, "piston")
PISTONS = {"minecraft:piston_head", "minecraft:moving_piston", } \
    | PISTON_BODIES

COMMAND_BLOCKS = variate(COMMAND_BLOCK_TYPES, "command_block")
COMMAND_ONLY_ACTUATORS = {"minecraft:structure_block", } | COMMAND_BLOCKS
ACTUATORS = {"minecraft:bell", "minecraft:dispenser", "minecraft:dragon_head",
             "minecraft:dropper", "minecraft:hopper", "minecraft:note_block",
             "minecraft:tnt", "minecraft:trapped_chest",
             "minecraft:tripwire_hook"} \
    | PISTONS | ENTRYWAYS | ACTUATOR_RAILS | COMMAND_ONLY_ACTUATORS
WIRING = {"minecraft:redstone_wire", "minecraft:redstone_torch",
          "minecraft:repeater", "minecraft:comparator"}
REDSTONE = SENSORS | ACTUATORS | WIRING

SLIMELIKES = {"minecraft:slime_block", "minecraft:honey_block", }

FLOOR_HEADS = variate(HEAD_TYPES,  "head")
WALL_HEADS = variate(HEAD_TYPES, "wall_head")
HEADS = FLOOR_HEADS | WALL_HEADS

CREATIVE_ONLY = {"minecraft:player_head", "minecraft:player_wall_head",
                 "minecraft:petrified_oak_slab", }
COMMANDS_ONLY = {"minecraft:barrier", "minecraft:"}

FALLING_BLOCKS = {"minecraft:dragon_egg", }\
    | ANVILS | CONCRETE_POWDERS | GRANULARS

WOOD_BLOCKS = TRUNKS | WOOD_BUTTONS | WOOD_ENTRYWAYS | WOOD_FENCES \
    | WOOD_PLANKS | WOOD_PRESSURE_PLATES | WOOD_SLABS | WOOD_STAIRS \
    | WOOD_SIGNS
FUNGUS_BLOCKS = FUNGUS_GROWTH_BLOCKS | FUNGUS_BUTTONS | FUNGUS_ENTRYWAYS \
    | FUNGUS_FENCES | FUNGUS_PLANKS | FUNGUS_PRESSURE_PLATES | FUNGUS_SLABS \
    | FUNGUS_STAIRS | FUNGUS_SIGNS
WOODY_BLOCKS = WOOD_BLOCKS | FUNGUS_BLOCKS

LAVA_FLAMMABLE = {"minecraft:composter", "minecraft:tnt",
                  "minecraft:bookshelf", "minecraft:lectern",
                  "minecraft:dead_bush"} \
    | WOOD_BLOCKS | BEE_NESTS | FOLIAGE | WOOLS | CARPETS | BAMBOOS \
    | TALL_FLOWERS | TRUE_GRASSES - {"minecraft:grass_block"}
FLAMMABLE = {"minecraft:coal_block", "minecraft:target",
             "minecraft:dried_kelp_block", "minecraft:hay_bale",
             "minecraft:scaffolding", "minecraft:"} \
    | LAVA_FLAMMABLE

BLOCKS = ORES | MINERAL_BLOCKS | SOILS | STONES | FLUIDS | LIQUID_BASED \
    | FIRES | LIFE | GLASS | SLABS | STAIRS | BARRIERS | ENTRYWAYS \
    | STRUCTURE_BLOCKS | LIGHTS | INTERACTABLE_BLOCKS | REDSTONE | SLIMELIKES \
    | HEADS | CREATIVE_ONLY | COMMANDS_ONLY

INVENTORY_BLOCKS = {"minecraft:barrel",
                    "minecraft:hopper", } | CHESTS | SHULKER_BOXES

CLIMBABLE = {"minecraft:ladder", "minecraft:scaffolding", } | VINES

# ================================================= grouped by obtrusiveness

INVISIBLE = AIRS | {"minecraft:barrier", "minecraft:structure_void"}

# filter skylight
FILTERING = {"minecraft:bubble_column",
             "minecraft:ice", "minecraft:frosted_ice",
             "minecraft:cobweb",
             "minecraft:slime_block", "minecraft:honey_block",
             "minecraft:spawner", "minecraft:beacon",
             "minecraft:end_gateway",
             "minecraft:chorus_plant", "minecraft:chorus_flower", } \
    | WATERS | LAVAS | LEAVES | SHULKER_BOXES

# can be seen through easily
UNOBTRUSIVE = {"minecraft:ladder", "minecraft:tripwire", "minecraft:end_rod",
               "minecraft:nether_portal", "minecraft:iron_bars",
               "minecraft:chain", "minecraft:conduit", "minecraft:lily_pad",
               "minecraft:scaffolding", "minecraft:snow", } \
    | GLASS | RAILS | WIRING | SWITCHES | TORCHES | SIGNS

# can be seen through moderately
OBTRUSIVE = {"minecraft:bell", "minecraft:brewing_stand", "minecraft:cake",
             "minecraft:flower_pot", "minecraft:lectern", } \
    | ANVILS | HEADS | PLANTS | BEDS | FENCES | GATES | SLABS | EGGS \
    | CAMPFIRES

TRANSPARENT = INVISIBLE | FILTERING | UNOBTRUSIVE | OBTRUSIVE

# all esle is considered opaque

# ========================================================= map colouring
# block visualization
# based on https://minecraft.gamepedia.com/Map_item_format#Base_colors
# liberty was taken to move stained glass panes and various flowers
# into the appropriate colour category

MAPTRANSPARENT = {"minecraft:redstone_lamp", "minecraft:cake",
                  "minecraft:ladder", "minecraft:tripwire",
                  "minecraft:flower_pot", "minecraft:end_rod",
                  "minecraft:glass", "minecraft:glass_pane",
                  "minecraft:nether_portal", "minecraft:iron_bars",
                  "minecraft:chain", } \
    | INVISIBLE | WIRING | RAILS | SWITCHES | HEADS | TORCHES

# base map colours
# WARNING: all non-transparent blocks are listed individually here again
PALETTE = {
    0x7FB238: ("minecraft:grass_block", "minecraft:slime_block"),
    0xF7E9A3: (
        "minecraft:sand",
        "minecraft:birch_planks",
        "minecraft:stripped_birch_log",
        "minecraft:birch_wood",
        "minecraft:stripped_birch_wood",
        "minecraft:birch_sign",
        "minecraft:birch_wall_sign",
        "minecraft:birch_pressure_plate",
        "minecraft:birch_trapdoor",
        "minecraft:birch_stairs",
        "minecraft:birch_slab",
        "minecraft:birch_fence_gate",
        "minecraft:birch_fence",
        "minecraft:birch_door",
        "minecraft:sandstone",
        "minecraft:sandstone_slab",
        "minecraft:sandstone_stairs",
        "minecraft:sandstone_wall",
        "minecraft:cut_sandstone",
        "minecraft:cut_sandstone_slab",
        "minecraft:smooth_sandstone",
        "minecraft:smooth_sandstone_slab",
        "minecraft:smooth_sandstone_stairs",
        "minecraft:chiseled_sandstone",
        "minecraft:glowstone",
        "minecraft:end_stone",
        "minecraft:end_stone_bricks",
        "minecraft:end_stone_brick_slab",
        "minecraft:end_stone_brick_stairs",
        "minecraft:end_stone_brick_wall",
        "minecraft:bone_block",
        "minecraft:turtle_egg",
        "minecraft:scaffolding",
    ),
    0xC7C7C7: ("minecraft:cobweb", "minecraft:mushroom_stem"),
    0xFF0000: (
        "minecraft:lava",
        "minecraft:tnt",
        "minecraft:fire",
        "minecraft:redstone_block",
    ),
    0xA0A0FF: (
        "minecraft:ice",
        "minecraft:frosted_ice",
        "minecraft:packed_ice",
        "minecraft:blue_ice",
    ),
    0xA7A7A7: (
        "minecraft:iron_block",
        "minecraft:iron_door",
        "minecraft:brewing_stand",
        "minecraft:heavy_weighted_pressure_plate",
        "minecraft:iron_trapdoor",
        "minecraft:lantern",
        "minecraft:anvil",
        "minecraft:chipped_anvil",
        "minecraft:damaged_anvil",
        "minecraft:grindstone",
        "minecraft:soul_lantern",
        "minecraft:lodestone",
    ),
    0x007C00: (
        "minecraft:oak_sapling",
        "minecraft:spruce_sapling",
        "minecraft:birch_sapling",
        "minecraft:jungle_sapling",
        "minecraft:acacia_sapling",
        "minecraft:dark_oak_sapling",
        "minecraft:wheat",
        "minecraft:sugar_cane",
        "minecraft:pumpkin_stem",
        "minecraft:melon_stem",
        "minecraft:lily_pad",
        "minecraft:cocoa",
        "minecraft:carrots",
        "minecraft:potatoes",
        "minecraft:beetroots",
        "minecraft:sweet_berry_bush",
        "minecraft:grass",
        "minecraft:tall_grass",
        "minecraft:fern",
        "minecraft:large_fern",
        "minecraft:vine",
        "minecraft:oak_leaves",
        "minecraft:spruce_leaves",
        "minecraft:birch_leaves",
        "minecraft:jungle_leaves",
        "minecraft:acacia_leaves",
        "minecraft:dark_oak_leaves",
        "minecraft:cactus",
        "minecraft:bamboo",
    ),
    0xFFFFFF: (
        "minecraft:snow",
        "minecraft:snow_block",
        "minecraft:white_bed",
        "minecraft:white_wool",
        "minecraft:white_stained_glass",
        "minecraft:white_stained_glass_pane",
        "minecraft:white_carpet",
        "minecraft:white_banner",
        "minecraft:white_shulker_box",
        "minecraft:white_glazed_terracotta",
        "minecraft:white_concrete",
        "minecraft:white_concrete_powder",
        "minecraft:lily_of_the_valley",
    ),
    0xA4A8B8: (
        "minecraft:clay",
        "minecraft:infested_stone",
        "minecraft:infested_cobblestone",
        "minecraft:infested_stone_bricks",
        "minecraft:infested_cracked_stone_bricks",
        "minecraft:infested_mossy_stone_bricks",
        "minecraft:infested_chiseled_stone_bricks",
    ),
    0x976D4D: (
        "minecraft:dirt",
        "minecraft:coarse_dirt",
        "minecraft:farmland",
        "minecraft:grass_path",
        "minecraft:granite",
        "minecraft:granite_slab",
        "minecraft:granite_stairs",
        "minecraft:granite_wall",
        "minecraft:polished_granite",
        "minecraft:polished_granite_slab",
        "minecraft:polished_granite_stairs",
        "minecraft:jungle_planks",
        "minecraft:jungle_log",
        "minecraft:stripped_jungle_log",
        "minecraft:jungle_wood",
        "minecraft:stripped_jungle_wood",
        "minecraft:jungle_sign",
        "minecraft:jungle_wall_sign",
        "minecraft:jungle_pressure_plate",
        "minecraft:jungle_trapdoor",
        "minecraft:jungle_stairs",
        "minecraft:jungle_slab",
        "minecraft:jungle_fence_gate",
        "minecraft:jungle_fence",
        "minecraft:jungle_door",
        "minecraft:jukebox",
        "minecraft:brown_mushroom_block",
    ),
    0x707070: (
        "minecraft:stone",
        "minecraft:stone_slab",
        "minecraft:andesite",
        "minecraft:andesite_slab",
        "minecraft:andesite_stairs",
        "minecraft:andesite_wall",
        "minecraft:polished_andesite",
        "minecraft:polished_andesite_slab",
        "minecraft:polished_andesite_stairs",
        "minecraft:cobblestone",
        "minecraft:cobblestone_slab",
        "minecraft:cobblestone_stairs",
        "minecraft:cobblestone_wall",
        "minecraft:bedrock",
        "minecraft:gold_ore",
        "minecraft:iron_ore",
        "minecraft:coal_ore",
        "minecraft:lapis_ore",
        "minecraft:diamond_ore",
        "minecraft:dispenser",
        "minecraft:dropper",
        "minecraft:mossy_cobblestone",
        "minecraft:mossy_cobblestone_slab",
        "minecraft:mossy_cobblestone_stairs",
        "minecraft:mossy_cobblestone_wall",
        "minecraft:spawner",
        "minecraft:furnace",
        "minecraft:stone_pressure_plate",
        "minecraft:redstone_ore",
        "minecraft:stone_bricks",
        "minecraft:stone_brick_slab",
        "minecraft:stone_brick_stairs",
        "minecraft:stone_brick_wall",
        "minecraft:mossy_stone_bricks",
        "minecraft:mossy_stone_brick_slab",
        "minecraft:mossy_stone_brick_stairs",
        "minecraft:mossy_stone_brick_wall",
        "minecraft:cracked_stone_bricks",
        "minecraft:chiseled_stone_bricks",
        "minecraft:emerald_ore",
        "minecraft:ender_chest",
        "minecraft:smooth_stone",
        "minecraft:smooth_stone_slab",
        "minecraft:observer",
        "minecraft:smoker",
        "minecraft:blast_furnace",
        "minecraft:stonecutter",
        "minecraft:sticky_piston",
        "minecraft:piston",
        "minecraft:piston_head",
        "minecraft:gravel",
        "minecraft:acacia_log",
        "minecraft:cauldron",
        "minecraft:hopper",
    ),
    0x4040FF: (
        "minecraft:kelp",
        "minecraft:seagrass",
        "minecraft:tall_seagrass",
        "minecraft:water",
        "minecraft:bubble_column",
    ),
    0x8F7748: (
        "minecraft:oak_planks",
        "minecraft:oak_log",
        "minecraft:stripped_oak_log",
        "minecraft:oak_wood",
        "minecraft:stripped_oak_wood",
        "minecraft:oak_sign",
        "minecraft:oak_wall_sign",
        "minecraft:oak_pressure_plate",
        "minecraft:oak_trapdoor",
        "minecraft:oak_stairs",
        "minecraft:oak_slab",
        "minecraft:oak_fence_gate",
        "minecraft:oak_fence",
        "minecraft:oak_door",
        "minecraft:note_block",
        "minecraft:bookshelf",
        "minecraft:chest",
        "minecraft:trapped_chest",
        "minecraft:crafting_table",
        "minecraft:daylight_detector",
        "minecraft:loom",
        "minecraft:barrel",
        "minecraft:cartography_table",
        "minecraft:fletching_table",
        "minecraft:lectern",
        "minecraft:smithing_table",
        "minecraft:composter",
        "minecraft:bamboo_sapling",
        "minecraft:dead_bush",
        "minecraft:petrified_oak_slab",
        "minecraft:beehive",
    ),
    0xFFFCF5: (
        "minecraft:diorite",
        "minecraft:diorite_slab",
        "minecraft:diorite_stairs",
        "minecraft:diorite_wall",
        "minecraft:polished_diorite",
        "minecraft:polished_diorite_slab",
        "minecraft:polished_diorite_stairs",
        "minecraft:birch_log",
        "minecraft:quartz_block",
        "minecraft:quartz_slab",
        "minecraft:quartz_stairs",
        "minecraft:smooth_quartz",
        "minecraft:smooth_quartz_slab",
        "minecraft:smooth_quartz_stairs",
        "minecraft:chiseled_quartz_block",
        "minecraft:quartz_pillar",
        "minecraft:quartz_bricks",
        "minecraft:sea_lantern",
        "minecraft:target",
    ),
    0xD87F33: (
        "minecraft:acacia_planks",
        "minecraft:stripped_acacia_log",
        "minecraft:stripped_acacia_wood",
        "minecraft:acacia_sign",
        "minecraft:acacia_wall_sign",
        "minecraft:acacia_pressure_plate",
        "minecraft:acacia_trapdoor",
        "minecraft:acacia_stairs",
        "minecraft:acacia_slab",
        "minecraft:acacia_fence_gate",
        "minecraft:acacia_fence",
        "minecraft:acacia_door",
        "minecraft:red_sand",
        "minecraft:orange_wool",
        "minecraft:orange_carpet",
        "minecraft:orange_shulker_box",
        "minecraft:orange_bed",
        "minecraft:orange_stained_glass",
        "minecraft:orange_stained_glass_pane",
        "minecraft:orange_banner",
        "minecraft:orange_glazed_terracotta",
        "minecraft:orange_concrete",
        "minecraft:orange_concrete_powder",
        "minecraft:pumpkin",
        "minecraft:carved_pumpkin",
        "minecraft:jack_o_lantern",
        "minecraft:terracotta",
        "minecraft:red_sandstone",
        "minecraft:red_sandstone_slab",
        "minecraft:red_sandstone_stairs",
        "minecraft:red_sandstone_wall",
        "minecraft:cut_red_sandstone",
        "minecraft:cut_red_sandstone_slab",
        "minecraft:smooth_red_sandstone",
        "minecraft:smooth_red_sandstone_slab",
        "minecraft:smooth_red_sandstone_stairs",
        "minecraft:chiseled_red_sandstone",
        "minecraft:honey_block",
        "minecraft:honeycomb_block",
        "minecraft:orange_tulip",
    ),
    0xB24CD8: (
        "minecraft:magenta_wool",
        "minecraft:magenta_carpet",
        "minecraft:magenta_shulker_box",
        "minecraft:magenta_bed",
        "minecraft:magenta_stained_glass",
        "minecraft:magenta_stained_glass_pane",
        "minecraft:magenta_banner",
        "minecraft:magenta_glazed_terracotta",
        "minecraft:magenta_concrete",
        "minecraft:magenta_concrete_powder",
        "minecraft:purpur_block",
        "minecraft:purpur_slab",
        "minecraft:purpur_stairs",
        "minecraft:purpur_pillar",
        "minecraft:allium",
        "minecraft:lilac",
    ),
    0x6699D8: (
        "minecraft:light_blue_wool",
        "minecraft:light_blue_carpet",
        "minecraft:light_blue_shulker_box",
        "minecraft:light_blue_bed",
        "minecraft:light_blue_stained_glass",
        "minecraft:light_blue_stained_glass_pane",
        "minecraft:light_blue_banner",
        "minecraft:light_blue_glazed_terracotta",
        "minecraft:light_blue_concrete",
        "minecraft:light_blue_concrete_powder",
        "minecraft:soul_fire",
        "minecraft:blue_orchid",
    ),
    0xE5E533: (
        "minecraft:sponge",
        "minecraft:wet_sponge",
        "minecraft:yellow_wool",
        "minecraft:yellow_carpet",
        "minecraft:yellow_shulker_box",
        "minecraft:yellow_bed",
        "minecraft:yellow_stained_glass",
        "minecraft:yellow_stained_glass_pane",
        "minecraft:yellow_banner",
        "minecraft:yellow_glazed_terracotta",
        "minecraft:yellow_concrete",
        "minecraft:yellow_concrete_powder",
        "minecraft:hay_block",
        "minecraft:horn_coral_block",
        "minecraft:horn_coral",
        "minecraft:horn_coral_fan",
        "minecraft:bee_nest",
        "minecraft:dandelion",
        "minecraft:sunflower",
    ),
    0x7FCC19: (
        "minecraft:lime_wool",
        "minecraft:lime_carpet",
        "minecraft:lime_shulker_box",
        "minecraft:lime_bed",
        "minecraft:lime_stained_glass",
        "minecraft:lime_stained_glass_pane",
        "minecraft:lime_banner",
        "minecraft:lime_glazed_terracotta",
        "minecraft:lime_concrete",
        "minecraft:lime_concrete_powder",
        "minecraft:melon",
    ),
    0xF27FA5: (
        "minecraft:pink_wool",
        "minecraft:pink_carpet",
        "minecraft:pink_shulker_box",
        "minecraft:pink_bed",
        "minecraft:pink_stained_glass",
        "minecraft:pink_stained_glass_pane",
        "minecraft:pink_banner",
        "minecraft:pink_glazed_terracotta",
        "minecraft:pink_concrete",
        "minecraft:pink_concrete_powder",
        "minecraft:brain_coral_block",
        "minecraft:brain_coral",
        "minecraft:brain_coral_fan",
        "minecraft:pink_tulip",
        "minecraft:peony",
    ),
    0x4C4C4C: (
        "minecraft:acacia_wood",
        "minecraft:gray_wool",
        "minecraft:gray_carpet",
        "minecraft:gray_shulker_box",
        "minecraft:gray_bed",
        "minecraft:gray_stained_glass",
        "minecraft:gray_stained_glass_pane",
        "minecraft:gray_banner",
        "minecraft:gray_glazed_terracotta",
        "minecraft:gray_concrete",
        "minecraft:gray_concrete_powder",
        "minecraft:dead_tube_coral_block",
        "minecraft:dead_tube_coral",
        "minecraft:dead_tube_coral_fan",
        "minecraft:dead_brain_coral_block",
        "minecraft:dead_brain_coral",
        "minecraft:dead_brain_coral_fan",
        "minecraft:dead_bubble_coral_block",
        "minecraft:dead_bubble_coral",
        "minecraft:dead_bubble_coral_fan",
        "minecraft:dead_fire_coral_block",
        "minecraft:dead_fire_coral",
        "minecraft:dead_fire_coral_fan",
        "minecraft:dead_horn_coral_block",
        "minecraft:dead_horn_coral",
        "minecraft:dead_horn_coral_fan",
    ),
    0x999999: (
        "minecraft:light_gray_wool",
        "minecraft:light_gray_carpet",
        "minecraft:light_gray_shulker_box",
        "minecraft:light_gray_bed",
        "minecraft:light_gray_stained_glass",
        "minecraft:light_gray_stained_glass_pane",
        "minecraft:light_gray_banner",
        "minecraft:light_gray_glazed_terracotta",
        "minecraft:light_gray_concrete",
        "minecraft:light_gray_concrete_powder",
        "minecraft:structure_block",
        "minecraft:jigsaw",
        "minecraft:azure_bluet",
        "minecraft:oxeye_daisy",
        "minecraft:white_tulip",
    ),
    0x4C7F99: (
        "minecraft:cyan_wool",
        "minecraft:cyan_carpet",
        "minecraft:cyan_shulker_box",
        "minecraft:cyan_bed",
        "minecraft:cyan_stained_glass",
        "minecraft:cyan_stained_glass_pane",
        "minecraft:cyan_banner",
        "minecraft:cyan_glazed_terracotta",
        "minecraft:cyan_concrete",
        "minecraft:cyan_concrete_powder",
        "minecraft:prismarine_slab",
        "minecraft:prismarine_stairs",
        "minecraft:prismarine_wall",
        "minecraft:warped_roots",
        "minecraft:warped_door",
        "minecraft:warped_fungus",
        "minecraft:twisting_vines",
        "minecraft:nether_sprouts",
    ),
    0x7F3FB2: (
        "minecraft:shulker_box",
        "minecraft:purple_wool",
        "minecraft:purple_carpet",
        "minecraft:purple_bed",
        "minecraft:purple_stained_glass",
        "minecraft:purple_stained_glass_pane",
        "minecraft:purple_banner",
        "minecraft:purple_glazed_terracotta",
        "minecraft:purple_concrete",
        "minecraft:purple_concrete_powder",
        "minecraft:mycelium",
        "minecraft:chorus_plant",
        "minecraft:chorus_flower",
        "minecraft:repeating_command_block",
        "minecraft:bubble_coral_block",
        "minecraft:bubble_coral",
        "minecraft:bubble_coral_fan",
    ),
    0x334CB2: (
        "minecraft:blue_wool",
        "minecraft:blue_carpet",
        "minecraft:blue_shulker_box",
        "minecraft:blue_bed",
        "minecraft:blue_stained_glass",
        "minecraft:blue_stained_glass_pane",
        "minecraft:blue_banner",
        "minecraft:blue_glazed_terracotta",
        "minecraft:blue_concrete",
        "minecraft:blue_concrete_powder",
        "minecraft:tube_coral_block",
        "minecraft:tube_coral",
        "minecraft:tube_coral_fan",
        "minecraft:cornflower",
    ),
    0x664C33: (
        "minecraft:dark_oak_planks",
        "minecraft:dark_oak_log",
        "minecraft:stripped_dark_oak_log",
        "minecraft:dark_oak_wood",
        "minecraft:stripped_dark_oak_wood",
        "minecraft:dark_oak_sign",
        "minecraft:dark_oak_wall_sign",
        "minecraft:dark_oak_pressure_plate",
        "minecraft:dark_oak_trapdoor",
        "minecraft:dark_oak_stairs",
        "minecraft:dark_oak_slab",
        "minecraft:dark_oak_fence_gate",
        "minecraft:dark_oak_fence",
        "minecraft:dark_oak_door",
        "minecraft:spruce_log",
        "minecraft:brown_wool",
        "minecraft:brown_carpet",
        "minecraft:brown_shulker_box",
        "minecraft:brown_bed",
        "minecraft:brown_stained_glass",
        "minecraft:brown_stained_glass_pane",
        "minecraft:brown_banner",
        "minecraft:brown_glazed_terracotta",
        "minecraft:brown_concrete",
        "minecraft:brown_concrete_powder",
        "minecraft:soul_sand",
        "minecraft:command_block",
        "minecraft:brown_mushroom",
        "minecraft:soul_soil",
    ),
    0x667F33: (
        "minecraft:green_wool",
        "minecraft:green_carpet",
        "minecraft:green_shulker_box",
        "minecraft:green_bed",
        "minecraft:green_stained_glass",
        "minecraft:green_stained_glass_pane",
        "minecraft:green_banner",
        "minecraft:green_glazed_terracotta",
        "minecraft:green_concrete",
        "minecraft:green_concrete_powder",
        "minecraft:end_portal_frame",
        "minecraft:chain_command_block",
        "minecraft:dried_kelp_block",
        "minecraft:sea_pickle",
    ),
    0x993333: (
        "minecraft:red_wool",
        "minecraft:red_carpet",
        "minecraft:red_shulker_box",
        "minecraft:red_bed",
        "minecraft:red_stained_glass",
        "minecraft:red_stained_glass_pane",
        "minecraft:red_banner",
        "minecraft:red_glazed_terracotta",
        "minecraft:red_concrete",
        "minecraft:red_concrete_powder",
        "minecraft:bricks",
        "minecraft:brick_slab",
        "minecraft:brick_stairs",
        "minecraft:brick_wall",
        "minecraft:red_mushroom_block",
        "minecraft:nether_wart",
        "minecraft:enchanting_table",
        "minecraft:nether_wart_block",
        "minecraft:fire_coral_block",
        "minecraft:fire_coral",
        "minecraft:fire_coral_fan",
        "minecraft:red_mushroom",
        "minecraft:shroomlight",
        "minecraft:poppy",
        "minecraft:red_tulip",
        "minecraft:rose_bush",
    ),
    0x191919: (
        "minecraft:black_wool",
        "minecraft:black_carpet",
        "minecraft:black_shulker_box",
        "minecraft:black_bed",
        "minecraft:black_stained_glass",
        "minecraft:black_stained_glass_pane",
        "minecraft:black_banner",
        "minecraft:black_glazed_terracotta",
        "minecraft:black_concrete",
        "minecraft:black_concrete_powder",
        "minecraft:obsidian",
        "minecraft:end_portal",
        "minecraft:dragon_egg",
        "minecraft:coal_block",
        "minecraft:end_gateway",
        "minecraft:basalt",
        "minecraft:polished_basalt",
        "minecraft:netherite_block",
        "minecraft:ancient_debris",
        "minecraft:crying_obsidian",
        "minecraft:respawn_anchor",
        "minecraft:blackstone",
        "minecraft:blackstone_slab",
        "minecraft:blackstone_stairs",
        "minecraft:blackstone_wall",
        "minecraft:polished_blackstone",
        "minecraft:polished_blackstone_slab",
        "minecraft:polished_blackstone_stairs",
        "minecraft:polished_blackstone_wall",
        "minecraft:polished_blackstone_bricks",
        "minecraft:polished_blackstone_brick_slab",
        "minecraft:polished_blackstone_brick_stairs",
        "minecraft:polished_blackstone_brick_wall",
        "minecraft:gilded_blackstone",
        "minecraft:wither_rose",
    ),
    0xFAEE4D: (
        "minecraft:gold_block",
        "minecraft:light_weighted_pressure_plate",
        "minecraft:bell",
    ),
    0x5CDBD5: (
        "minecraft:diamond_block",
        "minecraft:beacon",
        "minecraft:prismarine_bricks",
        "minecraft:prismarine_brick_slab",
        "minecraft:prismarine_brick_stairs",
        "minecraft:dark_prismarine",
        "minecraft:dark_prismarine_slab",
        "minecraft:dark_prismarine_stairs",
        "minecraft:conduit",
    ),
    0x4A80FF: ("minecraft:lapis_block",),
    0x00D93A: ("minecraft:emerald_block",),
    0x815631: (
        "minecraft:podzol",
        "minecraft:spruce_planks",
        "minecraft:stripped_spruce_log",
        "minecraft:spruce_wood",
        "minecraft:stripped_spruce_wood",
        "minecraft:spruce_sign",
        "minecraft:spruce_wall_sign",
        "minecraft:spruce_pressure_plate",
        "minecraft:spruce_trapdoor",
        "minecraft:spruce_stairs",
        "minecraft:spruce_slab",
        "minecraft:spruce_fence_gate",
        "minecraft:spruce_fence",
        "minecraft:spruce_door",
        "minecraft:campfire",
        "minecraft:soul_campfire",
    ),
    0x700200: (
        "minecraft:netherrack",
        "minecraft:nether_bricks",
        "minecraft:nether_brick_fence",
        "minecraft:nether_brick_slab",
        "minecraft:nether_brick_stairs",
        "minecraft:nether_brick_wall",
        "minecraft:cracked_nether_bricks",
        "minecraft:chiseled_nether_bricks",
        "minecraft:nether_gold_ore",
        "minecraft:nether_quartz_ore",
        "minecraft:magma_block",
        "minecraft:red_nether_bricks",
        "minecraft:red_nether_brick_slab",
        "minecraft:red_nether_brick_stairs",
        "minecraft:red_nether_brick_wall",
        "minecraft:crimson_roots",
        "minecraft:crimson_door",
        "minecraft:crimson_fungus",
        "minecraft:weeping_vines",
    ),
    0xD1B1A1: ("minecraft:white_terracotta",),
    0x9F5224: ("minecraft:orange_terracotta",),
    0x95576C: ("minecraft:magenta_terracotta",),
    0x706C8A: ("minecraft:light_blue_terracotta",),
    0xBA8524: ("minecraft:yellow_terracotta",),
    0x677535: ("minecraft:lime_terracotta",),
    0xA04D4E: ("minecraft:pink_terracotta",),
    0x392923: ("minecraft:gray_terracotta",),
    0x876B62: ("minecraft:light_gray_terracotta",),
    0x575C5C: ("minecraft:cyan_terracotta",),
    0x7A4958: ("minecraft:purple_terracotta", "minecraft:purple_shulker_box"),
    0x4C3E5C: ("minecraft:blue_terracotta",),
    0x4C3223: ("minecraft:brown_terracotta",),
    0x4C522A: ("minecraft:green_terracotta",),
    0x8E3C2E: ("minecraft:red_terracotta",),
    0x251610: ("minecraft:black_terracotta",),
    0xBD3031: ("minecraft:crimson_nylium",),
    0x943F61: (
        "minecraft:crimson_fence",
        "minecraft:crimson_fence_gate",
        "minecraft:crimson_planks",
        "minecraft:crimson_pressure_plate",
        "minecraft:crimson_sign",
        "minecraft:crimson_wall_sign",
        "minecraft:crimson_slab",
        "minecraft:crimson_stairs",
        "minecraft:crimson_stem",
        "minecraft:stripped_crimson_stem",
        "minecraft:crimson_trapdoor",
    ),
    0x5C191D: ("minecraft:crimson_hyphae",
               "minecraft:stripped_crimson_hyphae"),
    0x167E86: ("minecraft:warped_nylium",),
    0x3A8E8C: (
        "minecraft:warped_fence",
        "minecraft:warped_fence_gate",
        "minecraft:warped_planks",
        "minecraft:warped_pressure_plate",
        "minecraft:warped_sign",
        "minecraft:warped_wall_sign",
        "minecraft:warped_slab",
        "minecraft:warped_stairs",
        "minecraft:warped_stem",
        "minecraft:stripped_warped_stem",
        "minecraft:warped_trapdoor",
    ),
    0x562C3E: ("minecraft:warped_hyphae", "minecraft:stripped_warped_hyphae"),
    0x14B485: ("minecraft:warped_wart_block",),
}
PALETTELOOKUP = {}
for hex, blocks in PALETTE.items():
    for block in blocks:
        PALETTELOOKUP[block] = hex


# ========================================================= biome-related

BIOMES = {
    0: "ocean",
    1: "plains",
    2: "desert",
    3: "mountains",
    4: "forest",
    5: "taiga",
    6: "swamp",
    7: "river",
    8: "nether_wastes",
    9: "the_end",
    10: "frozen_ocean",
    11: "frozen_river",
    12: "snowy_tundra",
    13: "snowy_mountains",
    14: "mushroom_fields",
    15: "mushroom_field_shore",
    16: "beach",
    17: "desert_hills",
    18: "wooded_hills",
    19: "taiga_hills",
    20: "mountain_edge",
    21: "jungle",
    22: "jungle_hills",
    23: "jungle_edge",
    24: "deep_ocean",
    25: "stone_shore",
    26: "snowy_beach",
    27: "birch_forest",
    28: "birch_forest_hills",
    29: "dark_forest",
    30: "snowy_taiga",
    31: "snowy_taiga_hills",
    32: "giant_tree_taiga",
    33: "giant_tree_taiga_hills",
    34: "wooded_mountains",
    35: "savanna",
    36: "savanna_plateau",
    37: "badlands",
    38: "wooded_badlands_plateau",
    39: "badlands_plateau",
    40: "small_end_islands",
    41: "end_midlands",
    42: "end_highlands",
    43: "end_barrens",
    44: "warm_ocean",
    45: "lukewarm_ocean",
    46: "cold_ocean",
    47: "deep_warm_ocean",
    48: "deep_lukewarm_ocean",
    49: "deep_cold_ocean",
    50: "deep_frozen_ocean",
    127: "the_void",
    129: "sunflower_plains",
    130: "desert_lakes",
    131: "gravelly_mountains",
    132: "flower_forest",
    133: "taiga_mountains",
    134: "swamp_hills",
    140: "ice_spikes",
    149: "modified_jungle",
    151: "modified_jungle_edge",
    155: "tall_birch_forest",
    156: "tall_birch_hills",
    157: "dark_forest_hills",
    158: "snowy_taiga_mountains",
    160: "giant_spruce_taiga",
    161: "giant_spruce_taiga_hills",
    162: "modified_gravelly_mountains",
    163: "shattered_savanna",
    164: "shattered_savanna_plateau",
    165: "eroded_badlands",
    166: "modified_wooded_badlands_plateau",
    167: "modified_badlands_plateau",
    168: "bamboo_jungle",
    169: "bamboo_jungle_hills",
    170: "soul_sand_valley",
    171: "crimson_forest",
    172: "warped_forest",
    173: "basalt_deltas",
}

# ========================================================= technical values

# the width of ASCII characters in pixels
# space between characters is 1
# the widest supported Unicode character is 9 wide
ASCIIPIXELS = {
    "A": 5,
    "a": 5,
    "B": 5,
    "b": 5,
    "C": 5,
    "c": 5,
    "D": 5,
    "d": 5,
    "E": 5,
    "e": 5,
    "F": 5,
    "f": 4,
    "G": 5,
    "g": 5,
    "H": 5,
    "h": 5,
    "I": 3,
    "i": 1,
    "J": 5,
    "j": 5,
    "K": 5,
    "k": 4,
    "L": 5,
    "l": 2,
    "M": 5,
    "m": 5,
    "N": 5,
    "n": 5,
    "O": 5,
    "o": 5,
    "P": 5,
    "p": 5,
    "Q": 5,
    "q": 5,
    "R": 5,
    "r": 5,
    "S": 5,
    "s": 5,
    "T": 5,
    "t": 3,
    "U": 5,
    "u": 5,
    "V": 5,
    "v": 5,
    "W": 5,
    "w": 5,
    "X": 5,
    "x": 5,
    "Y": 5,
    "y": 5,
    "Z": 5,
    "z": 5,
    "1": 5,
    "2": 5,
    "3": 5,
    "4": 5,
    "5": 5,
    "6": 5,
    "7": 5,
    "8": 5,
    "9": 5,
    "0": 5,
    " ": 3,
    "!": 1,
    "@": 6,
    "#": 5,
    "$": 5,
    "£": 5,
    "%": 5,
    "^": 5,
    "&": 5,
    "*": 3,
    "(": 3,
    ")": 3,
    "_": 5,
    "-": 5,
    "+": 5,
    "=": 5,
    "~": 6,
    "[": 3,
    "]": 3,
    "{": 3,
    "}": 3,
    "|": 1,
    "\\": 5,
    ":": 1,
    ";": 1,
    '"': 3,
    "'": 1,
    ",": 1,
    "<": 4,
    ">": 4,
    ".": 1,
    "?": 5,
    "/": 5,
    "`": 2,
}

# terminal colour codes


def supports_color():
    """Return True if the running system's terminal supports color."""
    plat = sys.platform
    supported_platform = plat != "Pocket PC" and (
        plat != "win32" or "ANSICON" in os.environ
    )
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty


if supports_color():
    TCOLORS = {
        "black": "\033[38;2;000;000;000m",
        "gray": "\033[38;2;128;128;128m",
        "white": "\033[38;2;255;255;255m",
        "pink": "\033[38;2;255;192;203m",
        "red": "\033[38;2;255;000;000m",
        "orange": "\033[38;2;255;165;000m",
        "yellow": "\033[38;2;255;255;000m",
        "darkgreen": "\033[38;2;000;128;000m",
        "green": "\033[38;2;000;255;000m",
        "blue": "\033[38;2;135;206;235m",
        "darkblue": "\033[38;2;000;000;255m",
        "magenta": "\033[38;2;255;000;255m",
        "brown": "\033[38;2;139;069;019m",
        "CLR": "\033[0m",
    }  # 38 is replaced by 48 for background
else:
    TCOLORS = {
        "black": "",
        "gray": "",
        "white": "",
        "pink": "",
        "red": "",
        "orange": "",
        "yellow": "",
        "darkgreen": "",
        "green": "",
        "blue": "",
        "darkblue": "",
        "magenta": "",
        "brown": "",
        "CLR": "",
    }  # colour codes not printed

INVENTORYDIMENSIONS = {
    (9, 3): {"minecraft:barrel", } | CHESTS | SHULKER_BOXES,
    (3, 3): {"minecraft:dispenser", "minecraft:dropper", },
    (5, 1): {"minecraft:hopper", "minecraft:brewing_stand", },
    (3, 1): FURNACES,
}
INVENTORYLOOKUP = {}
for dimensions, blocks in INVENTORYDIMENSIONS.items():
    for block in blocks:
        INVENTORYLOOKUP[block] = dimensions

# version checking


def closestVersion(version):
    """Retrieve next-best version code to given version code."""
    if version in VERSIONS:
        return version
    for v in sorted(VERSIONS.keys(), reverse=True):
        if version - v >= 0:
            return v
    return 0


def checkVersion():
    """Retrieve Minecraft version and check compatibility."""
    from .worldLoader import WorldSlice

    slice = WorldSlice(0, 0, 1, 1)  # single-chunk slice
    current = int(slice.nbtfile["Chunks"][0]["DataVersion"].value)
    closestname = "Unknown"
    # check compatibility
    if current not in VERSIONS or VERSIONS[SUPPORTS] not in VERSIONS[current]:
        closest = closestVersion(current)
        closestname = VERSIONS[closest]
        closestname += " snapshot" if current > closest else ""
        if closest > SUPPORTS:
            print(
                f"{TCOLORS['orange']}WARNING: You are using a newer "
                "version of Minecraft then GDPC supports!\n"
                f"\tSupports: {VERSIONS[SUPPORTS]} "
                f"Detected: {closestname}{TCOLORS['CLR']}"
            )
        elif closest < SUPPORTS:
            print(
                f"{TCOLORS['orange']}WARNING: You are using an older "
                "version of Minecraft then GDPC supports!\n"
                f"\tSupports: {VERSIONS[SUPPORTS]} "
                f"Detected: {closestname}{TCOLORS['CLR']}"
            )
        else:
            raise ValueError(
                f"{TCOLORS['red']}Invalid supported version: "
                f"SUPPORTS = {current}!{TCOLORS['CLR']}"
            )
    else:
        closestname = VERSIONS[current]

    return (current, closestname)


CURRENTV, CURRENTVNAME = checkVersion()
