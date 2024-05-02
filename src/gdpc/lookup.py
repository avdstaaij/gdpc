"""Stores lists of various information on blocks, biomes and more.

NOTE: The block id categories here may not be fully up-to-date with the latest supported Minecraft
version. Although the block categories are not officially deprecated, there is a high chance that
they will be in the future. They will most likely be replaced with categories automatically
constructed from Minecraft's block tags (https://minecraft.wiki/Tag#Block_tags), because
this is more standardized and way easier to keep up-to-date.

To get a complete listing of all blocks for any Minecraft version, including various properties,
we currently recommend the `minecraft-data` package
(https://github.com/SpockBotMC/python-minecraft-data).
"""

# Note: The "#:" comments are so Sphinx autdodoc includes the constants.
# The following regex replace adds missing comments mostly correctly:
# Find:    ^(?!#)(.+)(?<!\\)(?<!#:)(?<!\()(?<!\{)(?<!,)$
# Replace: $1 #:


from typing import Dict, Iterable, Optional, Set, Union

from glm import ivec2

from .utils import isIterable


# ==================================================================================================
# Helper functions
# ==================================================================================================


def variate(
    variations: Iterable[str],
    extensions: Optional[Union[str, Iterable[Optional[str]]]] = None,
    isPrefix:   bool          = False,
    separator:  str           = "_",
    namespace:  Optional[str] = "minecraft",
) -> Set[str]:
    """Generates block variations.

    Returns a set of strings. For each variation, each extension is either appended or prepended
    depending on ``isPrefix``, using ``separator``.

    If ``namespace`` is not None, each string is additionally prefixed with ``"<namespace>:"``.
    """

    joined = None
    combinations = set()

    if extensions is None:
        joined = variations
    elif isinstance(extensions, str):
        combinations = {(v, extensions) for v in variations}
    elif isIterable(extensions):
        combinations = {(v, e) for v in variations for e in extensions}
    if isPrefix:
        combinations = {(e, v) for v, e in combinations}

    namespacePrefix = f"{namespace}:" if namespace is not None else ""

    if joined is None:
        joined = set()
        for c in combinations:
            if None in c:
                temp = list(c)
                temp.remove(None)
                c = tuple(temp)
            joined.add(separator.join(c))
    return {f"{namespacePrefix}{j}" for j in joined}


# ==================================================================================================
# Data
# ==================================================================================================


# ========================================================= materials


# COLOURS
# based on https://minecraft.wiki/Dye#Color_values
#   and https://minecraft.wiki/Block_colors
DYE_COLORS = {
    "white":      "0xF9FFFE",
    "orange":     "0xF9801D",
    "magenta":    "0xC74EBD",
    "light_blue": "0x3AB3DA",
    "yellow":     "0xFED83D",
    "lime":       "0x80C71F",
    "pink":       "0xF38BAA",
    "gray":       "0x474F52",
    "light_gray": "0x9D9D97",
    "cyan":       "0x169C9C",
    "purple":     "0x8932B8",
    "blue":       "0x3C44AA",
    "brown":      "0x835432",
    "green":      "0x5E7C16",
    "red":        "0xB02E26",
    "black":      "0x1D1D21",
} #:
GRASS_COLORS = {
    "generic":         "0x8EB971",
    "desert":          "0xBFB755",
    "badlands":        "0x90814D",
    "plains":          "0x91BD59",
    "taiga":           "0x86B783", "pine_taiga": "0x86B87F",
    "meadow":          "0x83BB6D",
    "snowy":           "0x80B497", "snowy_beach": "0x83B593",
    "forest":          "0x79C05A", "birch_forest": "0x88BB67",
    "dark_forest":     "0x507A32",
    "sparse_jungle":   "0x64C73F", "jungle": "0x59C93C",
    "mushroom_fields": "0x55C93F",
    "stony_peaks":     "0x9ABE4B",
    "windswept":       "0x8AB689",
    "swamp_brown":     "0x6A7039", "swamp_green": "0x4C763C",
} #:
FOLIAGE_COLORS = {
    "generic":         "0x71A74D",
    "desert":          "0xAEA42A",
    "badlands":        "0x9E814D",
    "plains":          "0x77AB2F",
    "taiga":           "0x68A464", "pine_taiga": "0x68A55F",
    "meadow":          "0x63A948",
    "snowy":           "0x60A17B", "snowy_beach": "0x64A278",
    "forest":          "0x59AE30", "birch_forest": "0x6BA941",
    "sparse_jungle":   "0x3EB80F", "jungle": "0x30BB0B",
    "mushroom_fields": "0x2BBB0F",
    "stony_peaks":     "0x82AC1E",
    "windswept":       "0x6DA36B",
    "swamp":           "0x6A7039",
} #:
WATER_COLORS = {
    "generic":  "0x3F76E4",
    "meadow":   "0x0E4ECF",
    "warm":     "0x43D5EE",
    "lukewarm": "0x45ADF2",
    "cold":     "0x3D57D6",
    "frozen":   "0x3938C9",
    "swamp":    "0x617B64",
} #:
REDSTONE_COLORS = {
    "0":  "0x4B0000",
    "1":  "0x6F0000",
    "2":  "0x790000",
    "3":  "0x820000",
    "4":  "0x8C0000",
    "5":  "0x970000",
    "6":  "0xA10000",
    "7":  "0xAB0000",
    "8":  "0xB50000",
    "9":  "0xBF0000",
    "10": "0xCA0000",
    "11": "0xD30000",
    "12": "0xDD0000",
    "13": "0xE70600",
    "14": "0xF11B00",
    "15": "0xFC3100",
} #:

# SHADES
# alternative terms that directly correlate with a dye color
CORAL_SHADES = {"tube": "blue", "brain": "pink", "bubble": "purple",
                "fire": "red", "horn": "yellow", "dead": "grey"} #:

# TERMINOLOGY
# words used to describe categorically similar types
CRIMSON_WORDS = {"crimson", "wart", "weeping", } #:
WARPED_WORDS = {"warped", "sprouts", "twisted"} #:

# MATERIAL TYPES
SAND_TYPES = {None, "red", } #:
IGNEOUS_TYPES = {"andesite", "diorite", "granite", } #:
STONE_TYPES = {"stone", "cobblestone", } #:
COBBLESTONE_TYPES = {None, "mossy", } #:

ORE_TYPES = {"coal", "lapis", "iron", "gold",
             "redstone", "diamond", "emerald", } #:
NETHER_ORE_TYPES = {"nether_gold", "nether_quartz", } #:

LIMITED_SANDSTONE_TYPES = {None, "smooth", } #:
SANDSTONE_TYPES = {"cut", "chiseled", } | LIMITED_SANDSTONE_TYPES #:
# 1.17 NOTE: "smooth",
BASALT_TYPES = {None, "polished", } #:
OBSIDIAN_TYPES = {None, "crying", } #:
STEMFRUIT_TYPES = {"pumpkin", "melon", } #:

AIR_TYPES = {None, "void", "cave", } #:
FIRE_TYPES = {None, "soul", } #:

ICE_TYPES = {None, "blue", "packed", "frosted"} #:
# bedrock NOTE: "flowing",
LIQUID_TYPES = {None, } #:

WOOD_TYPES = {"oak", "birch", "spruce", "jungle", "dark_oak", "acacia", "mangrove", } #:
MUSHROOM_TYPES = {"brown", "red", } #:
WART_TYPES = {"nether", "warped", } #:
FUNGUS_TYPES = {"crimson", "warped", } #:
FUNGUS_VINE_TYPES = {"weeping", "twisting", } #:

TULIP_TYPES = {"red", "orange", "white", "pink", } #:
SMALL_FLOWER_TYPES = {"dandelion", "poppy", "blue_orchid", "allium",
                      "azure_bluet", "oxeye_daisy", "cornflower",
                      "lily_of_the_valley", "wither_rose", } \
                     | variate(TULIP_TYPES, "tulip", namespace=None) #:
TALL_FLOWER_TYPES = {"sunflower", "lilac", "rose_bush", "peony", } #:

POTTED_PLANT_TYPES = {"dandelion", "poppy", "blue_orchid", "allium",
                      "azure_bluet", "oxeye_daisy",
                      "red_tulip", "orange_tulip", "white_tulip", "pink_tulip",
                      "cornflower", "lily_of_the_valley", "wither_rose",
                      "fern", "dead_bush", "cactus", "bamboo", ""} \
                     | variate(WOOD_TYPES, "sapling", namespace=None) \
                     | variate(MUSHROOM_TYPES, "mushroom", namespace=None) \
                     | variate(FUNGUS_TYPES, "fungus", namespace=None) \
                     | variate(FUNGUS_TYPES, "roots", namespace=None) #:

LIVE_CORAL_TYPES = set(CORAL_SHADES) - {"dead"} #:
DEAD_CORAL_TYPES = variate(LIVE_CORAL_TYPES, "dead",
                           isPrefix=True, namespace=None) #:
CORAL_TYPES = LIVE_CORAL_TYPES | DEAD_CORAL_TYPES #:

WOODY_TYPES = WOOD_TYPES | FUNGUS_TYPES #:

LIMITED_STONE_BRICK_TYPES = {None, "mossy", } #:
STONE_BRICK_TYPES = {"cracked", "chiseled", } | LIMITED_STONE_BRICK_TYPES #:

NETHER_BRICK_TYPES = {None, "red", } #:

QUARTZ_TYPES = {None, "smooth", } #:
QUARTZ_BLOCK_TYPES = {"block", "pillar", "bricks", } #:
POLISHED_BLACKSTONE_TYPES = {None, "brick", } #:
POLISHED_BLACKSTONE_BRICK_TYPES = {None, "cracked", } #:
SMOOTH_SANDSTONE_TYPES = variate(SAND_TYPES, "smooth",
                                 isPrefix=True, namespace=None) #:
CUT_SANDSTONE_TYPES = variate(SAND_TYPES, "cut",
                              isPrefix=True, namespace=None) #:
PRISMARINE_TYPES = {None, "dark", } #:
LIMITED_NETHER_BRICK_TYPES = {None, "red", } #:
NETHER_BRICK_TYPES = {"cracked", "chiseled", } | LIMITED_NETHER_BRICK_TYPES #:
PURPUR_TYPES = {"block", "pillar", } #:

ANVIL_TYPES = {None, "chipped", "damaged", } #:
CHEST_TYPES = {None, "trapped", "ender", } #:
CAULDRON_TYPES = {None, "lava", "powder_snow", "water", } #:

SPONGE_TYPES = {None, "wet", } #:
SKULL_TYPES = {"skeleton", "wither_skeleton", } #:
HEAD_TYPES = {"zombie", "player", "creeper", "dragon", } #:
CRANIUM_TYPES = SKULL_TYPES | HEAD_TYPES #:

WEIGHTED_PRESSURE_PLATE_TYPES = {"heavy", "light", } #:
SENSOR_RAIL_TYPES = {"detector", } #:
ACTUATOR_RAIL_TYPES = {None, "activator", "powered", } #:
PISTON_TYPES = {None, "sticky", } #:
COMMAND_BLOCK_TYPES = {None, "chain", "repeating", } #:

# NAMED MATERIAL TYPES
# for usage as an extension
# FIXME: replace with better `variate()` functionality
NAMED_STONE_BRICK_TYPES = variate(STONE_BRICK_TYPES, "stone_bricks",
                                  namespace=None) #:
NAMED_WOOD_TYPES = variate(WOOD_TYPES, "wood", namespace=None) #:
NAMED_LOG_TYPES = variate(WOOD_TYPES, "log", namespace=None) #:
NAMED_STEM_TYPES = variate(FUNGUS_TYPES, "stem", namespace=None) #:
NAMED_HYPHAE_TYPES = variate(FUNGUS_TYPES, "hyphae", namespace=None) #:

NAMED_LIVE_CORAL_TYPES = variate(LIVE_CORAL_TYPES, "coral", namespace=None) #:
NAMED_DEAD_CORAL_TYPES = variate(DEAD_CORAL_TYPES, "coral", namespace=None) #:
NAMED_CORAL_TYPES = NAMED_LIVE_CORAL_TYPES | NAMED_DEAD_CORAL_TYPES #:

NAMED_POLISHED_BLACKSTONE_TYPES = \
    variate(POLISHED_BLACKSTONE_TYPES, "polished_blackstone",
            isPrefix=True, namespace=None) #:
NAMED_POLISHED_IGNEOUS_TYPES = variate(IGNEOUS_TYPES, "polished",
                                       isPrefix=True, namespace=None) #:
NAMED_PRISMARINE_TYPES = variate(PRISMARINE_TYPES, "prismarine",
                                 namespace=None) #:

# ========================================================= grouped by model

# natural
# minerals
OVERWORLD_ORES = variate(ORE_TYPES, "ore") #:

NETHERRACK_ORES = variate(NETHER_ORE_TYPES, "ore") #:
NETHER_ORES = {"minecraft:gilded_blackstone", } | NETHERRACK_ORES #:

END_ORES: Set[str] = set() #:

ORES = OVERWORLD_ORES | NETHER_ORES | END_ORES #:

MINERAL_BLOCKS = {"minecraft:quartz_block", "minecraft:netherite_block", } \
                 | variate(ORE_TYPES, "block") #:

# soils
SPREADING_DIRTS = {"minecraft:mycelium", "minecraft:grass_block", } #:
DIRTS = {"minecraft:coarse_dirt", "minecraft:dirt",
         "minecraft:grass_path", "minecraft:farmland", "minecraft:podzol", } \
        | SPREADING_DIRTS #:
SANDS = variate(SAND_TYPES, "sand") #:
GRANULARS = {"minecraft:gravel", } | SANDS #:
RIVERBED_SOILS = {"minecraft:dirt", "minecraft:clay",
                  "minecraft:sand", "minecraft:gravel", } #:
OVERWORLD_SOILS = DIRTS | GRANULARS | RIVERBED_SOILS #:

NYLIUMS = variate(FUNGUS_TYPES, "nylium") #:
NETHERRACKS = {"minecraft:netherrack", } | NYLIUMS | NETHERRACK_ORES #:
SOUL_SOILS = {"minecraft:soul_sand", "minecraft:soul_soil", } #:
NETHER_SOILS = {"minecraft:netherrack", } | NYLIUMS | SOUL_SOILS #:

END_SOILS: Set[str] = set() #:

SOILS = OVERWORLD_SOILS | NETHER_SOILS | END_SOILS #:

# stones
IGNEOUS = variate(IGNEOUS_TYPES) #:
OBSIDIAN_BLOCKS = variate(OBSIDIAN_TYPES, "obsidian") #:
COBBLESTONES = variate(COBBLESTONE_TYPES, "cobblestone") #:
INFESTED_STONE_BRICKS = variate(
    NAMED_STONE_BRICK_TYPES, "infested", isPrefix=True) #:
INFESTED = variate(STONE_TYPES, "infested", isPrefix=True) \
           | INFESTED_STONE_BRICKS #:
RAW_SANDSTONES = variate(SAND_TYPES, "sandstone") #:
TERRACOTTAS = variate({None, } | set(DYE_COLORS), "terracotta") #:
OVERWORLD_STONES = {"minecraft:stone", } | IGNEOUS | OBSIDIAN_BLOCKS \
                   | COBBLESTONES | INFESTED | RAW_SANDSTONES | TERRACOTTAS #:

BASALT_BLOCKS = variate(BASALT_TYPES, "basalt") #:
NETHER_STONES = {"minecraft:blackstone", "minecraft:ancient_debris", } #:

END_STONES = {"minecraft:end_stone", } #:

VOLCANIC = {"minecraft:magma_block", } | BASALT_BLOCKS | OBSIDIAN_BLOCKS #:
STONES = {"minecraft:bedrock", } | VOLCANIC \
         | OVERWORLD_STONES | NETHER_STONES | END_STONES #:

# liquids
# 1.17 NOTE: "minecraft:powder_snow",
SNOWS = {"minecraft:snow", "minecraft:snow_block", } #:
ICE_BLOCKS = variate(ICE_TYPES, "ice") #:
WATERS = variate(LIQUID_TYPES, "water") #:
WATER_BASED = {"minecraft:bubble_column", } | SNOWS | ICE_BLOCKS | WATERS #:
LAVAS = variate(LIQUID_TYPES, "lava") #:
LAVA_BASED = VOLCANIC | LAVAS #:
LIQUIDS = WATERS | LAVAS #:
LIQUID_BASED = WATER_BASED | LAVA_BASED #:

# non-physical
AIRS = variate(AIR_TYPES, "air") #:
FLUIDS = LIQUIDS | AIRS #:
FIRES = variate(FIRE_TYPES, "fire") #:

# life
# fungals (mushrooms and fungi)
SMALL_MUSHROOMS = variate(MUSHROOM_TYPES, "mushroom") #:
MUSHROOM_CAPS = variate(MUSHROOM_TYPES, "mushroom_block") #:
MUSHROOM_STEMS = {"minecraft:mushroom_stem", } #:
MUSHROOM_BLOCKS = MUSHROOM_CAPS | MUSHROOM_STEMS #:
MUSHROOMS = SMALL_MUSHROOMS | MUSHROOM_BLOCKS #:

SMALL_DECORATIVE_FUNGI = {"minecraft:nether_sprouts", } \
                         | variate(FUNGUS_TYPES, "fungus") #:
SMALL_FARMABLE_FUNGI = {"minecraft:nether_wart", } \
                       | variate(FUNGUS_TYPES, "roots") #:
SMALL_FUNGI = SMALL_DECORATIVE_FUNGI | SMALL_FARMABLE_FUNGI #:
WART_BLOCKS = variate(WART_TYPES, "wart_block") #:
FUNGUS_VINES = variate(FUNGUS_VINE_TYPES, "vines") #:

BARKED_FUNGUS_STEMS = variate(FUNGUS_TYPES, "stem") #:
BARKED_FUNGUS_HYPHAE = variate(FUNGUS_TYPES, "hyphae") #:
BARKED_FUNGUS_STALKS = BARKED_FUNGUS_STEMS | BARKED_FUNGUS_HYPHAE #:
STRIPPED_FUNGUS_STEMS = variate(NAMED_STEM_TYPES, "stripped", isPrefix=True) #:
STRIPPED_FUNGUS_HYPHAE = variate(NAMED_HYPHAE_TYPES, "stripped", isPrefix=True) #:
STRIPPED_FUNGUS_STALKS = STRIPPED_FUNGUS_STEMS | STRIPPED_FUNGUS_HYPHAE #:
FUNGUS_STEMS = BARKED_FUNGUS_STEMS | STRIPPED_FUNGUS_STEMS #:
FUNGUS_HYPHAE = BARKED_FUNGUS_HYPHAE | STRIPPED_FUNGUS_HYPHAE #:
FUNGUS_STALKS = FUNGUS_STEMS | FUNGUS_HYPHAE #:
FUNGUS_GROWTH_BLOCKS = {"minecraft:shroomlight", } \
                       | WART_BLOCKS | FUNGUS_STALKS #:
FUNGI = SMALL_FUNGI | FUNGUS_GROWTH_BLOCKS #:

SMALL_FUNGALS = SMALL_MUSHROOMS | SMALL_FUNGI #:
FUNGAL_CAPS = MUSHROOM_CAPS | WART_BLOCKS #:
FUNGAL_STEMS = MUSHROOM_STEMS | FUNGUS_STEMS #:
FUNGAL_BLOCKS = MUSHROOM_BLOCKS | FUNGUS_GROWTH_BLOCKS #:
FUNGALS = SMALL_FUNGALS | FUNGAL_BLOCKS | FUNGUS_VINES #:

VINES = {"minecraft:vine", } | FUNGUS_VINES #:

# trees
SAPLINGS = variate(WOOD_TYPES, "sapling") #:
LEAVES = variate(WOOD_TYPES, "leaves") #:
FOLIAGE = {"minecraft:vine", } | LEAVES #:

BARKED_LOGS = variate(WOOD_TYPES, "log") #:
BARKED_WOODS = variate(WOOD_TYPES, "wood") #:
BARKED_TRUNKS = BARKED_LOGS | BARKED_WOODS #:
STRIPPED_LOGS = variate(NAMED_LOG_TYPES, "stripped", isPrefix=True) #:
STRIPPED_WOODS = variate(NAMED_WOOD_TYPES, "stripped", isPrefix=True) #:
STRIPPED_TRUNKS = STRIPPED_LOGS | STRIPPED_WOODS #:
WOODS = BARKED_TRUNKS | STRIPPED_WOODS #:
LOGS = BARKED_LOGS | STRIPPED_LOGS #:
TRUNKS = BARKED_TRUNKS | STRIPPED_TRUNKS #:

BARKED_TREE_BLOCKS = LEAVES | BARKED_WOODS | BARKED_LOGS #:
TREE_BLOCKS = LEAVES | WOODS | LOGS #:
TREES = SAPLINGS | TREE_BLOCKS #:

# grasses
TRUE_GRASSES = {"minecraft:grass_block",
                "minecraft:grass", "minecraft:tall_grass", } #:
FERNS = {"minecraft:fern", "minecraft:large_fern", } #:
BAMBOOS = {"minecraft:bamboo", "minecraft:bamboo_sapling", } #:

GRASS_BLOCKS = {"minecraft:grass_block", } #:
SHORT_GRASSES = {"minecraft:grass", "minecraft:fern", } #:
TALL_GRASSES = {"minecraft:tall_grass", "minecraft:large_fern", } #:
CANE_GRASSES = {"minecraft:sugar_cane", } | BAMBOOS #:

GRASS_PLANTS = SHORT_GRASSES | TALL_GRASSES | CANE_GRASSES #:
GRASSES = GRASS_BLOCKS | GRASS_PLANTS #:

# crops
PUMPKINS = {"minecraft:pumpkin", "minecraft:carved_pumpkin", } #:
BLOCK_CROP_STEMS = variate(STEMFRUIT_TYPES, "stem") #:
BLOCK_CROP_FRUITS = variate(STEMFRUIT_TYPES) #:
BLOCK_CROPS = BLOCK_CROP_STEMS | BLOCK_CROP_FRUITS #:

FARMLAND_CROPS = {"minecraft:wheat", "minecraft:carrots",
                  "minecraft:potatoes", "minecraft:beetroots", } \
                 | BLOCK_CROP_STEMS #:
WILD_CROPS = {"minecraft:cocoa", "minecraft:sweet_berry_bush", } #:

CROPS = BLOCK_CROPS | FARMLAND_CROPS | WILD_CROPS #:

# flowers
TULIPS = variate(TULIP_TYPES, "tulip") #:
SMALL_FLOWERS = variate(SMALL_FLOWER_TYPES) #:
TALL_FLOWERS = variate(TALL_FLOWER_TYPES) #:
FLOWERS = SMALL_FLOWERS | TALL_FLOWERS #:

# aquatic flora
SEAGRASSES = {"minecraft:seagrass", "minecraft:tall_seagrass", } #:
KELPS = {"minecraft:kelp_plant", "minecraft:kelp", } #:
WATER_PLANTS = {"minecraft:lily_pad", } | SEAGRASSES | KELPS #:

OVERWORLD_PLANT_BLOCKS = PUMPKINS | BLOCK_CROPS | MUSHROOM_BLOCKS | TREE_BLOCKS #:
OVERWORLD_PLANTS = {"minecraft:cactus", "minecraft:dead_bush", } \
                   | MUSHROOMS | FOLIAGE | TREES | GRASSES | CROPS | FLOWERS | WATER_PLANTS #:

NETHER_PLANT_BLOCKS = FUNGUS_GROWTH_BLOCKS #:
NETHER_PLANTS = FUNGI #:

CHORUS = {"minecraft:chorus_plant", "minecraft:chorus_flower", } #:
END_PLANT_BLOCKS: Set[str] = set() #:
END_PLANTS = CHORUS #:

PLANT_BLOCKS = OVERWORLD_PLANT_BLOCKS | NETHER_PLANT_BLOCKS | END_PLANT_BLOCKS #:
PLANTS = OVERWORLD_PLANTS | NETHER_PLANTS | END_PLANTS #:

# marine life
LIVE_CORAL_BLOCKS = variate(NAMED_LIVE_CORAL_TYPES, "block") #:
LIVE_CORAL_COLONY = variate(LIVE_CORAL_TYPES, "coral") #:
LIVE_CORAL_FANS = variate(NAMED_LIVE_CORAL_TYPES, "fan") #:
LIVE_CORALS = LIVE_CORAL_BLOCKS | LIVE_CORAL_COLONY | LIVE_CORAL_FANS #:
DEAD_CORAL_BLOCKS = variate(NAMED_DEAD_CORAL_TYPES, "block") #:
DEAD_CORAL_COLONY = variate(DEAD_CORAL_TYPES, "coral") #:
DEAD_CORAL_FANS = variate(NAMED_DEAD_CORAL_TYPES, "fan") #:
DEAD_CORALS = DEAD_CORAL_BLOCKS | DEAD_CORAL_COLONY | DEAD_CORAL_FANS #:
CORAL_BLOCKS = LIVE_CORAL_BLOCKS | DEAD_CORAL_BLOCKS #:
CORAL_COLONY = LIVE_CORAL_COLONY | DEAD_CORAL_COLONY #:
CORAL_FANS = LIVE_CORAL_FANS | DEAD_CORAL_FANS #:

CORALS = LIVE_CORALS | DEAD_CORALS #:

SPONGES = variate(SPONGE_TYPES, "sponge") #:

MARINE_ANIMALS = {"minecraft:sea_pickle", } | CORALS | SPONGES #:
MARINE_LIFE = WATER_PLANTS | MARINE_ANIMALS #:

OVERWORLD_ANIMALS = MARINE_ANIMALS #:
NETHER_ANIMALS: Set[str] = set() #:
END_ANIMALS: Set[str] = set() #:
ANIMALS = OVERWORLD_ANIMALS | NETHER_ANIMALS | END_ANIMALS #:

# animal product
EGGS = {"minecraft:dragon_egg", "minecraft:turtle_egg", } #:
BEE_NESTS = {"minecraft:beehive", "minecraft:bee_nest", } #:
NESTS = {"minecraft:bee_nest", "minecraft:cobweb", } #:
REMAINS = {"minecraft:bone_block", } #:

OVERWORLD_ANIMAL_PRODUCTS = {"minecraft:honeycomb_block"} \
                            | EGGS | NESTS #:
NETHER_ANIMAL_PRODUCTS: Set[str] = set() #:
END_ANIMAL_PRODUCTS = {"minecraft:dragon_egg", } #:
ANIMAL_PRODUCTS = REMAINS \
                  | OVERWORLD_ANIMAL_PRODUCTS | NETHER_ANIMAL_PRODUCTS | END_ANIMAL_PRODUCTS #:

OVERWORLD_LIFE = OVERWORLD_PLANTS | OVERWORLD_PLANT_BLOCKS \
                 | OVERWORLD_ANIMALS | OVERWORLD_ANIMAL_PRODUCTS #:
NETHER_LIFE = NETHER_PLANTS | NETHER_PLANT_BLOCKS \
              | NETHER_ANIMALS | NETHER_ANIMAL_PRODUCTS #:
END_LIFE = END_PLANTS | END_PLANT_BLOCKS | END_ANIMALS | END_ANIMAL_PRODUCTS #:
LIFE = OVERWORLD_LIFE | NETHER_LIFE | END_LIFE | ANIMAL_PRODUCTS #:

# building
# decoration
WOOLS = variate(DYE_COLORS, "wool") #:
CARPETS = variate(DYE_COLORS, "carpet") #:
BANNERS = variate(DYE_COLORS, "banner") #:
BEDS = variate(DYE_COLORS, "bed") #:

STAINED_GLASS_BLOCKS = variate(DYE_COLORS, "stained_glass") #:
GLASS_BLOCKS = {"minecraft:glass", } | STAINED_GLASS_BLOCKS #:
STAINED_GLASS_PANES = variate(DYE_COLORS, "stained_glass_pane") #:
GLASS_PANES = {"minecraft:glass_pane", } | STAINED_GLASS_PANES #:
STAINED_GLASSES = STAINED_GLASS_BLOCKS | STAINED_GLASS_PANES #:
PLAIN_GLASSES = {"minecraft:glass", "minecraft:glass_pane", } #:
GLASSES = GLASS_BLOCKS | GLASS_PANES #:

GLAZED_TERRACOTTAS = variate(DYE_COLORS, "glazed_terracotta") #:

# slabs
WOOD_SLABS = variate(WOOD_TYPES, "slab") #:
FUNGUS_SLABS = variate(FUNGUS_TYPES, "slab") #:
WOODY_SLABS = WOOD_SLABS | FUNGUS_SLABS #:
STONE_SLABS = {"minecraft:stone_slab", "minecraft:smooth_stone_slab", } #:
RAW_IGNEOUS_SLABS = variate(IGNEOUS_TYPES, "slab") #:
POLISHED_IGNEOUS_SLABS = variate(NAMED_POLISHED_IGNEOUS_TYPES, "slab") #:
IGNEOUS_SLABS = RAW_IGNEOUS_SLABS | POLISHED_IGNEOUS_SLABS #:
COBBLESTONE_SLABS = variate(COBBLESTONE_TYPES, "cobblestone_slab") #:
STONE_BRICK_SLABS = variate(LIMITED_STONE_BRICK_TYPES, "stone_brick_slab") #:
RAW_SANDSTONE_SLABS = variate(SAND_TYPES, "sandstone_slab") #:
SMOOTH_SANDSTONE_SLABS = variate(SMOOTH_SANDSTONE_TYPES, "sandstone_slab") #:
CUT_SANDSTONE_SLABS = variate(CUT_SANDSTONE_TYPES, "sandstone_slab") #:
SANDSTONE_SLABS = RAW_SANDSTONE_SLABS | SMOOTH_SANDSTONE_SLABS \
                  | CUT_SANDSTONE_SLABS #:
PRISMARINE_SLABS = {"minecraft:prismarine_brick_slab", } \
                   | variate(NAMED_PRISMARINE_TYPES, "slab") #:
NETHER_BRICK_SLABS = variate(LIMITED_NETHER_BRICK_TYPES, "nether_brick_slab") #:
QUARTZ_SLABS = variate(QUARTZ_TYPES, "quartz_slab") #:
BLACKSTONE_SLABS = {"minecraft:blackstone_slab", } \
                   | variate(NAMED_POLISHED_BLACKSTONE_TYPES, "slab") #:

OVERWORLD_SLABS = {"minecraft:brick_slab", } \
                  | WOOD_SLABS | COBBLESTONE_SLABS | STONE_SLABS | STONE_BRICK_SLABS \
                  | IGNEOUS_SLABS | SANDSTONE_SLABS | PRISMARINE_SLABS #:
NETHER_SLABS = FUNGUS_SLABS | NETHER_BRICK_SLABS | QUARTZ_SLABS \
               | BLACKSTONE_SLABS #:
END_SLABS = {"minecraft:end_stone_brick_slab", "minecraft:purpur_slab", } #:
SLABS = OVERWORLD_SLABS | NETHER_SLABS | END_SLABS #:

# stairs
WOOD_STAIRS = variate(WOOD_TYPES, "stairs") #:
FUNGUS_STAIRS = variate(FUNGUS_TYPES, "stairs") #:
WOODY_STAIRS = WOOD_STAIRS | FUNGUS_STAIRS #:
STONE_STAIRS = {"minecraft:stone_stairs", } #:
RAW_IGNEOUS_STAIRS = variate(IGNEOUS_TYPES, "stairs") #:
POLISHED_IGNEOUS_STAIRS = variate(NAMED_POLISHED_IGNEOUS_TYPES, "stairs") #:
IGNEOUS_STAIRS = RAW_IGNEOUS_STAIRS | POLISHED_IGNEOUS_STAIRS #:
COBBLESTONE_STAIRS = variate(COBBLESTONE_TYPES, "cobblestone_stairs") #:
STONE_BRICK_STAIRS = variate(LIMITED_STONE_BRICK_TYPES, "stone_brick_stairs") #:
RAW_SANDSTONE_STAIRS = variate(SAND_TYPES, "sandstone_stairs") #:
SMOOTH_SANDSTONE_STAIRS = variate(SMOOTH_SANDSTONE_TYPES, "sandstone_stairs") #:
SANDSTONE_STAIRS = RAW_SANDSTONE_STAIRS | SMOOTH_SANDSTONE_STAIRS #:
PRISMARINE_STAIRS = {"minecraft:prismarine_brick_stairs", } \
                    | variate(NAMED_PRISMARINE_TYPES, "stairs") #:
NETHER_BRICK_STAIRS = variate(
    LIMITED_NETHER_BRICK_TYPES, "nether_brick_stairs") #:
QUARTZ_STAIRS = variate(QUARTZ_TYPES, "quartz_stairs") #:
BLACKSTONE_STAIRS = {"minecraft:blackstone_stairs", } \
                    | variate(NAMED_POLISHED_BLACKSTONE_TYPES, "stairs") #:

OVERWORLD_STAIRS = {"minecraft:brick_stairs", } \
                   | WOOD_STAIRS | COBBLESTONE_STAIRS | STONE_STAIRS | STONE_BRICK_STAIRS \
                   | IGNEOUS_STAIRS | SANDSTONE_STAIRS | PRISMARINE_STAIRS #:
NETHER_STAIRS = FUNGUS_STAIRS | NETHER_BRICK_STAIRS | QUARTZ_STAIRS \
                | BLACKSTONE_STAIRS #:
END_STAIRS = {"minecraft:end_stone_brick_stairs", "minecraft:purpur_stairs", } #:
STAIRS = OVERWORLD_STAIRS | NETHER_STAIRS | END_STAIRS #:

# barriers
WOOD_FENCES = variate(WOOD_TYPES, "fence") #:
FUNGUS_FENCES = variate(FUNGUS_TYPES, "fence") #:
WOODY_FENCES = WOOD_FENCES | FUNGUS_FENCES #:
OVERWORLD_FENCES = WOOD_FENCES #:
NETHER_FENCES = {"minecraft:nether_brick_fence", } | FUNGUS_FENCES #:
END_FENCES: Set[str] = set() #:
FENCES = OVERWORLD_FENCES | NETHER_FENCES | END_FENCES #:

COBBLESTONE_WALLS = variate(COBBLESTONE_TYPES, "cobblestone_wall") #:
STONE_BRICK_WALLS = variate(LIMITED_STONE_BRICK_TYPES, "stone_brick_wall") #:
IGNEOUS_WALLS = variate(IGNEOUS_TYPES, "wall") #:
SANDSTONE_WALLS = variate(SAND_TYPES, "sandstone_wall") #:
NETHER_BRICK_WALLS = variate(LIMITED_NETHER_BRICK_TYPES, "nether_brick_wall") #:
BLACKSTONE_WALLS = {"minecraft:blackstone_wall", } \
                   | variate(NAMED_POLISHED_BLACKSTONE_TYPES, "wall") #:
OVERWORLD_WALLS = {"minecraft:brick_wall", "minecraft:prismarine_wall", } \
                  | COBBLESTONE_WALLS | STONE_BRICK_WALLS | IGNEOUS_WALLS | SANDSTONE_WALLS #:
NETHER_WALLS = NETHER_BRICK_WALLS | BLACKSTONE_WALLS #:
END_WALLS = {"minecraft:end_stone_brick_wall", } #:
WALLS = OVERWORLD_WALLS | NETHER_WALLS | END_WALLS #:

OVERWORLD_BARRIERS = OVERWORLD_FENCES | OVERWORLD_WALLS #:
NETHER_BARRIERS = NETHER_FENCES | NETHER_WALLS #:
END_BARRIERS = END_FENCES | END_WALLS #:
BARRIERS = FENCES | WALLS #:

# entryways
WOOD_DOORS = variate(WOOD_TYPES, "door") #:
FUNGUS_DOORS = variate(FUNGUS_TYPES, "door") #:
WOODY_DOORS = WOOD_DOORS | FUNGUS_DOORS #:
METAL_DOORS = {"minecraft:iron_door", } #:
OVERWORLD_DOORS = WOOD_DOORS | METAL_DOORS #:
NETHER_DOORS = FUNGUS_DOORS | METAL_DOORS #:
END_DOORS = METAL_DOORS #:
DOORS = OVERWORLD_DOORS | NETHER_DOORS | END_DOORS #:

WOOD_GATES = variate(WOOD_TYPES, "fence_gate") #:
FUNGUS_GATES = variate(FUNGUS_TYPES, "fence_gate") #:
WOODY_GATES = WOOD_GATES | FUNGUS_GATES #:
METAL_GATES: Set[str] = set() #:
OVERWORLD_GATES = WOOD_GATES | METAL_GATES #:
NETHER_GATES = FUNGUS_GATES | METAL_GATES #:
END_GATES = METAL_GATES #:
GATES = OVERWORLD_GATES | NETHER_GATES | END_GATES #:

WOOD_TRAPDOORS = variate(WOOD_TYPES, "trapdoor") #:
FUNGUS_TRAPDOORS = variate(FUNGUS_TYPES, "trapdoor") #:
WOODY_TRAPDOORS = WOOD_TRAPDOORS | FUNGUS_TRAPDOORS #:
METAL_TRAPDOORS = {"minecraft:iron_trapdoor", } #:
OVERWORLD_TRAPDOORS = WOOD_TRAPDOORS | METAL_TRAPDOORS #:
NETHER_TRAPDOORS = FUNGUS_TRAPDOORS | METAL_TRAPDOORS #:
END_TRAPDOORS = METAL_TRAPDOORS #:
TRAPDOORS = OVERWORLD_TRAPDOORS | NETHER_TRAPDOORS | END_TRAPDOORS #:

WOOD_ENTRYWAYS = WOOD_DOORS | WOOD_GATES | WOOD_TRAPDOORS #:
FUNGUS_ENTRYWAYS = FUNGUS_DOORS | FUNGUS_GATES | FUNGUS_TRAPDOORS #:
WOODY_ENTRYWAYS = WOODY_DOORS | WOODY_GATES | WOODY_TRAPDOORS #:
METAL_ENTRYWAYS = METAL_DOORS | METAL_GATES | METAL_TRAPDOORS #:

OVERWORLD_ENTRYWAYS = OVERWORLD_DOORS | OVERWORLD_GATES | OVERWORLD_TRAPDOORS #:
NETHER_ENTRYWAYS = NETHER_DOORS | NETHER_GATES | NETHER_TRAPDOORS #:
END_ENTRYWAYS = END_DOORS | END_GATES | END_TRAPDOORS #:
ENTRYWAYS = OVERWORLD_ENTRYWAYS | NETHER_ENTRYWAYS | END_ENTRYWAYS #:

# structural
WOOD_PLANKS = variate(WOOD_TYPES, "planks") #:
FUNGUS_PLANKS = variate(FUNGUS_TYPES, "planks") #:
PLANKS = WOOD_PLANKS | FUNGUS_PLANKS #:

POLISHED_IGNEOUS_BLOCKS = variate(IGNEOUS_TYPES, "polished", isPrefix=True) #:

STONE_BRICKS = {"minecraft:smooth_stone", } \
               | variate(STONE_BRICK_TYPES, "stone_bricks") #:
POLISHED_BLACKSTONE_BRICKS = \
    variate(POLISHED_BLACKSTONE_BRICK_TYPES, "polished_blackstone_bricks") #:
NETHER_BRICK_BRICKS = variate(NETHER_BRICK_TYPES, "nether_bricks") #:

OVERWORLD_BRICKS = {"minecraft:bricks", "minecraft:prismarine_bricks"} \
                   | STONE_BRICKS #:
NETHER_DIMENSION_BRICKS = POLISHED_BLACKSTONE_BRICKS | NETHER_BRICK_BRICKS #:
END_BRICKS = {"minecraft:end_stone_bricks", } #:
BRICKS = OVERWORLD_BRICKS | NETHER_DIMENSION_BRICKS | END_BRICKS #:

CONCRETES = variate(DYE_COLORS, "concrete") #:
CONCRETE_POWDERS = variate(DYE_COLORS, "concrete_powder") #:

REGULAR_SANDSTONES = variate(SANDSTONE_TYPES, "sandstone") #:
RED_SANDSTONES = variate(SANDSTONE_TYPES, "red_sandstone") #:
SANDSTONES = REGULAR_SANDSTONES | RED_SANDSTONES #:

PRISMARINE_BLOCKS = {"minecraft:prismarine_bricks", } \
                    | variate(PRISMARINE_TYPES, "prismarine") #:

POLISHED_BLACKSTONES = {"minecraft:polished_blackstone",
                        "minecraft:chiseled_polished_blackstone"} \
                       | POLISHED_BLACKSTONE_BRICKS #:
QUARTZES = {"minecraft:smooth_quartz", "minecraft:chiseled_quartz_block",
            "minecraft:quartz_block", "minecraft:quartz_bricks",
            "minecraft:quartz_pillar", } #:
PURPUR_BLOCKS = variate(PURPUR_TYPES, "purpur", isPrefix=True) #:

SHULKER_BOXES = variate({None, } | set(DYE_COLORS), "shulker_box") #:
DYEABLE_BLOCKS = WOOLS | CARPETS | BEDS | BANNERS | STAINED_GLASSES \
                 | TERRACOTTAS | GLAZED_TERRACOTTAS | CONCRETES | CONCRETE_POWDERS \
                 | SHULKER_BOXES - {"minecraft:shulker_box", } #:
ORNAMENTAL_BLOCKS = {"minecraft:bookshelf", "minecraft:hay_block",
                     "minecraft:chain", "minecraft:iron_bars",
                     "minecraft:dried_kelp_block", } \
                    | DYEABLE_BLOCKS | GLASSES | SLABS | STAIRS | BARRIERS #:

OVERWORLD_STRUCTURE_BLOCKS = ORNAMENTAL_BLOCKS | WOOD_PLANKS | SANDSTONES \
                             | OVERWORLD_BRICKS | POLISHED_IGNEOUS_BLOCKS | PRISMARINE_BLOCKS #:
NETHER_STRUCTURE_BLOCKS = FUNGUS_PLANKS | NETHER_DIMENSION_BRICKS \
                          | POLISHED_BLACKSTONES | QUARTZES #:
END_STRUCTURE_BLOCKS = END_BRICKS | PURPUR_BLOCKS #:
STRUCTURE_BLOCKS = OVERWORLD_STRUCTURE_BLOCKS | NETHER_STRUCTURE_BLOCKS \
                   | END_STRUCTURE_BLOCKS #:

# lights
TORCHES = variate(FIRE_TYPES, "torch") #:
LANTERNS = variate(FIRE_TYPES, "lantern") #:
BLOCK_LIGHTS = {"minecraft:glowstone", "minecraft:jack_o_lantern",
                "minecraft:sea_lantern", } #:
LIGHTS = {"minecraft:end_rod"} | TORCHES | LANTERNS | BLOCK_LIGHTS #:

# interactable
WOOD_FLOOR_SIGNS = variate(WOOD_TYPES, "sign") #:
FUNGUS_FLOOR_SIGNS = variate(FUNGUS_TYPES, "sign") #:
WOODY_FLOOR_SIGNS = WOOD_FLOOR_SIGNS | FUNGUS_FLOOR_SIGNS #:
FLOOR_SIGNS = WOODY_FLOOR_SIGNS #:
WOOD_WALL_SIGNS = variate(WOOD_TYPES, "wall_sign") #:
FUNGUS_WALL_SIGNS = variate(FUNGUS_TYPES, "wall_sign") #:
WOODY_WALL_SIGNS = WOOD_WALL_SIGNS | FUNGUS_WALL_SIGNS #:
WALL_SIGNS = WOODY_WALL_SIGNS #:
WOOD_SIGNS = WOOD_FLOOR_SIGNS | WOOD_WALL_SIGNS #:
FUNGUS_SIGNS = FUNGUS_FLOOR_SIGNS | FUNGUS_WALL_SIGNS #:
SIGNS = FLOOR_SIGNS | WALL_SIGNS #:

# 1.17 NOTE: CAULDRONS = variate(CAULDRON_TYPES, "cauldron")
CAULDRONS = {"minecraft:cauldron", } #:
FURNACES = {"minecraft:blast_furnace", "minecraft:furnace",
            "minecraft:smoker", } #:
ANVILS = variate(ANVIL_TYPES, "anvil") #:
JOB_SITE_BLOCKS = {"minecraft:barrel", "minecraft:blast_furnace",
                   "minecraft:brewing_stand", "minecraft:cartography_table",
                   "minecraft:composter",
                   "minecraft:fletching_table", "minecraft:grindstone",
                   "minecraft:lectern", "minecraft:loom",
                   "minecraft:smithing_table", "minecraft:stonecutter", } \
                  | CAULDRONS #:

CHESTS = variate(CHEST_TYPES, "chest") #:
UI_BLOCKS = {"minecraft:beacon",
             "minecraft:crafting_table", "minecraft:enchanting_table", } \
            | SIGNS | FURNACES | ANVILS | JOB_SITE_BLOCKS | CHESTS | SHULKER_BOXES #:

CAMPFIRES = variate(FIRE_TYPES, "campfire") #:

OVERWORLD_PORTALS: Set[str] = set() #:
OVERWORLD_PORTAL_BLOCKS = OVERWORLD_PORTALS #:
NETHER_PORTALS = {"minecraft:nether_portal", } #:
NETHER_PORTAL_BLOCKS = NETHER_PORTALS | OBSIDIAN_BLOCKS #:
END_PORTALS = {"minecraft:end_gateway", "minecraft:end_portal", } #:
END_PORTAL_BLOCKS = {"minecraft:end_portal_frame", "minecraft:bedrock", } \
                    | END_PORTALS #:
PORTALS = OVERWORLD_PORTALS | NETHER_PORTALS | END_PORTALS #:
PORTAL_BLOCKS = OVERWORLD_PORTAL_BLOCKS | NETHER_PORTAL_BLOCKS \
                | END_PORTAL_BLOCKS #:

WOOD_BUTTONS = variate(WOOD_TYPES, "button") #:
FUNGUS_BUTTONS = variate(FUNGUS_TYPES, "button") #:
WOODY_BUTTONS = WOOD_BUTTONS | FUNGUS_BUTTONS #:
BUTTONS = {"minecraft:stone_button", "minecraft:polished_blackstone_button"} \
          | WOODY_BUTTONS #:
SWITCHES = {"minecraft:lever", } | BUTTONS #:

# interaction has an immediate effect (no UI)
FLOWER_POTS = {"minecraft:flower_pot", } \
              | variate(POTTED_PLANT_TYPES, "potted", isPrefix=True) #:
USABLE_BLOCKS = {"minecraft:bell", "minecraft:cake", "minecraft:conduit",
                 "minecraft:jukebox", "minecraft:lodestone",
                 "minecraft:respawn_anchor", "minecraft:spawner",
                 "minecraft:tnt", } \
                | BEE_NESTS | CAMPFIRES | CAULDRONS | SWITCHES | FLOWER_POTS #:

INTERACTABLE_BLOCKS = USABLE_BLOCKS | UI_BLOCKS #:

SENSOR_RAILS = variate(SENSOR_RAIL_TYPES, "rail") #:
ACTUATOR_RAILS = variate(ACTUATOR_RAIL_TYPES, "rail") #:
RAILS = {"minecraft:rail", } | SENSOR_RAILS | ACTUATOR_RAILS #:

WOOD_PRESSURE_PLATES = variate(WOOD_TYPES, "pressure_plate") #:
FUNGUS_PRESSURE_PLATES = variate(FUNGUS_TYPES, "pressure_plate") #:
WOODY_PRESSURE_PLATES = WOOD_PRESSURE_PLATES | FUNGUS_PRESSURE_PLATES #:
STONE_PRESSURE_PLATES = {"minecraft:stone_pressure_plate",
                         "minecraft:polished_blackstone_pressure_plate"} #:
WEIGHTED_PRESSURE_PLATES = variate(WEIGHTED_PRESSURE_PLATE_TYPES,
                                   "weighted_pressure_plate") #:
PRESSURE_PLATES = WOODY_PRESSURE_PLATES | STONE_PRESSURE_PLATES \
                  | WEIGHTED_PRESSURE_PLATES #:

SENSORS = {"minecraft:daylight_detector", "minecraft:target",
           "minecraft:observer", "minecraft:trapped_chest",
           "minecraft:tripwire_hook"} \
          | SENSOR_RAILS | SWITCHES | PRESSURE_PLATES #:

PISTON_BODIES = variate(PISTON_TYPES, "piston") #:
PISTONS = {"minecraft:piston_head", "minecraft:moving_piston", } \
          | PISTON_BODIES #:

COMMAND_BLOCKS = variate(COMMAND_BLOCK_TYPES, "command_block") #:
COMMAND_ONLY_ACTUATORS = {"minecraft:structure_block", "minecraft:jigsaw"} \
                         | COMMAND_BLOCKS #:
ACTUATORS = {"minecraft:bell", "minecraft:dispenser", "minecraft:dragon_head",
             "minecraft:dropper", "minecraft:hopper", "minecraft:note_block",
             "minecraft:tnt", "minecraft:redstone_lamp"} \
            | PISTONS | ENTRYWAYS | ACTUATOR_RAILS | COMMAND_ONLY_ACTUATORS #:
WIRING = {"minecraft:redstone_wire", "minecraft:redstone_torch",
          "minecraft:repeater", "minecraft:comparator"} #:
REDSTONE = {"minecraft:tripwire", } | SENSORS | ACTUATORS | WIRING #:

SLIMELIKES = {"minecraft:slime_block", "minecraft:honey_block", } #:

FLOOR_SKULLS = variate(SKULL_TYPES, "skull") #:
WALL_SKULLS = variate(SKULL_TYPES, "wall_skull") #:
SKULLS = FLOOR_SKULLS | WALL_SKULLS #:
FLOOR_HEADS = variate(HEAD_TYPES, "head") #:
WALL_HEADS = variate(HEAD_TYPES, "wall_head") #:
HEADS = FLOOR_HEADS | WALL_HEADS #:
FLOOR_CRANIUMS = FLOOR_SKULLS | FLOOR_HEADS #:
WALL_CRANIUMS = WALL_SKULLS | WALL_HEADS #:
CRANIUMS = FLOOR_CRANIUMS | WALL_CRANIUMS #:

CREATIVE_ONLY = {"minecraft:player_head", "minecraft:player_wall_head",
                 "minecraft:petrified_oak_slab", } #:
COMMANDS_ONLY = {"minecraft:barrier", } #:

FALLING_BLOCKS = {"minecraft:dragon_egg", } \
                 | ANVILS | CONCRETE_POWDERS | GRANULARS #:

WOOD_BLOCKS = TRUNKS | WOOD_BUTTONS | WOOD_ENTRYWAYS | WOOD_FENCES \
              | WOOD_PLANKS | WOOD_PRESSURE_PLATES | WOOD_SLABS | WOOD_STAIRS \
              | WOOD_SIGNS #:
FUNGUS_BLOCKS = FUNGUS_GROWTH_BLOCKS | FUNGUS_BUTTONS | FUNGUS_ENTRYWAYS \
                | FUNGUS_FENCES | FUNGUS_PLANKS | FUNGUS_PRESSURE_PLATES | FUNGUS_SLABS \
                | FUNGUS_STAIRS | FUNGUS_SIGNS #:
WOODY_BLOCKS = WOOD_BLOCKS | FUNGUS_BLOCKS #:

LAVA_FLAMMABLE = {"minecraft:composter", "minecraft:tnt",
                  "minecraft:bookshelf", "minecraft:lectern",
                  "minecraft:dead_bush"} \
                 | WOOD_BLOCKS | BEE_NESTS | FOLIAGE | WOOLS | CARPETS | BAMBOOS \
                 | TALL_FLOWERS | TRUE_GRASSES - {"minecraft:grass_block"} #:
FLAMMABLE = {"minecraft:coal_block", "minecraft:target",
             "minecraft:dried_kelp_block", "minecraft:hay_block",
             "minecraft:scaffolding", "minecraft:"} \
            | LAVA_FLAMMABLE #:

CLIMBABLE = {"minecraft:ladder", "minecraft:scaffolding", } | VINES #:

INVISIBLE_BLOCKS = {"minecraft:structure_void", "minecraft:barrier", } | AIRS #:

BLOCKS = ORES | MINERAL_BLOCKS | SOILS | STONES | FLUIDS | LIQUID_BASED \
         | FIRES | LIFE | GLASSES | SLABS | STAIRS | BARRIERS | ENTRYWAYS \
         | STRUCTURE_BLOCKS | LIGHTS | PORTAL_BLOCKS | INTERACTABLE_BLOCKS \
         | REDSTONE | SLIMELIKES | CLIMBABLE \
         | CRANIUMS | CREATIVE_ONLY | COMMANDS_ONLY | INVISIBLE_BLOCKS #:

INVENTORY_BLOCKS = {"minecraft:barrel",
                    "minecraft:hopper", } | CHESTS | SHULKER_BOXES #:

# ================================================= grouped by structure
# underwater
COLD_OCEAN_RUIN_BLOCKS = {"minecraft:gravel", "minecraft:sand",
                          "minecraft:prismarine", "minecraft:polished_granite",
                          "minecraft:sea_lantern", "minecraft:magma_block",
                          "minecraft:chest",
                          "minecraft:purple_glazed_terracotta",
                          "minecraft:bricks",
                          "minecraft:spruce_planks",
                          "minecraft:dark_oak_planks",
                          "minecraft:obsidian", } \
                         | STONE_BRICKS #:
WARM_OCEAN_RUIN_BLOCKS = {"minecraft:sand", "minecraft:gravel",
                          "minecraft:polished_granite",
                          "minecraft:polished_diorite",
                          "minecraft:sea_lantern", "minecraft:magma_block",
                          "minecraft:chest",
                          "minecraft:light_blue_terracotta",
                          "minecraft:sandstone_stairs", } \
                         | REGULAR_SANDSTONES #:
OCEAN_RUINS_BLOCKS = WARM_OCEAN_RUIN_BLOCKS | COLD_OCEAN_RUIN_BLOCKS #:
SHIPWRECK_BLOCKS = {"minecraft:chest", } \
                   | BARKED_LOGS | WOOD_PLANKS | WOOD_FENCES | WOOD_SLABS | WOOD_STAIRS \
                   | WOOD_TRAPDOORS | WOOD_DOORS #:
OCEAN_MONUMENT_BLOCKS = {"minecraft:gold_block", "minecraft:sea_lantern",
                         "minecraft:wet_sponge"} \
                        | KELPS | SEAGRASSES | PRISMARINE_BLOCKS | WATERS #:
ICEBERG_BLOCKS = ICE_BLOCKS | SNOWS - {"minecraft:frosted_ice", } #:

# underground
REGULAR_MINESHAFT_BLOCKS = {"minecraft:rail",
                            "minecraft:torch", "minecraft:cobweb",
                            "minecraft:spawner", "minecraft:chain",
                            "minecraft:oak_log", "minecraft:oak_fence",
                            "minecraft:oak_planks", } #:
BADLANDS_MINESHAFT_BLOCKS = {"minecraft:rail",
                             "minecraft:torch", "minecraft:cobweb",
                             "minecraft:spawner", "minecraft:chain",
                             "minecraft:dark_oak_log",
                             "minecraft:dark_oak_fence",
                             "minecraft:dark_oak_planks", } #:
MINESHAFT_BLOCKS = REGULAR_MINESHAFT_BLOCKS | BADLANDS_MINESHAFT_BLOCKS #:
STRONGHOLD_BLOCKS = {"minecraft:spawner", "minecraft:end_portal_frame",
                     "minecraft:end_portal_block", "minecraft:torch",
                     "minecraft:oak_fence", "minecraft:chest",
                     "minecraft:stone_brick_slab", "minecraft:cobblestone",
                     "minecraft:stone_brick_stairs", "minecraft:oak_planks",
                     "minecraft:ladder", "minecraft:smooth_stone_slab",
                     "minecraft:stone_button", "minecraft:iron_door",
                     "minecraft:oak_door", "minecraft:cobblestone_stairs",
                     "minecraft:bookshelf", "minecraft:cobweb", } \
                    | STONE_BRICKS | INFESTED | WATERS | LAVAS #:
BURIED_TREASURE_BLOCKS = {"minecraft:chest", } #:
DUNGEON_BLOCKS = {"minecraft:chest", "mineraft:spawner", } | COBBLESTONES #:
DESERT_WELL_BLOCKS = {"minecraft:sandstone", "minecraft:sandstone_slab", } \
                     | WATERS #:
FOREST_ROCK_BLOCKS = {"minecraft:mossy_cobblestone", } #:
OVERWORLD_FOSSIL_BLOCKS = {"minecraft:bone_block", "minecraft:coal_ore",
                           "minecraft:diamond_ore", } #:

# overground
DESERT_PYRAMID_BLOCKS = {"minecraft:blue_terracotta", "minecraft:chest",
                         "minecraft:orange_terracotta",
                         "minecraft:sandstone_slab",
                         "minecraft:sandstone_stairs",
                         "minecraft:stone_pressure_plate",
                         "minecraft:tnt", } \
                        | REGULAR_SANDSTONES #:
IGLOO_LAB_BLOCKS = {"minecraft:oak_trapdoor", "minecraft:ladder",
                    "minecraft:torch", "minecraft:stone", "minecraft:chest",
                    "minecraft:red_carpet", "minecraft:polished_andesite",
                    "minecraft:cobweb", "minecraft:iron_bars",
                    "minecraft:oak_wall_sign", "minecraft:cauldron",
                    "minecraft:spruce_stairs", "minecraft:spruce_slab",
                    "minecraft:brewing_stand", "minecraft:potted_cactus", } \
                   | STONE_BRICKS | INFESTED_STONE_BRICKS #:
IGLOO_BLOCKS = {"minecraft:snow",
                "minecraft:white_carpet", "minecraft:light_gray_carpet",
                "minecraft:ice", "minecraft:packed_ice",
                "minecraft:redstone_torch", "minecraft:furnace",
                "minecraft:red_bed", "minecraft:crafting_table", } \
               | IGLOO_LAB_BLOCKS #:
JUNGLE_TEMPLE_BLOCKS = {"minecraft:chest", "minecraft:chiseled_stone_bricks",
                        "minecraft:cobblestone_stairs", "minecraft:dispenser",
                        "minecraft:lever", "minecraft:repeater",
                        "minecraft:redstone_wire", "minecraft:sticky_piston",
                        "minecraft:tripwire", "minecraft:tripwire_hook",
                        "minecraft:vines", } \
                       | COBBLESTONES #:
PILLAGER_WATCHTOWER = {"minecraft:dark_oak_planks", "minecraft:dark_oak_log",
                       "minecraft:dark_oak_stairs", "minecraft:dark_oak_slab",
                       "minecraft:dark_oak_fence",
                       "minecraft:cobblestone", "minecraft:cobblestone_stairs",
                       "minecraft:cobblestone_slab",
                       "minecraft:cobblestone_wall",
                       "minecraft:torch", "minecraft:chest",
                       "minecraft:birch_planks",
                       "minecraft:white_wall_banner", } #:
PILLAGER_CAGE = {"minecraft:dark_oak_fence", "minecraft:dark_oak_log",
                 "minecraft:dark_oak_stairs", "minecraft:dark_oak_slab", } #:
PILLAGER_LOGS = {"minecraft:dark_oak_log", } #:
PILLAGER_TARGETS = {"minecraft:dark_oak_fence", "minecraft:carved_pumpkin",
                    "minecraft:hay_block", } #:
PILLAGER_TENT = {"minecraft:white_wool", "minecraft:dark_oak_fence",
                 "minecraft:pumpkin", "minecraft:crafting_table", } #:
PILLAGER_OUTPOST_BLOCKS = PILLAGER_WATCHTOWER | PILLAGER_CAGE | PILLAGER_LOGS \
                          | PILLAGER_TARGETS | PILLAGER_TENT #:
SWAMP_HUT = {"minecraft:crafting_table", "minecraft:potted_red_mushroom",
             "minecraft:oak_fence", "minecraft:oak_log",
             "minecraft:spruce_planks", "minecraft:spruce_stairs", } \
            | CAULDRONS #:

PLAINS_VILLAGE_ACCESSORY = {"minecraft:oak_trapdoor", "minecraft:dandelion", "minecraft:poppy", "minecraft:oxeye_daisy", "minecraft:grass_block"} #:
PLAINS_VILLAGE_ANIMAL_PEN = {"minecraft:torch", "minecraft:dandelion", "minecraft:hay_block", "minecraft:oak_fence", "minecraft:poppy", "minecraft:grass_block", "minecraft:oak_fence_gate"} | WATERS #:
PLAINS_VILLAGE_ARMORER_HOUSE = {"minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:blast_furnace", "minecraft:torch", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:oak_door", "minecraft:smooth_stone",
                                "minecraft:brick", "minecraft:oak_stairs", "minecraft:oak_log", "minecraft:oak_slab"} #:
PLAINS_VILLAGE_BIG_HOUSE = {"minecraft:cobblestone_stairs", "minecraft:white_bed", "minecraft:torch", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:oak_door", "minecraft:oak_planks", "minecraft:chest", "minecraft:oak_log"} #:
PLAINS_VILLAGE_BUTCHER_SHOP = {"minecraft:cobblestone_wall", "minecraft:smooth_stone_slab", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:hay_block", "minecraft:grass_block", "minecraft:oak_door",
                               "minecraft:oak_pressure_plate", "minecraft:oak_stairs", "minecraft:oak_fence", "minecraft:smoker", "minecraft:oak_planks", "minecraft:oak_log", "potted_dandelion"} #:
PLAINS_VILLAGE_CARTOGRAPHER = {"minecraft:cartography_table", "minecraft:oak_pressure_plate", "minecraft:yellow_carpet", "minecraft:oak_stairs", "minecraft:chest", "minecraft:oak_log", "minecraft:oak_slab", "minecraft:torch", "minecraft:dandelion",
                               "minecraft:oak_fence", "minecraft:dirt_path", "minecraft:oak_trapdoor", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:oak_door", "minecraft:white_carpet", "minecraft:oak_planks", "minecraft:poppy",
                               "minecraft:grass_block"} #:
PLAINS_VILLAGE_FISHER_COTTAGE = {"minecraft:cobblestone_stairs", "minecraft:oak_trapdoor", "minecraft:torch", "minecraft:crafting_table", "minecraft:dirt", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:oak_door", "minecraft:oak_stairs",
                                 "minecraft:oak_fence", "minecraft:oak_planks", "minecraft:barrel", "minecraft:chest", "minecraft:oak_log", "minecraft:grass_block", "minecraft:oak_slab"} | WATERS #:
PLAINS_VILLAGE_FLETCHER_HOUSE = {"minecraft:grass_path", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:fletching_table", "minecraft:oak_door", "minecraft:grass_block", "minecraft:yellow_wool",
                                 "minecraft:oak_stairs", "minecraft:oak_fence", "minecraft:oak_planks", "minecraft:white_wool", "minecraft:oak_log", "potted_dandelion", "minecraft:oak_slab", "minecraft:yellow_carpet"} #:
PLAINS_VILLAGE_FOUNTAIN = {"minecraft:grass_path", "minecraft:cobblestone", "minecraft:bell", "minecraft:torch"} | WATERS #:
PLAINS_VILLAGE_LAMP = {"minecraft:torch", "minecraft:stripped_oak_wood", "minecraft:oak_fence"} #:
PLAINS_VILLAGE_FARM = {"minecraft:farmland", "minecraft:dirt", "minecraft:composter", "minecraft:oak_log", "minecraft:wheat", "minecraft:water"} | WATERS #:
PLAINS_VILLAGE_LIBRARY = {"minecraft:cobblestone_stairs", "minecraft:dirt_path", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:bookshelf", "minecraft:lectern", "minecraft:oak_door", "minecraft:oak_stairs",
                          "minecraft:oak_fence", "minecraft:wall_torch", "minecraft:oak_planks", "minecraft:oak_log", "minecraft:grass_block"} #:
PLAINS_VILLAGE_MASONS_HOUSE = {"minecraft:cobblestone_stairs", "minecraft:oak_trapdoor", "minecraft:torch", "minecraft:terracotta", "minecraft:stonecutter", "minecraft:cobblestone", "minecraft:dandelion", "minecraft:glass_pane",
                               "minecraft:white_terracotta", "minecraft:clay", "minecraft:oak_door", "minecraft:oak_stairs", "minecraft:oak_fence", "minecraft:oak_planks", "minecraft:oak_log", "minecraft:grass_block"} #:
PLAINS_VILLAGE_HOUSE = {"minecraft:stripped_oak_log", "minecraft:oak_pressure_plate", "minecraft:yellow_bed", "minecraft:white_terracotta", "minecraft:ladder", "minecraft:green_carpet", "minecraft:oak_stairs", "minecraft:chest", "minecraft:oak_log",
                        "minecraft:oak_slab", "minecraft:cobblestone_stairs", "minecraft:torch", "minecraft:farmland", "minecraft:oak_fence", "minecraft:oak_trapdoor", "minecraft:white_bed", "minecraft:cobblestone", "minecraft:glass_pane",
                        "minecraft:oak_door", "minecraft:oak_planks", "minecraft:poppy", "minecraft:grass_block"} | WATERS #:
PLAINS_VILLAGE_MEETING_POINT = {"minecraft:cobblestone_stairs", "minecraft:grass_path", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:yellow_wool", "minecraft:oak_leaves", "minecraft:oak_fence", "minecraft:oak_planks",
                                "minecraft:white_wool", "minecraft:oak_log", "minecraft:grass_block", "minecraft:bell", "minecraft:oak_slab"} | WATERS #:
PLAINS_VILLAGE_SHEPHERD_HOUSE = {"minecraft:torch", "minecraft:dirt_path", "minecraft:yellow_wool", "minecraft:glass_pane", "minecraft:loom", "minecraft:oak_door", "minecraft:white_carpet", "minecraft:oak_stairs", "minecraft:oak_fence",
                                 "minecraft:oak_planks", "minecraft:white_wool", "minecraft:oak_log", "minecraft:grass_block", "minecraft:oak_slab", "minecraft:yellow_carpet"} #:
PLAINS_VILLAGE_STABLE = {"minecraft:cobblestone_stairs", "minecraft:grass_path", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:white_terracotta", "minecraft:hay_block", "minecraft:oak_door",
                         "minecraft:oak_stairs", "minecraft:oak_fence", "minecraft:oak_planks", "minecraft:water", "minecraft:oak_log", "minecraft:grass_block", "minecraft:oak_slab"} | WATERS #:
PLAINS_VILLAGE_TANNERY = {"minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:torch", "minecraft:cauldron", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:oak_door", "minecraft:smooth_stone", "minecraft:oak_stairs",
                          "minecraft:oak_fence", "minecraft:oak_planks", "minecraft:chest", "minecraft:oak_log", "minecraft:oak_slab"} #:
PLAINS_VILLAGE_TEMPLE = {"minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:torch", "minecraft:cobblestone", "minecraft:brewing_stand", "minecraft:oak_door", "minecraft:white_terracotta", "minecraft:cobblestone_slab",
                         "minecraft:oak_stairs", "minecraft:ladder", "minecraft:oak_planks", "minecraft:white_stained_glass_pane", "minecraft:oak_log", "minecraft:yellow_stained_glass_pane"} #:
PLAINS_VILLAGE_TOOL_SMITH_HOUSE = {"minecraft:cobblestone_stairs", "minecraft:torch", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:oak_door", "minecraft:oak_stairs", "minecraft:oak_planks", "minecraft:oak_log",
                                   "minecraft:smithing_table"} #:
PLAINS_VILLAGE_WEAPONSMITH = {"minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:torch", "minecraft:lava", "minecraft:cobblestone", "minecraft:chest", "minecraft:glass_pane", "minecraft:oak_door", "minecraft:oak_pressure_plate",
                              "minecraft:grindstone", "minecraft:iron_bars", "minecraft:oak_stairs", "minecraft:oak_fence", "minecraft:oak_planks", "minecraft:furnace", "minecraft:oak_log", "minecraft:smooth_stone_slab"} #:
PLAINS_VILLAGE_BLOCKS = PLAINS_VILLAGE_ACCESSORY | PLAINS_VILLAGE_ANIMAL_PEN | PLAINS_VILLAGE_ARMORER_HOUSE | PLAINS_VILLAGE_BIG_HOUSE | PLAINS_VILLAGE_BUTCHER_SHOP | PLAINS_VILLAGE_CARTOGRAPHER | PLAINS_VILLAGE_FISHER_COTTAGE | PLAINS_VILLAGE_FLETCHER_HOUSE | PLAINS_VILLAGE_FOUNTAIN | PLAINS_VILLAGE_LAMP | PLAINS_VILLAGE_FARM | PLAINS_VILLAGE_LIBRARY | PLAINS_VILLAGE_MASONS_HOUSE | PLAINS_VILLAGE_HOUSE | PLAINS_VILLAGE_MEETING_POINT | PLAINS_VILLAGE_SHEPHERD_HOUSE | PLAINS_VILLAGE_STABLE | PLAINS_VILLAGE_TANNERY | PLAINS_VILLAGE_TEMPLE | PLAINS_VILLAGE_TOOL_SMITH_HOUSE | PLAINS_VILLAGE_WEAPONSMITH #:
DESERTPLAINS_VILLAGE_ANIMAL_PEN = {"minecraft:grass_block", "minecraft:jungle_fence_gate", "minecraft:hay_block", "minecraft:sandstone_wall"} #:
DESERTPLAINS_VILLAGE_BLOCKS = DESERTPLAINS_VILLAGE_ANIMAL_PEN #:
DESERT_VILLAGE_ANIMAL_PEN = {"minecraft:jungle_fence_gate", "minecraft:cut_sandstone", "minecraft:smooth_sandstone_slab", "minecraft:grass_block", "minecraft:smooth_sandstone_stairs", "minecraft:water", "minecraft:sandstone_wall"} | WATERS #:
DESERT_VILLAGE_ARMORER = {"minecraft:blast_furnace", "minecraft:torch", "minecraft:granite_wall", "minecraft:jungle_fence", "minecraft:sand", "minecraft:granite", "minecraft:jungle_door", "minecraft:smooth_sandstone", "minecraft:cut_sandstone",
                          "minecraft:smooth_sandstone_slab", "minecraft:stone_button", "minecraft:smooth_sandstone_stairs", "minecraft:granite_stairs"} #:
DESERT_VILLAGE_BUTCHER_SHOP = {"minecraft:smooth_stone_slab", "minecraft:torch", "minecraft:terracotta", "minecraft:jungle_door", "minecraft:smooth_sandstone", "minecraft:cut_sandstone", "minecraft:smooth_sandstone_slab", "minecraft:smoker",
                               "minecraft:grass_block", "minecraft:smooth_sandstone_stairs", "minecraft:sandstone_wall"} #:
DESERT_VILLAGE_CARTOGRAPHER = {"minecraft:torch", "minecraft:cartography_table", "minecraft:jungle_door", "minecraft:smooth_sandstone", "potted_cactus", "minecraft:cut_sandstone", "minecraft:smooth_sandstone_slab",
                               "minecraft:smooth_sandstone_stairs"} #:
DESERT_VILLAGE_FARM = {"minecraft:farmland", "minecraft:sand", "minecraft:composter", "minecraft:smooth_sandstone", "minecraft:hay_block", "minecraft:wheat", "minecraft:cut_sandstone", "minecraft:jungle_trapdoor", "minecraft:smooth_sandstone_stairs",
                       "minecraft:water"} | WATERS #:
DESERT_VILLAGE_FISHER = {"minecraft:torch", "minecraft:sand", "minecraft:jungle_door", "minecraft:hay_block", "minecraft:smooth_sandstone", "potted_cactus", "minecraft:cut_sandstone", "minecraft:barrel", "potted_dead_bush",
                         "minecraft:smooth_sandstone_slab"} | WATERS #:
DESERT_VILLAGE_FLETCHER_HOUSE = {"minecraft:torch", "minecraft:sand", "minecraft:fletching_table", "minecraft:jungle_door", "minecraft:smooth_sandstone", "potted_cactus", "minecraft:ladder", "minecraft:cut_sandstone",
                                 "minecraft:smooth_sandstone_slab", "minecraft:smooth_sandstone_stairs", "minecraft:sandstone_wall"} #:
DESERT_VILLAGE_LAMP = {"minecraft:torch", "minecraft:terracotta", "minecraft:cut_sandstone"} #:
DESERT_VILLAGE_LIBRARY = {"minecraft:torch", "minecraft:sand", "minecraft:bookshelf", "minecraft:lectern", "minecraft:jungle_door", "minecraft:smooth_sandstone", "minecraft:white_carpet", "potted_cactus", "minecraft:sandstone",
                          "minecraft:cut_sandstone", "minecraft:sandstone_slab", "minecraft:lime_carpet", "minecraft:smooth_sandstone_stairs"} #:
DESERT_VILLAGE_MASON = {"minecraft:torch", "minecraft:sand", "minecraft:lime_terracotta", "minecraft:stonecutter", "minecraft:jungle_door", "minecraft:smooth_sandstone", "minecraft:clay_ball", "minecraft:cut_sandstone",
                        "minecraft:smooth_sandstone_slab", "minecraft:white_glazed_terracotta", "minecraft:sandstone_wall"} #:
DESERT_VILLAGE_HOUSE = {"minecraft:jungle_button", "minecraft:smooth_sandstone", "potted_cactus", "minecraft:ladder", "minecraft:sea_pickle", "potted_dead_bush", "minecraft:terracotta", "minecraft:sand", "minecraft:green_bed",
                        "minecraft:green_carpet", "minecraft:jungle_door", "minecraft:chest", "minecraft:smooth_sandstone_stairs", "minecraft:sandstone_stairs", "minecraft:torch", "minecraft:cyan_bed", "minecraft:sandstone",
                        "minecraft:sandstone_slab", "minecraft:cut_sandstone", "minecraft:chiseled_sandstone", "minecraft:smooth_sandstone_slab", "minecraft:sandstone_wall", "minecraft:crafting_table", "minecraft:cactus", "minecraft:lime_bed"} #:
DESERT_VILLAGE_MEETING_POINT = {"minecraft:white_glazed_terracotta", "minecraft:torch", "minecraft:terracotta", "minecraft:sand", "minecraft:sandstone_wall", "minecraft:smooth_sandstone_stairs", "minecraft:smooth_sandstone", "minecraft:hay_block",
                                "potted_cactus", "minecraft:cut_sandstone", "minecraft:sandstone_slab", "minecraft:smooth_sandstone_slab", "minecraft:bell", "minecraft:water", "potted_dead_bush"} | WATERS #:
DESERT_VILLAGE_SHEPHERD_HOUSE = {"minecraft:torch", "minecraft:sand", "minecraft:loom", "minecraft:hay_block", "minecraft:jungle_door", "minecraft:smooth_sandstone", "potted_cactus", "minecraft:cut_sandstone", "minecraft:sandstone_slab",
                                 "minecraft:sandstone_wall"} | WATERS #:
DESERT_VILLAGE_TANNERY = {"minecraft:torch", "minecraft:terracotta", "minecraft:sand", "minecraft:jungle_door", "minecraft:smooth_sandstone", "potted_cactus", "minecraft:cut_sandstone", "minecraft:sandstone_slab", "minecraft:smooth_sandstone_slab",
                          "minecraft:smooth_sandstone_stairs", "minecraft:cauldron"} #:
DESERT_VILLAGE_TEMPLE = {"minecraft:white_glazed_terracotta", "minecraft:torch", "minecraft:sand", "minecraft:smooth_sandstone_stairs", "minecraft:lime_glazed_terracotta", "minecraft:brewing_stand", "minecraft:smooth_sandstone", "potted_cactus",
                         "minecraft:sandstone_slab", "minecraft:cut_sandstone", "minecraft:chest", "minecraft:smooth_sandstone_slab"} #:
DESERT_VILLAGE_TOOL_SMITH = {"minecraft:torch", "minecraft:light_blue_glazed_terracotta", "minecraft:terracotta", "minecraft:sand", "minecraft:smooth_sandstone_stairs", "minecraft:jungle_button", "minecraft:jungle_door", "minecraft:smooth_sandstone",
                             "potted_cactus", "minecraft:smooth_sandstone_slab", "minecraft:chest", "minecraft:smithing_table"} #:
DESERT_VILLAGE_WEAPONSMITH = {"minecraft:torch", "minecraft:lava", "minecraft:furnace", "minecraft:cobblestone", "minecraft:smooth_sandstone_stairs", "minecraft:smooth_sandstone", "minecraft:grindstone", "minecraft:iron_bars", "potted_cactus",
                              "minecraft:cut_sandstone", "minecraft:sandstone_slab", "minecraft:chest", "minecraft:smooth_sandstone_slab", "minecraft:sandstone_wall"} #:
DESERT_VILLAGE_BLOCKS = DESERT_VILLAGE_ANIMAL_PEN | DESERT_VILLAGE_ARMORER | DESERT_VILLAGE_BUTCHER_SHOP | DESERT_VILLAGE_CARTOGRAPHER | DESERT_VILLAGE_FARM | DESERT_VILLAGE_FISHER | DESERT_VILLAGE_FLETCHER_HOUSE | DESERT_VILLAGE_LAMP | DESERT_VILLAGE_LIBRARY | DESERT_VILLAGE_MASON | DESERT_VILLAGE_HOUSE | DESERT_VILLAGE_MEETING_POINT | DESERT_VILLAGE_SHEPHERD_HOUSE | DESERT_VILLAGE_TANNERY | DESERT_VILLAGE_TEMPLE | DESERT_VILLAGE_TOOL_SMITH | DESERT_VILLAGE_WEAPONSMITH #:
SNOWY_VILLAGE_ANIMAL_PEN = {"minecraft:spruce_fence_gate", "minecraft:torch", "minecraft:stripped_spruce_log", "minecraft:dirt", "minecraft:snow_block", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:snow", "minecraft:grass_block",
                            "minecraft:water", "minecraft:lantern"} | WATERS #:
SNOWY_VILLAGE_ARMORER_HOUSE = {"minecraft:blast_furnace", "minecraft:cobblestone_wall", "minecraft:torch", "minecraft:stripped_spruce_log", "minecraft:diorite_stairs", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:diorite",
                               "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:stripped_spruce_wood", "minecraft:spruce_planks", "minecraft:snow", "minecraft:spruce_door", "minecraft:diorite_wall", "minecraft:chest",
                               "minecraft:spruce_slab", "minecraft:lantern"} #:
SNOWY_VILLAGE_BUTCHERS_SHOP = {"minecraft:cobblestone_wall", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:snow_block", "minecraft:smooth_stone", "minecraft:grass_block", "minecraft:spruce_stairs",
                               "minecraft:spruce_fence", "minecraft:stripped_spruce_wood", "minecraft:spruce_planks", "minecraft:snow", "minecraft:spruce_door", "minecraft:smoker", "minecraft:smooth_stone_slab", "minecraft:spruce_slab",
                               "minecraft:lantern"} #:
SNOWY_VILLAGE_CARTOGRAPHER_HOUSE = {"minecraft:torch", "minecraft:stripped_spruce_log", "minecraft:cartography_table", "minecraft:glass_pane", "minecraft:spruce_stairs", "minecraft:spruce_planks", "minecraft:snow", "minecraft:spruce_door",
                                    "minecraft:chest", "minecraft:spruce_slab"} #:
SNOWY_VILLAGE_FARM = {"minecraft:farmland", "minecraft:stripped_spruce_log", "minecraft:composter", "minecraft:snow_block", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:stripped_spruce_wood", "minecraft:snow", "minecraft:wheat",
                      "minecraft:water", "minecraft:lantern"} | WATERS #:
SNOWY_VILLAGE_FISHER_COTTAGE = {"minecraft:grass_path", "minecraft:stripped_spruce_log", "minecraft:dirt", "minecraft:glass_pane", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:spruce_planks", "minecraft:snow",
                                "minecraft:spruce_door", "minecraft:barrel", "minecraft:grass_block", "minecraft:spruce_slab", "minecraft:lantern"} | WATERS #:
SNOWY_VILLAGE_FLETCHER_HOUSE = {"minecraft:torch", "minecraft:stripped_spruce_log", "minecraft:glass_pane", "minecraft:fletching_table", "minecraft:blue_carpet", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:stripped_spruce_wood",
                                "minecraft:spruce_planks", "minecraft:snow", "minecraft:spruce_door"} #:
SNOWY_VILLAGE_LAMP_POST = {"minecraft:spruce_fence", "minecraft:snow", "minecraft:lantern"} #:
SNOWY_VILLAGE_LIBRARY = {"minecraft:torch", "minecraft:snow_block", "minecraft:bookshelf", "minecraft:lectern", "minecraft:glass_pane", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:stripped_spruce_wood", "minecraft:spruce_planks",
                         "minecraft:snow", "minecraft:spruce_door", "minecraft:lantern"} #:
SNOWY_VILLAGE_MASONS_HOUSE = {"minecraft:stripped_spruce_log", "minecraft:diorite_stairs", "minecraft:stonecutter", "minecraft:snow_block", "minecraft:red_carpet", "minecraft:glass_pane", "minecraft:diorite", "minecraft:blue_carpet",
                              "minecraft:spruce_stairs", "minecraft:stripped_spruce_wood", "minecraft:spruce_planks", "minecraft:snow", "minecraft:spruce_door", "minecraft:diorite_wall", "minecraft:furnace", "minecraft:spruce_slab",
                              "minecraft:lantern"} #:
SNOWY_VILLAGE_HOUSE = {"minecraft:cobblestone_wall", "minecraft:dirt", "minecraft:stripped_spruce_wood", "minecraft:spruce_door", "minecraft:blue_bed", "minecraft:lantern", "minecraft:stripped_spruce_log", "minecraft:spruce_planks",
                       "minecraft:blue_ice", "minecraft:chest", "minecraft:spruce_slab", "minecraft:torch", "minecraft:light_gray_wool", "minecraft:furnace", "minecraft:white_bed", "minecraft:cobblestone", "minecraft:snow_block",
                       "minecraft:glass_pane", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:packed_ice", "minecraft:snow", "minecraft:red_bed", "minecraft:grass_block"} #:
SNOWY_VILLAGE_MEETING_POINT = {"minecraft:grass_path", "minecraft:torch", "minecraft:dirt", "minecraft:stone_bricks", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:stripped_spruce_wood", "minecraft:packed_ice", "minecraft:snow",
                               "minecraft:spruce_planks", "minecraft:grass_block", "minecraft:bell", "minecraft:lantern"} #:
SNOWY_VILLAGE_SHEPHERDS_HOUSE = {"minecraft:torch", "minecraft:stripped_spruce_log", "minecraft:loom", "minecraft:spruce_fence", "minecraft:spruce_stairs", "minecraft:spruce_planks", "minecraft:spruce_door", "minecraft:snow", "minecraft:chest",
                                 "minecraft:grass_block", "minecraft:spruce_slab", "minecraft:lantern"} #:
SNOWY_VILLAGE_TANNERY = {"minecraft:torch", "minecraft:stripped_spruce_log", "minecraft:furnace", "minecraft:chest", "minecraft:glass_pane", "minecraft:diorite", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:spruce_planks",
                         "minecraft:spruce_door", "minecraft:diorite_wall", "minecraft:spruce_slab", "minecraft:cauldron", "minecraft:lantern"} #:
SNOWY_VILLAGE_TEMPLE = {"minecraft:torch", "minecraft:snow_block", "minecraft:brewing_stand", "minecraft:spruce_stairs", "minecraft:spruce_fence", "minecraft:stripped_spruce_wood", "minecraft:spruce_door", "minecraft:spruce_planks", "minecraft:snow",
                        "minecraft:lantern"} #:
SNOWY_VILLAGE_TOOL_SMITH = {"minecraft:stripped_spruce_log", "minecraft:spruce_stairs", "minecraft:spruce_slab", "minecraft:spruce_planks", "minecraft:snow", "minecraft:spruce_door", "minecraft:smithing_table", "minecraft:lantern"} #:
SNOWY_VILLAGE_WEAPON_SMITH = {"minecraft:torch", "minecraft:stripped_spruce_log", "minecraft:diorite_stairs", "minecraft:lava", "minecraft:chest", "minecraft:grindstone", "minecraft:diorite", "minecraft:spruce_stairs", "minecraft:iron_bars",
                              "minecraft:spruce_planks", "minecraft:snow", "minecraft:spruce_door", "minecraft:diorite_wall", "minecraft:spruce_slab", "minecraft:lantern"} #:
SNOWY_VILLAGE_BLOCKS = SNOWY_VILLAGE_ANIMAL_PEN | SNOWY_VILLAGE_ARMORER_HOUSE | SNOWY_VILLAGE_BUTCHERS_SHOP | SNOWY_VILLAGE_CARTOGRAPHER_HOUSE | SNOWY_VILLAGE_FARM | SNOWY_VILLAGE_FISHER_COTTAGE | SNOWY_VILLAGE_FLETCHER_HOUSE | SNOWY_VILLAGE_LAMP_POST | SNOWY_VILLAGE_LIBRARY | SNOWY_VILLAGE_MASONS_HOUSE | SNOWY_VILLAGE_HOUSE | SNOWY_VILLAGE_MEETING_POINT | SNOWY_VILLAGE_SHEPHERDS_HOUSE | SNOWY_VILLAGE_TANNERY | SNOWY_VILLAGE_TEMPLE | SNOWY_VILLAGE_TOOL_SMITH | SNOWY_VILLAGE_WEAPON_SMITH #:
SAVANNA_VILLAGE_ANIMAL_PEN = {"minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:grass_block", "minecraft:acacia_planks", "minecraft:grass", "minecraft:acacia_fence_gate", "minecraft:acacia_slab",
                              "minecraft:acacia_fence", "minecraft:water", "minecraft:tall_grass"} | WATERS #:
SAVANNA_VILLAGE_ARMORER = {"minecraft:blast_furnace", "minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:dirt_path", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:orange_glazed_terracotta",
                           "minecraft:acacia_planks", "minecraft:grass", "minecraft:grass_block", "minecraft:orange_terracotta"} #:
SAVANNA_VILLAGE_BUTCHERS_SHOP = {"minecraft:cobblestone_wall", "minecraft:acacia_log", "minecraft:dirt", "minecraft:yellow_terracotta", "minecraft:acacia_planks", "minecraft:acacia_stairs", "minecraft:acacia_slab", "minecraft:chest",
                                 "minecraft:smoker", "minecraft:smooth_stone_slab", "minecraft:torch", "minecraft:grass", "minecraft:acacia_door", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:acacia_fence", "minecraft:acacia_wood",
                                 "minecraft:grass_block", "minecraft:orange_terracotta"} #:
SAVANNA_VILLAGE_CARTOGRAPHER = {"minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:cartography_table", "minecraft:acacia_stairs", "minecraft:glass_pane", "minecraft:acacia_planks", "minecraft:brown_wall_banner",
                                "minecraft:acacia_fence", "minecraft:acacia_slab", "minecraft:chest", "minecraft:acacia_wood"} #:
SAVANNA_VILLAGE_FISHER_COTTAGE = {"minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:glass_pane", "minecraft:barrel", "minecraft:acacia_planks", "minecraft:grass",
                                  "minecraft:acacia_fence", "minecraft:acacia_slab", "minecraft:acacia_wood", "minecraft:grass_block"} | WATERS #:
SAVANNA_VILLAGE_FLETCHER_HOUSE = {"minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:dirt_path", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:glass_pane", "minecraft:acacia_pressure_plate",
                                  "minecraft:fletching_table", "minecraft:poppy", "minecraft:yellow_terracotta", "minecraft:acacia_planks", "minecraft:grass", "minecraft:brown_wall_banner", "minecraft:acacia_fence", "minecraft:acacia_slab",
                                  "minecraft:grass_block"} #:
SAVANNA_VILLAGE_LAMP_POST = {"minecraft:torch", "minecraft:acacia_fence"} #:
SAVANNA_VILLAGE_FARM = {"minecraft:farmland", "minecraft:acacia_log", "minecraft:dirt_path", "minecraft:acacia_stairs", "minecraft:composter", "minecraft:dirt", "minecraft:melon", "minecraft:acacia_planks", "minecraft:grass", "minecraft:grass_block",
                        "minecraft:wheat", "minecraft:water", "minecraft:tall_grass"} | WATERS #:
SAVANNA_VILLAGE_LIBRARY = {"minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:acacia_sapling", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:bookshelf", "minecraft:glass_pane", "minecraft:lectern",
                           "minecraft:white_carpet", "minecraft:acacia_planks", "minecraft:grass", "minecraft:orange_carpet", "minecraft:poppy", "minecraft:grass_block", "minecraft:tall_grass", "minecraft:orange_terracotta"} #:
SAVANNA_VILLAGE_MASON = {"minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:yellow_glazed_terracotta", "minecraft:stonecutter", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:glass_pane",
                         "minecraft:acacia_pressure_plate", "minecraft:acacia_planks", "minecraft:grass", "minecraft:clay_ball", "minecraft:acacia_fence", "minecraft:chest", "minecraft:grass_block"} #:
SAVANNA_VILLAGE_HOUSE = {"minecraft:acacia_log", "minecraft:dirt", "minecraft:yellow_terracotta", "minecraft:acacia_planks", "minecraft:water", "minecraft:red_terracotta", "minecraft:acacia_stairs", "minecraft:orange_bed", "minecraft:acacia_slab",
                         "minecraft:chest", "potted_dandelion", "minecraft:farmland", "minecraft:torch", "minecraft:acacia_pressure_plate", "minecraft:grass", "minecraft:brown_wall_banner", "minecraft:dirt_path", "minecraft:grass_path",
                         "minecraft:acacia_door", "minecraft:crafting_table", "minecraft:glass_pane", "minecraft:acacia_fence", "minecraft:red_bed", "minecraft:acacia_wood", "minecraft:grass_block", "minecraft:wheat", "minecraft:tall_grass",
                         "minecraft:orange_terracotta"} | WATERS #:
SAVANNA_VILLAGE_MEETING_POINT = {"minecraft:grass_path", "minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:yellow_terracotta", "minecraft:grass", "minecraft:brown_wall_banner",
                                 "minecraft:acacia_fence", "minecraft:acacia_slab", "minecraft:acacia_wood", "minecraft:grass_block", "minecraft:bell", "minecraft:water", "minecraft:tall_grass", "minecraft:orange_terracotta"} | WATERS #:
SAVANNA_VILLAGE_SHEPHERD = {"minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:dirt_path", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:glass_pane", "minecraft:loom", "minecraft:acacia_planks",
                            "minecraft:grass", "minecraft:acacia_fence", "minecraft:acacia_wood", "minecraft:grass_block", "minecraft:tall_grass"} | WATERS #:
SAVANNA_VILLAGE_TANNERY = {"minecraft:grass_path", "minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:glass_pane", "minecraft:smooth_stone", "minecraft:yellow_terracotta",
                           "minecraft:acacia_planks", "minecraft:grass", "minecraft:brown_wall_banner", "minecraft:acacia_fence", "minecraft:acacia_slab", "minecraft:chest", "minecraft:grass_block", "minecraft:cauldron"} #:
SAVANNA_VILLAGE_TEMPLE = {"minecraft:acacia_log", "minecraft:dirt", "minecraft:brewing_stand", "minecraft:yellow_terracotta", "minecraft:acacia_planks", "minecraft:red_terracotta", "minecraft:acacia_stairs", "minecraft:torch", "minecraft:grass",
                          "minecraft:orange_stained_glass_pane", "minecraft:brown_wall_banner", "minecraft:yellow_stained_glass_pane", "minecraft:grass_path", "minecraft:acacia_door", "minecraft:red_carpet", "minecraft:glass_pane",
                          "minecraft:acacia_wood", "minecraft:grass_block", "minecraft:orange_terracotta"} #:
SAVANNA_VILLAGE_TOOL_SMITH = {"minecraft:grass_path", "minecraft:torch", "minecraft:acacia_log", "minecraft:acacia_door", "minecraft:acacia_stairs", "minecraft:dirt", "minecraft:glass_pane", "minecraft:acacia_planks", "minecraft:grass",
                              "minecraft:brown_wall_banner", "minecraft:acacia_fence", "minecraft:acacia_slab", "minecraft:grass_block", "minecraft:smithing_table"} #:
SAVANNA_VILLAGE_WEAPONSMITH = {"minecraft:acacia_log", "minecraft:dirt", "minecraft:smooth_stone", "minecraft:acacia_planks", "minecraft:iron_bars", "minecraft:acacia_stairs", "minecraft:grindstone", "minecraft:chest", "minecraft:smooth_stone_slab",
                               "minecraft:torch", "minecraft:lava", "minecraft:acacia_pressure_plate", "minecraft:stripped_acacia_log", "minecraft:grass", "minecraft:brown_wall_banner", "minecraft:grass_path", "minecraft:acacia_door",
                               "minecraft:glass_pane", "minecraft:white_carpet", "minecraft:acacia_fence", "minecraft:grass_block"} #:
SAVANNA_VILLAGE_BLOCKS = SAVANNA_VILLAGE_ANIMAL_PEN | SAVANNA_VILLAGE_ARMORER | SAVANNA_VILLAGE_BUTCHERS_SHOP | SAVANNA_VILLAGE_CARTOGRAPHER | SAVANNA_VILLAGE_FISHER_COTTAGE | SAVANNA_VILLAGE_FLETCHER_HOUSE | SAVANNA_VILLAGE_LAMP_POST | SAVANNA_VILLAGE_FARM | SAVANNA_VILLAGE_LIBRARY | SAVANNA_VILLAGE_MASON | SAVANNA_VILLAGE_HOUSE | SAVANNA_VILLAGE_MEETING_POINT | SAVANNA_VILLAGE_SHEPHERD | SAVANNA_VILLAGE_TANNERY | SAVANNA_VILLAGE_TEMPLE | SAVANNA_VILLAGE_TOOL_SMITH | SAVANNA_VILLAGE_WEAPONSMITH #:
TAIGA_VILLAGE_ANIMAL_PEN = {"minecraft:spruce_fence_gate", "minecraft:torch", "minecraft:spruce_fence", "minecraft:spruce_stairs", "minecraft:spruce_planks", "minecraft:spruce_trapdoor", "minecraft:grass_block"} #:
TAIGA_VILLAGE_ARMORER = {"minecraft:blast_furnace", "minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:grass_path", "minecraft:torch", "minecraft:armor_stand", "minecraft:cobblestone", "minecraft:dirt", "minecraft:fern",
                         "minecraft:spruce_log", "minecraft:large_fern", "minecraft:grass_block", "minecraft:campfire"} #:
TAIGA_VILLAGE_ARMORER_HOUSE = {"minecraft:blast_furnace", "minecraft:cobblestone_wall", "minecraft:cobblestone_stairs", "minecraft:grass_path", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane",
                               "minecraft:spruce_log", "minecraft:spruce_door", "minecraft:spruce_planks", "minecraft:poppy", "minecraft:grass_block", "minecraft:spruce_trapdoor"} #:
TAIGA_VILLAGE_BUTCHER_SHOP = {"minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:smooth_stone_slab", "minecraft:torch", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:poppy", "minecraft:fern",
                              "minecraft:spruce_fence", "minecraft:spruce_log", "minecraft:spruce_door", "minecraft:large_fern", "minecraft:smoker", "minecraft:grass_block", "minecraft:campfire", "minecraft:spruce_trapdoor"} #:
TAIGA_VILLAGE_CARTOGRAPHER_HOUSE = {"minecraft:cobblestone_wall", "minecraft:grass_path", "minecraft:torch", "minecraft:cartography_table", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:spruce_fence",
                                    "minecraft:spruce_log", "minecraft:spruce_stairs", "minecraft:ladder", "minecraft:spruce_door", "minecraft:spruce_planks", "minecraft:poppy", "minecraft:chest", "minecraft:grass_block", "minecraft:spruce_trapdoor"} #:
TAIGA_VILLAGE_DECORATION = {"minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:cobblestone", "minecraft:hay_block", "minecraft:spruce_planks", "minecraft:spruce_trapdoor", "minecraft:campfire"} #:
TAIGA_VILLAGE_FISHER_COTTAGE = {"minecraft:grass_path", "minecraft:torch", "minecraft:gravel", "minecraft:sand", "minecraft:cobblestone", "minecraft:dirt", "minecraft:poppy", "minecraft:fern", "minecraft:spruce_fence", "minecraft:spruce_log",
                                "minecraft:spruce_door", "minecraft:clay_ball", "minecraft:spruce_planks", "minecraft:large_fern", "minecraft:barrel", "minecraft:grass_block", "minecraft:spruce_trapdoor"} | WATERS #:
TAIGA_VILLAGE_FLETCHER_HOUSE = {"minecraft:cobblestone_stairs", "minecraft:torch", "minecraft:purple_carpet", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:fletching_table", "minecraft:spruce_fence", "minecraft:spruce_log",
                                "minecraft:spruce_stairs", "minecraft:spruce_door", "minecraft:spruce_planks", "minecraft:poppy", "minecraft:chest", "minecraft:grass_block", "minecraft:spruce_trapdoor"} #:
TAIGA_VILLAGE_LAMP_POST = {"minecraft:cobblestone_wall", "minecraft:torch"} #:
TAIGA_VILLAGE_FARM = {"minecraft:cobblestone_stairs", "minecraft:cobblestone_wall", "minecraft:farmland", "minecraft:grass_path", "minecraft:torch", "minecraft:mossy_cobblestone", "minecraft:dirt", "minecraft:composter", "minecraft:large_fern",
                      "minecraft:cobblestone", "minecraft:fern", "minecraft:pumpkin", "minecraft:spruce_trapdoor", "minecraft:grass_block", "minecraft:wheat", "minecraft:water", "minecraft:pumpkin_stem"} | WATERS #:
TAIGA_VILLAGE_LIBRARY = {"minecraft:cobblestone_wall", "minecraft:purple_carpet", "minecraft:dirt", "minecraft:large_fern", "minecraft:spruce_door", "minecraft:cobblestone_stairs", "minecraft:torch", "minecraft:bookshelf", "minecraft:lectern",
                         "minecraft:spruce_trapdoor", "minecraft:grass_path", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:red_carpet", "minecraft:fern", "minecraft:spruce_log", "minecraft:spruce_stairs", "minecraft:poppy",
                         "minecraft:grass_block"} #:
TAIGA_VILLAGE_MASONS_HOUSE = {"minecraft:cobblestone_stairs", "minecraft:torch", "potted_spruce_sapling", "minecraft:stonecutter", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:spruce_fence", "minecraft:spruce_log",
                              "minecraft:spruce_door", "minecraft:spruce_planks", "minecraft:spruce_trapdoor", "minecraft:grass_block"} #:
TAIGA_VILLAGE_HOUSE = {"minecraft:cobblestone_wall", "minecraft:purple_bed", "minecraft:dirt", "minecraft:spruce_door", "minecraft:blue_bed", "minecraft:spruce_planks", "minecraft:chest", "minecraft:spruce_slab", "minecraft:cobblestone_stairs",
                       "minecraft:torch", "minecraft:spruce_sign", "minecraft:bookshelf", "minecraft:spruce_trapdoor", "minecraft:furnace", "minecraft:spruce_pressure_plate", "minecraft:campfire", "minecraft:grass_path", "minecraft:crafting_table",
                       "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:poppy", "minecraft:fern", "minecraft:spruce_fence", "minecraft:spruce_log", "minecraft:spruce_stairs", "minecraft:large_fern", "minecraft:grass_block"} #:
TAIGA_VILLAGE_MEETING_POINT = {"minecraft:grass_path", "minecraft:torch", "minecraft:mossy_cobblestone", "minecraft:cobblestone", "minecraft:dirt", "minecraft:spruce_fence", "minecraft:spruce_log", "minecraft:spruce_planks",
                               "minecraft:spruce_trapdoor", "minecraft:grass_block", "minecraft:bell"} | WATERS #:
TAIGA_VILLAGE_SHEPHERDS_HOUSE = {"minecraft:cobblestone_stairs", "minecraft:grass_path", "minecraft:torch", "minecraft:purple_carpet", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:loom", "minecraft:white_carpet",
                                 "minecraft:spruce_fence", "minecraft:spruce_log", "minecraft:spruce_door", "minecraft:spruce_planks", "minecraft:spruce_trapdoor", "minecraft:spruce_pressure_plate", "minecraft:grass_block"} #:
TAIGA_VILLAGE_TANNERY = {"minecraft:cobblestone_stairs", "minecraft:torch", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:poppy", "minecraft:fern", "minecraft:spruce_log", "minecraft:spruce_door", "minecraft:large_fern",
                         "minecraft:chest", "minecraft:grass_block", "minecraft:cauldron", "minecraft:spruce_trapdoor"} #:
TAIGA_VILLAGE_TEMPLE = {"minecraft:cobblestone_wall", "minecraft:purple_carpet", "minecraft:dirt", "minecraft:large_fern", "minecraft:brewing_stand", "minecraft:ladder", "minecraft:spruce_door", "minecraft:spruce_planks",
                        "minecraft:cobblestone_stairs", "minecraft:torch", "minecraft:spruce_trapdoor", "potted_poppy", "minecraft:spruce_wood", "minecraft:grass_path", "minecraft:cobblestone", "minecraft:glass_pane", "minecraft:spruce_fence",
                        "minecraft:spruce_log", "minecraft:poppy", "minecraft:grass_block"} #:
TAIGA_VILLAGE_TOOL_SMITH = {"minecraft:cobblestone_stairs", "minecraft:grass_path", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:spruce_log", "minecraft:spruce_door", "minecraft:spruce_planks",
                            "minecraft:spruce_trapdoor", "minecraft:chest", "minecraft:grass_block", "minecraft:smithing_table"} #:
TAIGA_VILLAGE_WEAPONSMITH = {"minecraft:cobblestone_wall", "minecraft:grass_path", "minecraft:torch", "minecraft:cobblestone", "minecraft:dirt", "minecraft:glass_pane", "minecraft:large_fern", "minecraft:grindstone", "minecraft:fern",
                             "minecraft:spruce_fence", "minecraft:spruce_log", "minecraft:spruce_door", "minecraft:spruce_planks", "minecraft:spruce_stairs", "minecraft:poppy", "minecraft:chest", "minecraft:grass_block", "minecraft:spruce_trapdoor"} #:
TAIGA_VILLAGE_BLOCKS = TAIGA_VILLAGE_ANIMAL_PEN | TAIGA_VILLAGE_ARMORER | TAIGA_VILLAGE_ARMORER_HOUSE | TAIGA_VILLAGE_BUTCHER_SHOP | TAIGA_VILLAGE_CARTOGRAPHER_HOUSE | TAIGA_VILLAGE_DECORATION | TAIGA_VILLAGE_FISHER_COTTAGE | TAIGA_VILLAGE_FLETCHER_HOUSE | TAIGA_VILLAGE_LAMP_POST | TAIGA_VILLAGE_FARM | TAIGA_VILLAGE_LIBRARY | TAIGA_VILLAGE_MASONS_HOUSE | TAIGA_VILLAGE_HOUSE | TAIGA_VILLAGE_MEETING_POINT | TAIGA_VILLAGE_SHEPHERDS_HOUSE | TAIGA_VILLAGE_TANNERY | TAIGA_VILLAGE_TEMPLE | TAIGA_VILLAGE_TOOL_SMITH | TAIGA_VILLAGE_WEAPONSMITH #:
VILLAGE_BLOCKS = PLAINS_VILLAGE_BLOCKS | DESERT_VILLAGE_BLOCKS | SAVANNA_VILLAGE_BLOCKS | TAIGA_VILLAGE_BLOCKS | SNOWY_VILLAGE_BLOCKS #:

WOODLAND_MANSION_BLOCKS = {"minecraft:birch_fence", "minecraft:birch_planks",
                           "minecraft:birch_slab", "minecraft:birch_stairs",
                           "minecraft:black_wall_banner",
                           "minecraft:black_carpet", "minecraft:black_wool",
                           "minecraft:blue_carpet", "minecraft:blue_wool",
                           "minecraft:bookshelf",
                           "minecraft:brown_carpet", "minecraft:brown_wool",
                           "minecraft:carved_pumpkin", "minecraft:cauldron",
                           "minecraft:chest", "minecraft:trapped_chest",
                           "minecraft:coarse_dirt",
                           "minecraft:cobblestone",
                           "minecraft:cobblestone_slab",
                           "minecraft:cobblestone_stairs",
                           "minecraft:cobblestone_wall",
                           "minecraft:cobweb",
                           "minecraft:cyan_carpet", "minecraft:cyan_wool",
                           "minecraft:damaged_anvil",
                           "minecraft:dark_oak_door",
                           "minecraft:dark_oak_fence",
                           "minecraft:dark_oak_fence_gate",
                           "minecraft:dark_oak_leaves",
                           "minecraft:dark_oak_log",
                           "minecraft:dark_oak_sapling",
                           "minecraft:dark_oak_stairs",
                           "minecraft:diamond_block", "minecraft:dirt",
                           "minecraft:farmland",
                           "minecraft:glass", "minecraft:glass_pane",
                           "minecraft:gray_wall_banner",
                           "minecraft:gray_carpet", "minecraft:gray_wool",
                           "minecraft:green_carpet", "minecraft:green_wool",
                           "minecraft:infested_cobblestone",
                           "minecraft:iron_bars", "minecraft:iron_door",
                           "minecraft:ladder", "minecraft:lapis_block",
                           "minecraft:lever",
                           "minecraft:light_blue_wool",
                           "minecraft:light_gray_wall_banner",
                           "minecraft:light_gray_carpet",
                           "minecraft:light_gray_wool",
                           "minecraft:lily_pad",
                           "minecraft:lime_carpet", "minecraft:lime_wool",
                           "minecraft:magenta_carpet",
                           "minecraft:oak_fence", "minecraft:oak_planks",
                           "minecraft:oak_slab", "minecraft:oak_stairs",
                           "minecraft:obsidian",
                           "minecraft:orange_wool",
                           "minecraft:pink_carpet",
                           "minecraft:polished_andesite",
                           "minecraft:potted_allium",
                           "minecraft:potted_azure_bluet",
                           "minecraft:potted_birch_sapling",
                           "minecraft:potted_blue_orchid",
                           "minecraft:potted_dandelion",
                           "minecraft:potted_oxeye_daisy",
                           "minecraft:potted_poppy",
                           "minecraft:potted_red_tulip",
                           "minecraft:potted_white_tulip",
                           "minecraft:purple_carpet",
                           "minecraft:rail",
                           "minecraft:red_carpet", "minecraft:red_wool",
                           "minecraft:redstone_wire",
                           "minecraft:smooth_stone_slab",
                           "minecraft:spawner", "minecraft:tnt",
                           "minecraft:torch", "minecraft:wall_torch",
                           "minecraft:vines",
                           "minecraft:wheat",
                           "minecraft:white_carpet", "minecraft:white_wool",
                           "minecraft:yellow_carpet", "minecraft:yellow_wool",
                           } \
                          | BLOCK_CROPS | SMALL_MUSHROOMS | LAVAS | WATERS #:

# mixed
OVERWORLD_RUINED_PORTAL_BLOCKS = {"minecraft:gold_block",
                                  "minecraft:chest",
                                  "minecraft:magma_block",
                                  "minecraft:netherrack",
                                  "minecraft:iron_bars",
                                  "minecraft:stone",
                                  } \
                                 | OBSIDIAN_BLOCKS | LAVAS | STONE_SLABS \
                                 | STONE_BRICKS | STONE_BRICK_SLABS | STONE_BRICK_STAIRS | STONE_BRICK_WALLS #:

REGULAR_OVERWORLD_STRUCTURE_BLOCKS = MINESHAFT_BLOCKS | STRONGHOLD_BLOCKS \
                                     | OVERWORLD_RUINED_PORTAL_BLOCKS | DUNGEON_BLOCKS #:
BEACHES_STRUCTURE_BLOCKS = BURIED_TREASURE_BLOCKS #:
DARK_FOREST_STRUCTURE_BLOCKS = WOODLAND_MANSION_BLOCKS #:
DESERT_STRUCTURE_BLOCKS = DESERT_PYRAMID_BLOCKS | DESERT_VILLAGE_BLOCKS \
                          | DESERT_WELL_BLOCKS | PILLAGER_OUTPOST_BLOCKS | OVERWORLD_FOSSIL_BLOCKS #:
JUNGLE_STRUCTURE_BLOCKS = JUNGLE_TEMPLE_BLOCKS #:
FROZEN_OCEAN_STRUCTURE_BLOCKS = ICEBERG_BLOCKS #:
OCEAN_STRUCTURE_BLOCKS = FROZEN_OCEAN_STRUCTURE_BLOCKS \
                         | OCEAN_RUINS_BLOCKS | SHIPWRECK_BLOCKS | OCEAN_MONUMENT_BLOCKS #:
PLAINS_STRUCTURE_BLOCKS = PILLAGER_OUTPOST_BLOCKS | PLAINS_VILLAGE_BLOCKS #:
SAVANNA_STRUCTURE_BLOCKS = PILLAGER_OUTPOST_BLOCKS | SAVANNA_VILLAGE_BLOCKS #:
SNOWY_STRUCTURE_BLOCKS = SNOWY_VILLAGE_BLOCKS | IGLOO_BLOCKS \
                         | PILLAGER_OUTPOST_BLOCKS #:
SWAMP_STRUCTURE_BLOCKS = SWAMP_HUT | OVERWORLD_FOSSIL_BLOCKS #:
OLD_GROWTH_TAIGA_BLOCKS = FOREST_ROCK_BLOCKS #:
TAIGA_STRUCTURE_BLOCKS = OLD_GROWTH_TAIGA_BLOCKS \
                         | PILLAGER_OUTPOST_BLOCKS | TAIGA_VILLAGE_BLOCKS #:
OVERWORLD_GENERATED_STRUCTURE_BLOCKS = REGULAR_OVERWORLD_STRUCTURE_BLOCKS \
                                       | BEACHES_STRUCTURE_BLOCKS | DARK_FOREST_STRUCTURE_BLOCKS \
                                       | DESERT_STRUCTURE_BLOCKS | JUNGLE_STRUCTURE_BLOCKS \
                                       | OCEAN_STRUCTURE_BLOCKS | PLAINS_STRUCTURE_BLOCKS \
                                       | SAVANNA_STRUCTURE_BLOCKS | SNOWY_STRUCTURE_BLOCKS \
                                       | SWAMP_STRUCTURE_BLOCKS | TAIGA_STRUCTURE_BLOCKS #:

# nether
NETHER_FORTRESS_BLOCKS = {"minecraft:nether_bricks",
                          "minecraft:nether_brick_fence",
                          "minecraft:nether_brick_stairs",
                          "minecraft:soul_sand", "minecraft:nether_wart",
                          "minecraft:chest", "minecraft:spawner", } \
                         | LAVAS #:
BASTION_REMNANT_BLOCKS = {"minecraft:bgold_block",
                          "minecraft:blackstone",
                          "minecraft:blackstone_slab",
                          "minecraft:blackstone_stairs",
                          "minecraft:blackstone_wall",
                          "minecraft:gilded_blackstone",
                          "minecraft:polished_blackstone_brick_stairs",
                          "minecraft:chiseled_polished_blackstone",
                          "minecraft:chain",
                          "minecraft:lantern",
                          "minecraft:chest",
                          "minecraft:glowstone",
                          "minecraft:magma_block",
                          "minecraft:nether_wart",
                          "minecraft:netherrack",
                          "minecraft:quartz",
                          "minecraft:smooth_quartz",
                          "minecraft:smooth_quartz_slab",
                          "minecraft:soul_sand",
                          "minecraft:spawner", } \
                         | BASALT_BLOCKS | POLISHED_BLACKSTONE_BRICKS | LAVAS #:
NETHER_RUINED_PORTAL_BLOCKS = {"minecraft:gold_block",
                               "minecraft:chest",
                               "minecraft:magma_block",
                               "minecraft:netherrack",
                               "minecraft:chain",
                               "minecraft:chiseled_polished_blackstone",
                               "minecraft:polished_blackstone",
                               "minecraft:polished_blackstone_stairs",
                               "minecraft:polished_blackstone_brick_slab",
                               "minecraft:polished_blackstone_brick_stairs",
                               "minecraft:polished_blackstone_brick_wall", } \
                              | OBSIDIAN_BLOCKS | LAVAS | POLISHED_BLACKSTONE_BRICKS #:
NETHER_FOSSIL_BLOCKS = {"minecraft:bone_block", } #:

REGULAR_NETHER_STRUCTURE_BLOCKS = NETHER_FORTRESS_BLOCKS \
                                  | NETHER_RUINED_PORTAL_BLOCKS #:
NETHER_WASTES_STRUCTURE_BLOCKS = BASTION_REMNANT_BLOCKS #:
CRIMSON_FOREST_STRUCTURE_BLOCKS = BASTION_REMNANT_BLOCKS #:
WARPED_FOREST_STRUCTURE_BLOCKS = BASTION_REMNANT_BLOCKS #:
SOUL_SAND_VALLEY_STRUCTURE_BLOCKS = BASTION_REMNANT_BLOCKS \
                                    | NETHER_FOSSIL_BLOCKS #:
NETHER_GENERATED_STRUCTURE_BLOCKS = REGULAR_NETHER_STRUCTURE_BLOCKS \
                                    | NETHER_WASTES_STRUCTURE_BLOCKS | CRIMSON_FOREST_STRUCTURE_BLOCKS \
                                    | WARPED_FOREST_STRUCTURE_BLOCKS | SOUL_SAND_VALLEY_STRUCTURE_BLOCKS #:

# end
END_CITY_BLOCKS = {"minecraft:chest", "minecraft:end_rod",
                   "minecraft:end_stone_bricks",
                   "minecraft:ender_chest",
                   "minecraft:magenta_wall_banner",
                   "minecraft:ladder",
                   "minecraft:magenta_stained_glass",
                   "minecraft:purpur_slab",
                   "minecraft:purpur_stairs", } \
                  | PURPUR_BLOCKS #:
END_SHIP_BLOCKS = {"minecraft:ender_dragon_wall_head",
                   "minecraft:obsidian", } \
                  | END_CITY_BLOCKS \
                  - {"minecraft:magenta_wall_banner", "minecraft:ender_chest"} #:

REGULAR_END_STRUCTURE_BLOCKS = END_CITY_BLOCKS | END_SHIP_BLOCKS #:
END_GENERATED_STRUCTURE_BLOCKS = REGULAR_END_STRUCTURE_BLOCKS #:

# groups
RUINED_PORTAL_BLOCKS = OVERWORLD_RUINED_PORTAL_BLOCKS \
                       | NETHER_RUINED_PORTAL_BLOCKS #:
FOSSIL_BLOCKS = OVERWORLD_FOSSIL_BLOCKS | NETHER_FOSSIL_BLOCKS #:
GENERATED_STRUCTURE_BLOCKS = OVERWORLD_GENERATED_STRUCTURE_BLOCKS \
                             | NETHER_GENERATED_STRUCTURE_BLOCKS | END_GENERATED_STRUCTURE_BLOCKS #:

# ================================================= grouped by obtrusiveness

INVISIBLE = INVISIBLE_BLOCKS #:

# filter skylight
FILTERING = {"minecraft:bubble_column",
             "minecraft:ice", "minecraft:frosted_ice",
             "minecraft:cobweb",
             "minecraft:slime_block", "minecraft:honey_block",
             "minecraft:spawner", "minecraft:beacon",
             "minecraft:end_gateway", } \
            | CHORUS | FLUIDS | LEAVES | SHULKER_BOXES #:

# can be seen through easily
UNOBTRUSIVE = {"minecraft:ladder", "minecraft:tripwire", "minecraft:end_rod",
               "minecraft:nether_portal", "minecraft:iron_bars",
               "minecraft:chain", "minecraft:conduit", "minecraft:lily_pad",
               "minecraft:scaffolding", "minecraft:snow", } \
              | GLASSES | RAILS | WIRING | SWITCHES | TORCHES | SIGNS #:

# can be seen through moderately
OBTRUSIVE = {"minecraft:bell", "minecraft:brewing_stand", "minecraft:cake",
             "minecraft:lectern", } \
            | ANVILS | CRANIUMS | PLANTS | BEDS | FENCES | GATES | SLABS | EGGS \
            | CAMPFIRES | FLOWER_POTS #:

TRANSPARENT = INVISIBLE | FILTERING | UNOBTRUSIVE | OBTRUSIVE #:

# all else is considered opaque

# ========================================================= map colouring
# block visualization
# based on https://minecraft.gamepedia.com/Map_item_format#Base_colors
# liberty was taken to move stained glass panes and various flowers
# into the appropriate colour category

MAP_TRANSPARENT = {"minecraft:redstone_lamp", "minecraft:cake",
                  "minecraft:ladder",
                  "minecraft:tripwire_hook", "minecraft:tripwire",
                  "minecraft:end_rod",
                  "minecraft:glass", "minecraft:glass_pane",
                  "minecraft:nether_portal", "minecraft:iron_bars",
                  "minecraft:chain", } \
                 | INVISIBLE | WIRING | RAILS | SWITCHES | CRANIUMS | TORCHES | FLOWER_POTS #:

# base map colours
# WARNING: all non-transparent blocks are listed individually here again
COLOR_TO_BLOCKS: Dict[int, Set[str]] = {
    0x7FB238: {"minecraft:grass_block", "minecraft:slime_block", },
    0xF7E9A3: {
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
                  "minecraft:sandstone_slab",
                  "minecraft:sandstone_stairs",
                  "minecraft:sandstone_wall",
                  "minecraft:cut_sandstone_slab",
                  "minecraft:smooth_sandstone_slab",
                  "minecraft:smooth_sandstone_stairs",
                  "minecraft:glowstone",
                  "minecraft:end_stone",
                  "minecraft:end_stone_bricks",
                  "minecraft:end_stone_brick_slab",
                  "minecraft:end_stone_brick_stairs",
                  "minecraft:end_stone_brick_wall",
                  "minecraft:bone_block",
                  "minecraft:turtle_egg",
                  "minecraft:scaffolding",
              } | REGULAR_SANDSTONES,
    0xC7C7C7: {"minecraft:cobweb", "minecraft:mushroom_stem", },
    0xFF0000: {
                  "minecraft:tnt",
                  "minecraft:fire",
                  "minecraft:redstone_block",
              } | LAVAS,
    0xA0A0FF: ICE_BLOCKS,
    0xA7A7A7: {
                  "minecraft:iron_block",
                  "minecraft:iron_door",
                  "minecraft:brewing_stand",
                  "minecraft:heavy_weighted_pressure_plate",
                  "minecraft:iron_trapdoor",
                  "minecraft:grindstone",
                  "minecraft:lodestone",
              } | ANVILS | LANTERNS,
    0x007C00: {
                  "minecraft:lily_pad",
                  "minecraft:cactus",
              } | SAPLINGS | FOLIAGE | GRASS_PLANTS - {"minecraft:bamboo_sapling", }
              | WILD_CROPS | FARMLAND_CROPS,
    0xFFFFFF: {
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
              } | SNOWS,
    0xA4A8B8: {
                  "minecraft:clay",
              } | INFESTED,
    0x976D4D: {
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
              } | DIRTS - SPREADING_DIRTS - {"minecraft:podzol"},
    0x707070: {
                  "minecraft:stone",
                  "minecraft:stone_slab",
                  "minecraft:stone_stairs",
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
                  "minecraft:dispenser",
                  "minecraft:dropper",
                  "minecraft:mossy_cobblestone",
                  "minecraft:mossy_cobblestone_slab",
                  "minecraft:mossy_cobblestone_stairs",
                  "minecraft:mossy_cobblestone_wall",
                  "minecraft:spawner",
                  "minecraft:furnace",
                  "minecraft:stone_pressure_plate",
                  "minecraft:stone_brick_wall",
                  "minecraft:mossy_stone_brick_wall",
                  "minecraft:ender_chest",
                  "minecraft:smooth_stone",
                  "minecraft:smooth_stone_slab",
                  "minecraft:observer",
                  "minecraft:smoker",
                  "minecraft:blast_furnace",
                  "minecraft:stonecutter",
                  "minecraft:gravel",
                  "minecraft:acacia_log",
                  "minecraft:cauldron",
                  "minecraft:hopper",
              } | OVERWORLD_ORES | PISTONS
              | STONE_BRICKS | STONE_BRICK_SLABS | STONE_BRICK_STAIRS,
    0x4040FF: {
                  "minecraft:water",
                  "minecraft:bubble_column",
              } | KELPS | SEAGRASSES,
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
        "minecraft:prismarine",
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
    0x191919: {
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
                  "minecraft:polished_blackstone_brick_slab",
                  "minecraft:polished_blackstone_brick_stairs",
                  "minecraft:polished_blackstone_brick_wall",
                  "minecraft:polished_blackstone_pressure_plate",
                  "minecraft:chiseled_polished_blackstone",
                  "minecraft:gilded_blackstone",
                  "minecraft:wither_rose",
              } | BASALT_BLOCKS | POLISHED_BLACKSTONE_BRICKS,
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
} #:
BLOCK_TO_COLOR: Dict[str, int] = {} #:
for hexval, ids in COLOR_TO_BLOCKS.items():
    for bid in ids:
        BLOCK_TO_COLOR[bid] = hexval

# ========================================================= biome-related

BIOMES = {
    0:   "ocean",
    1:   "plains",
    2:   "desert",
    3:   "mountains",
    4:   "forest",
    5:   "taiga",
    6:   "swamp",
    7:   "river",
    8:   "nether_wastes",
    9:   "the_end",
    10:  "frozen_ocean",
    11:  "frozen_river",
    12:  "snowy_tundra",
    13:  "snowy_mountains",
    14:  "mushroom_fields",
    15:  "mushroom_field_shore",
    16:  "beach",
    17:  "desert_hills",
    18:  "wooded_hills",
    19:  "taiga_hills",
    20:  "mountain_edge",
    21:  "jungle",
    22:  "jungle_hills",
    23:  "jungle_edge",
    24:  "deep_ocean",
    25:  "stone_shore",
    26:  "snowy_beach",
    27:  "birch_forest",
    28:  "birch_forest_hills",
    29:  "dark_forest",
    30:  "snowy_taiga",
    31:  "snowy_taiga_hills",
    32:  "giant_tree_taiga",
    33:  "giant_tree_taiga_hills",
    34:  "wooded_mountains",
    35:  "savanna",
    36:  "savanna_plateau",
    37:  "badlands",
    38:  "wooded_badlands_plateau",
    39:  "badlands_plateau",
    40:  "small_end_islands",
    41:  "end_midlands",
    42:  "end_highlands",
    43:  "end_barrens",
    44:  "warm_ocean",
    45:  "lukewarm_ocean",
    46:  "cold_ocean",
    47:  "deep_warm_ocean",
    48:  "deep_lukewarm_ocean",
    49:  "deep_cold_ocean",
    50:  "deep_frozen_ocean",
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
} #:

# ========================================================= technical values

# the width of ASCII characters in pixels
# space between characters is 1
# the widest supported Unicode character is 9 wide
ASCII_CHAR_TO_WIDTH = {
    "A":  5,
    "a":  5,
    "B":  5,
    "b":  5,
    "C":  5,
    "c":  5,
    "D":  5,
    "d":  5,
    "E":  5,
    "e":  5,
    "F":  5,
    "f":  4,
    "G":  5,
    "g":  5,
    "H":  5,
    "h":  5,
    "I":  3,
    "i":  1,
    "J":  5,
    "j":  5,
    "K":  5,
    "k":  4,
    "L":  5,
    "l":  2,
    "M":  5,
    "m":  5,
    "N":  5,
    "n":  5,
    "O":  5,
    "o":  5,
    "P":  5,
    "p":  5,
    "Q":  5,
    "q":  5,
    "R":  5,
    "r":  5,
    "S":  5,
    "s":  5,
    "T":  5,
    "t":  3,
    "U":  5,
    "u":  5,
    "V":  5,
    "v":  5,
    "W":  5,
    "w":  5,
    "X":  5,
    "x":  5,
    "Y":  5,
    "y":  5,
    "Z":  5,
    "z":  5,
    "1":  5,
    "2":  5,
    "3":  5,
    "4":  5,
    "5":  5,
    "6":  5,
    "7":  5,
    "8":  5,
    "9":  5,
    "0":  5,
    " ":  3,
    "!":  1,
    "@":  6,
    "#":  5,
    "$":  5,
    "£":  5,
    "%":  5,
    "^":  5,
    "&":  5,
    "*":  3,
    "(":  3,
    ")":  3,
    "_":  5,
    "-":  5,
    "+":  5,
    "=":  5,
    "~":  6,
    "[":  3,
    "]":  3,
    "{":  3,
    "}":  3,
    "|":  1,
    "\\": 5,
    ":":  1,
    ";":  1,
    '"':  3,
    "'":  1,
    ",":  1,
    "<":  4,
    ">":  4,
    ".":  1,
    "?":  5,
    "/":  5,
    "`":  2,
} #:


BOOK_PAGES_PER_BOOK      = 100 #:
BOOK_CHARACTERS_PER_PAGE = 255 #:
BOOK_LINES_PER_PAGE      = 14 #:
BOOK_PIXELS_PER_LINE     = 114 #:


INVENTORY_SIZE_TO_CONTAINER_BLOCKS = {
    ivec2(9,3): {"minecraft:barrel", } | CHESTS | SHULKER_BOXES,
    ivec2(3,3): {"minecraft:dispenser", "minecraft:dropper", },
    ivec2(5,1): {"minecraft:hopper", "minecraft:brewing_stand", },
    ivec2(3,1): FURNACES,
} #:
CONTAINER_BLOCK_TO_INVENTORY_SIZE = {} #:
for size, ids in INVENTORY_SIZE_TO_CONTAINER_BLOCKS.items():
    for bid in ids:
        CONTAINER_BLOCK_TO_INVENTORY_SIZE[bid] = size
