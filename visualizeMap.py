import cv2
import matplotlib.pyplot as plt
import numpy as np

import interfaceUtils
from worldLoader import WorldSlice

rect = (0, 0, 128, 128)  # default build area of example.py

buildArea = interfaceUtils.requestBuildArea()
if buildArea != -1:
    x1 = buildArea["xFrom"]
    z1 = buildArea["zFrom"]
    x2 = buildArea["xTo"]
    z2 = buildArea["zTo"]
    print(buildArea)
    rect = (x1, z1, x2 - x1, z2 - z1)
    print(rect)

slice = WorldSlice(rect)

heightmap1 = np.array(
    slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"], dtype=np.uint8)
heightmap2 = np.array(slice.heightmaps["OCEAN_FLOOR"], dtype=np.uint8)
heightmap = np.minimum(heightmap1, heightmap2)
watermap = heightmap - heightmap2 + 128

bHM = cv2.blur(heightmap, (7, 7))

dx = cv2.Scharr(heightmap, cv2.CV_16S, 1, 0)
dy = cv2.Scharr(heightmap, cv2.CV_16S, 0, 1)
atan = np.arctan2(dx, dy, dtype=np.float64) * 5 / 6.283
atan = atan % 5
atan = atan.astype('uint8')

finalHM = cv2.medianBlur(heightmap, 7)

diffmap = finalHM.astype('float64') - heightmap.astype('float64')
diffmap = np.round(diffmap)
diffmap = diffmap.astype('int8')

# diff
img = heightmap
diffx = cv2.Scharr(img, cv2.CV_16S, 1, 0)
diffy = cv2.Scharr(img, cv2.CV_16S, 0, 1)
dmag = np.absolute(diffx) + np.absolute(diffy)
# thres = 32
# dmag = dmag - thres
dmag = dmag.clip(0, 255)
dmag = dmag.astype('uint8')

# block visualization
# based on https://minecraft.gamepedia.com/Map_item_format#Base_colors
# liberty was taken to move stained glass into the appropriate colour category

VERSION = "1.16.x"

TRANSPARENT = ('minecraft:air', 'minecraft:void_air', 'minecraft:cave_air',
               'minecraft:barrier', 'minecraft:redstone_lamp', 'minecraft:cake', 'minecraft:powered_rail', 'minecraft:detector_rail', 'minecraft:torch', 'minecraft:redstone_wire', 'minecraft:ladder', 'minecraft:rail', 'minecraft:lever', 'minecraft:redstone_torch',
               'minecraft:stone_button', 'minecraft:oak_button', , 'minecraft:spruce_button', 'minecraft:birch_button', 'minecraft:jungle_button', 'minecraft:acacia_button', 'minecraft:dark_oak_button', 'minecraft:crimson_button', 'minecraft:warped_button', 'minecraft:polished_blackstone_button',
               'minecraft:repeater', 'minecraft:tripwire_hook', 'minecraft:tripwire', 'minecraft:flower_pot', 'minecraft:head', 'minecraft:comparator', 'minecraft:activator_rail', 'minecraft:end_rod',
               'minecraft:glass', 'minecraft:glass_pane',
               'minecraft:nether_portal', 'minecraft:structure_void', 'minecraft:iron_bars', 'minecraft:soul_fire_torch', 'minecraft:chain')

# base colours
PALETTE = {0x7fb238: ('minecraft:grass_block', 'minecraft:slime_block'),
           0xf7e9a3: ('minecraft:sand',
                      'minecraft:birch_planks', 'minecraft:birch_log', 'minecraft:birch_stripped_log', 'minecraft:birch_wood', 'minecraft:birch_stripped_wood', 'minecraft:birch_sign', 'minecraft:birch_pressure_plate', 'minecraft:birch_trapdoor', 'minecraft:birch_stairs', 'minecraft:birch_slab', 'minecraft:birch_fence_gate', 'minecraft:birch_fence', 'minecraft:birch_door)',
                      'minecraft:sandstone', 'minecraft:sandstone_slab', 'minecraft:sandstone_stairs', 'minecraft:sandstone_wall)',
                      'minecraft:cut_sandstone', 'minecraft:cut_sandstone_slab', 'minecraft:cut_sandstone_stairs', 'minecraft:cut_sandstone_wall)',
                      'minecraft:smooth_sandstone', 'minecraft:smooth_sandstone_slab', 'minecraft:smooth_sandstone_stairs', 'minecraft:smooth_sandstone_wall)',
                      'minecraft:chiseled_sandstone',
                      'minecraft:glowstone',
                      'minecraft:end_stone',
                      'minecraft:end_stone_bricks', 'minecraft:end_stone_brick_slab', 'minecraft:end_stone_brick_stairs', 'minecraft:end_stone_brick_wall)',
                      'minecraft:bone_block',
                      'minecraft:turtle_egg',
                      'minecraft:scaffolding'),
           0xc7c7c7: ('minecraft:cobweb', 'minecraft:mushroom_stem'),
           0xff0000: ('minecraft:lava', 'minecraft:tnt',
                      'minecraft:fire', 'minecraft:redstone_block'),
           0xa0a0ff: ('minecraft:ice', 'minecraft:frosted_ice',
                      'minecraft:packed_ice', 'minecraft:blue_ice'),
           0xa7a7a7: ('minecraft:block_of_iron', 'minecraft:iron_door',
                      'minecraft:brewing_stand', 'minecraft:heavy_weighted_pressure_plate',
                      'minecraft:iron_trapdoor', 'minecraft:lantern',
                      'minecraft:anvil', 'minecraft:chipped_anvil', 'minecraft:damaged_anvil',
                      'minecraft:grindstone', 'minecraft:soul_fire_lantern',
                      'minecraft:lodestone'),
           0x007c00: ('minecraft:oak_sapling', 'minecraft:spruce_sapling', 'minecraft:birch_sapling', 'minecraft:jungle_sapling', 'minecraft:acacia_sapling', 'minecraft:dark_oak_sapling',
                      'minecraft:dandelion', 'minecraft:poppy', 'minecraft:blue_orchid', 'minecraft:allium', 'minecraft:azure_bluet', 'minecraft:red_tulip', 'minecraft:orange_tulip', 'minecraft:white_tulip', 'minecraft:pink_tulip', 'minecraft:oxeye_daisy', 'minecraft:cornflower', 'minecraft:lily_of_the_valley', 'minecraft:wither_rose', 'minecraft:sunflower', 'minecraft:lilac', 'minecraft:rose_bush', 'minecraft:peony',
                      'minecraft:wheat', 'minecraft:sugar_cane', 'minecraft:pumpkin_stem', 'minecraft:melon_stem', 'minecraft:lily_pad', 'minecraft:cocoa', 'minecraft:carrots', 'minecraft:potatoes', 'minecraft:beetroots', 'minecraft:sweet_berry_bush',
                      'minecraft:grass', 'minecraft:tall_grass',
                      'minecraft:fern', 'minecraft:large_fern',
                      'minecraft:vines',
                      'minecraft:oak_leaves', 'minecraft:spruce_leaves', 'minecraft:birch_leaves', 'minecraft:jungle_leaves', 'minecraft:acacia_leaves', 'minecraft:dark_oak_leaves',
                      'minecraft:cactus',
                      'minecraft:bamboo'),
           0xffffff: ('minecraft:snow', 'minecraft:snow_block',
                      'minecraft:white_bed', 'minecraft:white_wool',
                      'minecraft:white_stained_glass', 'minecraft:white_stained_glass_pane',
                      'minecraft:white_carpet', 'minecraft:white_banner',
                      'minecraft:white_shulker_box', 'minecraft:white_glazed_terracotta',
                      'minecraft:white_concrete', 'minecraft:white_concrete_powder'),
           0xa4a8b8: ('minecraft:clay',
                      'minecraft:infested_stone', 'minecraft:infested_cobblestone', 'minecraft:infested_stone_bricks', 'minecraft:infested_cracked_stone_bricks', 'minecraft:infested_mossy_stone_bricks', 'minecraft:infested_chiseled_stone_bricks'),
           0x976d4d: ('minecraft:dirt', 'minecraft:coarse_dirt', 'minecraft:farmland', 'minecraft:grass_path',
                      'minecraft:granite', 'minecraft:granite_slab', 'minecraft:granite_stairs', 'minecraft:granite_wall',
                      'minecraft:polished_granite', 'minecraft:polished_granite_slab', 'minecraft:polished_granite_stairs',
                      'minecraft:jungle_planks', 'minecraft:jungle_log', 'minecraft:stripped_jungle_log', 'minecraft:jungle_wood', 'minecraft:stripped_jungle_wood', 'minecraft:jungle_sign', 'minecraft:jungle_pressure_plate', 'minecraft:jungle_trapdoor', 'minecraft:jungle_stairs', 'minecraft:jungle_slab', 'minecraft:jungle_fence_gate', 'minecraft:jungle_fence', 'minecraft:jungle_door)',
                      'minecraft:jukebox', 'minecraft:brown_mushroom_block'),
           0x707070: ('minecraft:stone', 'minecraft:stone_slab', 'minecraft:stone_stairs',
                      'minecraft:andesite', 'minecraft:andesite_slab', 'minecraft:andesite_stairs',
                      'minecraft:cobblestone', 'minecraft:cobblestone_slab', 'minecraft:cobblestone_stairs',
                      'minecraft:bedrock', 'minecraft:gold_ore',
                      'minecraft:iron_ore', 'minecraft:coal_ore',
                      'minecraft:lapis_lazuli_ore', 'diamond_ore'
                      'minecraft:dispenser', 'minecraft:dropper',
                      'minecraft:mossy_cobblestone', 'minecraft:mossy_cobblestone_slab', 'minecraft:mossy_cobblestone_stairs',
                      'minecraft:spawner', 'minecraft:furnace', 'minecraft:stone_pressure_plate', 'minecraft:redstone_ore',
                      'minecraft:stone_bricks', 'minecraft:stone_brick_slab', 'minecraft:stone_brick_stairs', 'minecraft:stone_brick_wall',
                      'minecraft:mossy_stone_bricks', 'minecraft:mossy_stone_brick_slab', 'minecraft:mossy_stone_brick_stairs', 'minecraft:mossy_stone_brick_wall',
                      'minecraft:cracked_stone_bricks', 'minecraft:chiseled_stone_bricks',
                      'minecraft:emerald_ore', 'minecraft:ender_chest',
                      'minecraft:smooth_stone', 'minecraft:smooth_stone_slab', 'minecraft:smooth_stone_stairs',
                      'minecraft:observer', 'minecraft:smoker',
                      'minecraft:blast_furnace', 'minecraft:stonecutter',
                      'minecraft:sticky_piston', 'minecraft:piston',
                      'minecraft:piston_head', 'minecraft:gravel',
                      'minecraft:acacia_log', 'minecraft:cauldron',
                      'minecraft:hopper'),
           0x4040ff: ('minecraft:kelp', 'minecraft:seagrass',
                      'minecraft:water', 'minecraft:bubble_column'),
           0x8f7748: ('minecraft:oak_planks', 'minecraft:oak_log', 'minecraft:oak_stripped_log', 'minecraft:oak_wood', 'minecraft:oak_stripped_wood', 'minecraft:oak_sign', 'minecraft:oak_pressure_plate', 'minecraft:oak_trapdoor', 'minecraft:oak_stairs', 'minecraft:oak_slab', 'minecraft:oak_fence_gate', 'minecraft:oak_fence', 'minecraft:oak_door)',
                      'minecraft:note_block', 'minecraft:bookshelf',
                      'minecraft:chest', 'minecraft:trapped_chest',
                      'minecraft:crafting_table', 'minecraft:daylight_detector',
                      'minecraft:loom', 'minecraft:barrel',
                      'minecraft:cartography_table', 'minecraft:fletching_table',
                      'minecraft:lectern', 'minecraft:smithing_table',
                      'minecraft:composter', 'minecraft:bamboo_sapling',
                      'minecraft:dead_bush', 'minecraft:petrified_oak_slab',
                      'minecraft:beehive'),
           0xfffcf5: ('minecraft:diorite', 'minecraft:polished_diorite',
                      'minecraft:birch_log',
                      'minecraft:block of quartz', 'minecraft:quartz_slab', 'minecraft:quartz_stairs',
                      'minecraft:chiseled_quartz_block', 'minecraft:quartz_pillar', 'minecraft:quartz_bricks',
                      'minecraft:sea_lantern', 'minecraft:target'),
           0xd87f33: ('minecraft:acacia_planks', 'minecraft:acacia_log', 'minecraft:acacia_stripped_log', 'minecraft:acacia_wood', 'minecraft:acacia_stripped_wood', 'minecraft:acacia_sign', 'minecraft:acacia_pressure_plate', 'minecraft:acacia_trapdoor', 'minecraft:acacia_stairs', 'minecraft:acacia_slab', 'minecraft:acacia_fence_gate', 'minecraft:acacia_fence', 'minecraft:acacia_door)',
                      'minecraft:red_sand',
                      'minecraft:orange_wool', 'minecraft:orange_carpet',
                      'minecraft:orange_shulker_box', 'minecraft:orange_bed',
                      'minecraft:orange_stained_glass', 'minecraft:orange_stained_glass_pane',
                      'minecraft:orange_banner', 'minecraft:orange_glazed_terracotta',
                      'minecraft:orange_concrete', 'minecraft:orange_concrete_powder',
                      'minecraft:pumpkin', 'minecraft:carved_pumpkin', "minecraft:jack_o'lantern",
                      'minecraft:terracotta',
                      'minecraft:red_sandstone', 'minecraft:red_sandstone_slab', 'minecraft:red_sandstone_stairs', 'minecraft:red_sandstone_wall)',
                      'minecraft:cut_red_sandstone', 'minecraft:cut_red_sandstone_slab', 'minecraft:cut_red_sandstone_stairs', 'minecraft:cut_red_sandstone_wall)',
                      'minecraft:smooth_red_sandstone', 'minecraft:smooth_red_sandstone_slab', 'minecraft:smooth_red_sandstone_stairs', 'minecraft:smooth_red_sandstone_wall)',
                      'minecraft:chiseled_red_sandstone',
                      'minecraft:honey_block', 'minecraft:honeycomb_block'),
           0xb24cd8: ('minecraft:magenta_wool', 'minecraft:magenta_carpet',
                      'minecraft:magenta_shulker_box', 'minecraft:magenta_bed',
                      'minecraft:magenta_stained_glass', 'minecraft:magenta_stained_glass_pane',
                      'minecraft:magenta_banner', 'minecraft:magenta_glazed_terracotta',
                      'minecraft:magenta_concrete', 'minecraft:magenta_concrete_powder')
           0xb24cd8: ('minecraft:light_blue_wool', 'minecraft:light_blue_carpet',
                      'minecraft:light_blue_shulker_box', 'minecraft:light_blue_bed',
                      'minecraft:light_blue_stained_glass', 'minecraft:light_blue_stained_glass_pane',
                      'minecraft:light_blue_banner', 'minecraft:light_blue_glazed_terracotta',
                      'minecraft:light_blue_concrete', 'minecraft:light_blue_concrete_powder',
                      'minecraft:soul_fire'),
           0xe5e533: ('minecraft:sponge', 'minecraft:wet_sponge',
                      'minecraft:yellow', 'minecraft:yellow_carpet',
                      'minecraft:yellow_shulker_box', 'minecraft:yellow_bed',
                      'minecraft:yellow_stained_glass', 'minecraft:yellow_stained_glass_pane',
                      'minecraft:yellow_banner', 'minecraft:yellow_glazed_terracotta',
                      'minecraft:yellow_concrete', 'minecraft:yellow_concrete_powder',
                      'minecraft:hay_bale',
                      'minecraft:horn_coral_block', 'minecraft:horn_coral', 'minecraft:horn_coral_fan',
                      'minecraft:bee_nest'),
           0x7fcc19: ('minecraft:light_green_wool', 'minecraft:light_green_carpet',
                      'minecraft:light_green_shulker_box', 'minecraft:light_green_bed',
                      'minecraft:light_green_stained_glass', 'minecraft:light_green_stained_glass_pane',
                      'minecraft:light_green_banner', 'minecraft:light_green_glazed_terracotta',
                      'minecraft:light_green_concrete', 'minecraft:light_green_concrete_powder',
                      'minecraft:melon'),
           0xf27fa5: ('minecraft:pink_wool', 'minecraft:pink_carpet',
                      'minecraft:pink_shulker_box', 'minecraft:pink_bed',
                      'minecraft:pink_stained_glass', 'minecraft:pink_stained_glass_pane',
                      'minecraft:pink_banner', 'minecraft:pink_glazed_terracotta',
                      'minecraft:pink_concrete', 'minecraft:pink_concrete_powder',
                      'minecraft:brain_coral_block', 'minecraft:brain_coral', 'minecraft:brain_coral_fan'),
           0x4c4c4c: ('minecraft:acacia_wood',
                      'minecraft:gray_wool', 'minecraft:gray_carpet',
                      'minecraft:gray_shulker_box', 'minecraft:gray_bed',
                      'minecraft:gray_stained_glass', 'minecraft:gray_stained_glass_pane',
                      'minecraft:gray_banner', 'minecraft:gray_glazed_terracotta',
                      'minecraft:gray_concrete', 'minecraft:gray_concrete_powder',
                      'minecraft:dead_tube_coral_block', 'minecraft:dead_tube_coral', 'minecraft:dead_tube_coral_fan',
                      'minecraft:dead_brain_coral_block', 'minecraft:dead_brain_coral', 'minecraft:dead_brain_coral_fan',
                      'minecraft:dead_bubble_coral_block', 'minecraft:dead_bubble_coral', 'minecraft:dead_bubble_coral_fan',
                      'minecraft:dead_fire_coral_block', 'minecraft:dead_fire_coral', 'minecraft:dead_fire_coral_fan',
                      'minecraft:dead_horn_coral_block', 'minecraft:dead_horn_coral', 'minecraft:dead_horn_coral_fan'),
           0x999999: ('minecraft:light_gray_wool', 'minecraft:light_gray_carpet',
                      'minecraft:light_gray_shulker_box', 'minecraft:light_gray_bed',
                      'minecraft:light_gray_stained_glass', 'minecraft:light_gray_stained_glass_pane',
                      'minecraft:light_gray_banner', 'minecraft:light_gray_glazed_terracotta',
                      'minecraft:light_gray_concrete', 'minecraft:light_gray_concrete_powder',
                      'minecraft:structure_block', 'minecraft:jigsaw_block'),
           0x4c7f99: ('minecraft:cyan_wool', 'minecraft:cyan_carpet',
                      'minecraft:cyan_shulker_box', 'minecraft:cyan_bed',
                      'minecraft:cyan_stained_glass', 'minecraft:cyan_stained_glass_pane',
                      'minecraft:cyan_banner', 'minecraft:cyan_glazed_terracotta',
                      'minecraft:cyan_concrete', 'minecraft:cyan_concrete_powder',
                      'minecraft:prismarine_slab', 'minecraft:prismarine_stairs', 'minecraft:prismarine_wall',
                      'minecraft:warped_roots', 'minecraft:warped_door', 'minecraft:warped_fungus',
                      'minecraft:twisting_vines', 'minecraft:nether_sprouts'),
           0x7f3fb2: ('minecraft:shulker_box',
                      'minecraft:purple_wool', 'minecraft:purple_carpet',
                      'minecraft:purple_shulker_box', 'minecraft:purple_bed',
                      'minecraft:purple_stained_glass', 'minecraft:purple_stained_glass_pane',
                      'minecraft:purple_banner', 'minecraft:purple_glazed_terracotta',
                      'minecraft:purple_concrete', 'minecraft:purple_concrete_powder',
                      'minecraft:mycelium',
                      'minecraft:chorus_plant', 'minecraft:chorus_flower',
                      'minecraft:repeating_command_block',
                      'minecraft:bubble_coral_block', 'minecraft:bubble_coral', 'minecraft:bubble_coral_fan'),
           0x334cb2: ('minecraft:blue_wool', 'minecraft:blue_carpet',
                      'minecraft:blue_shulker_box', 'minecraft:blue_bed',
                      'minecraft:blue_stained_glass', 'minecraft:blue_stained_glass_pane',
                      'minecraft:blue_banner', 'minecraft:blue_glazed_terracotta',
                      'minecraft:blue_concrete', 'minecraft:blue_concrete_powder',
                      'minecraft:tube_coral_block', 'minecraft:tube_coral', 'minecraft:tube_coral_fan'),
           0x664c33: ('minecraft:dark_oak_planks', 'minecraft:dark_oak_log', 'minecraft:dark_oak_stripped_log', 'minecraft:dark_oak_wood', 'minecraft:dark_oak_stripped_wood', 'minecraft:dark_oak_sign', 'minecraft:dark_oak_pressure_plate', 'minecraft:dark_oak_trapdoor', 'minecraft:dark_oak_stairs', 'minecraft:dark_oak_slab', 'minecraft:dark_oak_fence_gate', 'minecraft:dark_oak_fence', 'minecraft:dark_oak_door)',
                      'minecraft:spruce_log',
                      'minecraft:brown_wool', 'minecraft:brown_carpet',
                      'minecraft:brown_shulker_box', 'minecraft:brown_bed',
                      'minecraft:brown_stained_glass', 'minecraft:brown_stained_glass_pane',
                      'minecraft:brown_banner', 'minecraft:brown_glazed_terracotta',
                      'minecraft:brown_concrete', 'minecraft:brown_concrete_powder',
                      'minecraft:soul_sand', 'minecraft:command_block',
                      'minecraft:brown_mushroom', 'minecraft:soul_soil'),
           0x667f33: ('minecraft:green_wool', 'minecraft:green_carpet',
                      'minecraft:green_shulker_box', 'minecraft:green_bed',
                      'minecraft:green_stained_glass', 'minecraft:green_stained_glass_pane',
                      'minecraft:green_banner', 'minecraft:green_glazed_terracotta',
                      'minecraft:green_concrete', 'minecraft:green_concrete_powder',
                      'minecraft:end_portal_frame', 'minecraft:chain_command_block',
                      'minecraft:dried_kelp_block', 'minecraft:sea_pickle'),
           0x993333: ('minecraft:red_wool', 'minecraft:red_carpet',
                      'minecraft:red_shulker_box', 'minecraft:red_bed',
                      'minecraft:red_stained_glass', 'minecraft:red_stained_glass_pane',
                      'minecraft:red_banner', 'minecraft:red_glazed_terracotta',
                      'minecraft:red_concrete', 'minecraft:red_concrete_powder',
                      'minecraft:bricks', 'minecraft:brick_slab', 'minecraft:brick_stairs', 'minecraft:brick_wall'
                      'minecraft:red_mushroom_block', 'minecraft:nether_wart',
                      'minecraft:enchanting_table', 'minecraft:nether_wart_block',
                      'minecraft:fire_coral_block', 'minecraft:fire_coral', 'minecraft:fire_coral_fan',
                      'minecraft:red_mushroom', 'minecraft:shroomlight'),
           0x191919: ('minecraft:black_wool', 'minecraft:black_carpet',
                      'minecraft:black_shulker_box', 'minecraft:black_bed',
                      'minecraft:black_stained_glass', 'minecraft:black_stained_glass_pane',
                      'minecraft:black_banner', 'minecraft:black_glazed_terracotta',
                      'minecraft:black_concrete', 'minecraft:black_concrete_powder',
                      'minecraft:obsidian', 'minecraft:end_portal',
                      'minecraft:dragon_egg', 'minecraft:coal_block',
                      'minecraft:end_gateway', 'minecraft:basalt',
                      'minecraft:polished_basalt', 'minecraft:block_of_netherite',
                      'minecraft:ancient_debris', 'minecraft:crying_obsidian',
                      'minecraft:respawn_anchor',
                      'minecraft:blackstone', 'minecraft:blackstone_slab', 'minecraft:blackstone_stairs', 'minecraft:blackstone_wall',
                      'minecraft:polished_blackstone', 'minecraft:polished_blackstone_slab', 'minecraft:polished_blackstone_stairs', 'minecraft:polished_blackstone_wall',
                      'minecraft:gilded_blackstone'),
           0xfaee4d: ('minecraft:block_of_gold', 'minecraft:light_weighted_pressure_plate', 'minecraft:bell'),
           0x5cdbd5: ('minecraft:block_of_diamond', 'minecraft:beacon',
                      'minecraft:prismarine_bricks', 'prismarine_brick_slab', 'minecraft:prismarine_brick_stairs',
                      'minecraft:dark_prismarine', 'dark_prismarine_slab', 'minecraft:dark_prismarine_stairs',
                      'minecraft:conduit'),
           0x4a80ff: ('minecraft:lapis_lazuli_block'),
           0x00d93a: ('minecraft:block_of_emerald'),
           0x815631: ('minecraft:podzol', 'minecraft:spruce_planks', 'minecraft:spruce_log', 'minecraft:stripped_spruce_log', 'minecraft:spruce_wood', 'minecraft:stripped_spruce_wood', 'minecraft:spruce_sign', 'minecraft:spruce_pressure_plate', 'minecraft:spruce_trapdoor', 'minecraft:spruce_stairs', 'minecraft:spruce_slab', 'minecraft:spruce_fence_gate', 'minecraft:spruce_fence', 'minecraft:spruce_door'
                      'minecraft:oak_log', 'minecraft:jungle_log',
                      'minecraft:campfire', 'minecraft:soul_campfire'),
           0x700200: ('minecraft:netherrack',
                      'minecraft:nether_bricks', 'minecraft:nether_brick_fence', 'minecraft:nether_brick_slab', 'minecraft:nether_brick_stairs', 'minecraft:nether_brick_wall', 'minecraft:cracked_nether_brick', 'minecraft:chiseled_nether_brick',
                      'minecraft:nether_gold_ore', 'minecraft:nether_quartz_ore',
                      'minecraft:magma_block',
                      'minecraft:red_nether_bricks', 'minecraft:red_nether_brick_slab', 'minecraft:red_nether_brick_stairs', 'minecraft:red_nether_brick_wall',
                      'minecraft:crimson_roots', 'minecraft:crimson_door', 'minecraft:crimson_fungus',
                      'minecraft:weeping_vines'),
           0xd1b1a1: ('minecraft:white_terracotta'),
           0x9f5224: ('minecraft:orange_terracotta'),
           0x95576c: ('minecraft:magenta_terracotta'),
           0x706c8a: ('minecraft:light_blue_terracotta'),
           0xba8524: ('minecraft:yellow_terracotta'),
           0x677535: ('minecraft:light_green_terracotta'),
           0xa04d4e: ('minecraft:pink_terracotta'),
           0x392923: ('minecraft:gray_terracotta'),
           0x876b62: ('minecraft:light_gray_terracotta'),
           0x575c5c: ('minecraft:cyan_terracotta'),
           0x7a4958: ('minecraft:purple_terracotta', 'minecraft:purple_shulker_box'),
           0x4c3e5c: ('minecraft:blue_terracotta'),
           0x4c3223: ('minecraft:brown_terracotta'),
           0x4c522a: ('minecraft:green_terracotta'),
           0x8e3c2e: ('minecraft:red_terracotta'),
           0x251610: ('minecraft:black_terracotta'),
           0xbd3031: ('minecraft:crimson_nylium'),
           0x943f61: ('minecraft:crimson_fence', 'minecraft:crimson_fence_gate', 'minecraft:crimson_planks', 'minecraft:crimson_pressure_plate', 'minecraft:crimson_sign', 'minecraft:crimson_slab', 'minecraft:crimson_stairs', 'minecraft:crimson_stem', 'minecraft:stripped_crimson_stem', 'minecraft:crimson_trapdoor'),
           0x5c191d: ('minecraft:crimson_hyphae', 'minecraft:stripped_crimson_hyphae'),
           0x167e86: ('minecraft:warped_nylium'),
           0x3a8e8c: ('minecraft:warped_fence', 'minecraft:warped_fence_gate', 'minecraft:warped_planks', 'minecraft:warped_pressure_plate', 'minecraft:warped_sign', 'minecraft:warped_slab', 'minecraft:warped_stairs', 'minecraft:warped_stem', 'minecraft:stripped_warped_stem', 'minecraft:warped_trapdoor'),
           0x562c3e: ('minecraft:warped_hyphae', 'minecraft:stripped_warped_hyphae'),
           0x14b485: ('minecraft:warped_wart_block')}


def verifyPaletteBlocks():
    counter = 0
    badcounter = 0
    passed = []
    tocheck = [block for i in PALETTE.values() for j in i] + TRANSPARENT
    for block in tocheck:
        if block in passed:
            badcounter += 1
            print(block + " is duplicate")
        elif interfaceUtils.setBlock(0, 300, 0, block) != 1
        badcounter += 1
        print("Cannot verify " + block)
        counter += 1
        passed.append(block)
        print(str(counter) + " blocks verified.", end='\r')
    interfaceUtils.setBlock(0, 300, 0, 'air')
    print("Scan complete.\n{}/{} blocks duplicate or could not be verified.".format(badcounter, counter))
    if badcounter > 0:
        print("Please check you are running on Minecraft " + VERSION)

# to translate a string of regular names into the appropriate list of minecraft block IDs
# def f(string): return ["minecraft:"+i.strip().lower().replace(" ", "_") for i in string.split(", ")]


palette = [
    "unknown",
    "minecraft:dirt",
    "minecraft:grass",
    "minecraft:grass_block",
    "minecraft:stone",
    "minecraft:sand",
    "minecraft:snow",
    "minecraft:water",
    "minecraft:ice",
    "minecraft:white_wool",
    "minecraft:white_concrete",
]

# to translate a 255 RGB to hex RGB value
# def f(r, g, b): return "0x"+(hex(r)+hex(g)+hex(b)).replace("0x", "")

paletteColors = [
    0x000000,
    0x777733,
    0x33aa33,
    0x33aa33,
    0x777777,
    0xffffaa,
    0xffffff,
    0x3333ee,
    0xaaaaee,
    0xffffff,
    0xffffff,
]

verifyPaletteBlocks()

paletteReverseLookup = {}
for i in range(len(palette)):
    paletteReverseLookup[palette[i]] = i

topmap = np.zeros((rect[2], rect[3]), dtype='int')
topcolor = np.zeros(topmap.shape, dtype="int")

unknownBlocks = set()

for dx in range(rect[2]):
    for dz in range(rect[3]):
        for dy in range(5):
            x = rect[0] + dx
            z = rect[1] + dz
            y = int(heightmap1[(dx, dz)]) - dy

            blockCompound = slice.getBlockCompoundAt((x, y, z))

            if blockCompound != None:
                blockID = blockCompound["Name"].value
                if(blockID in TRANSPARENT):
                    continue
                else:
                    numID = paletteReverseLookup.get(blockID, 0)
                    if(numID == 0):
                        unknownBlocks.add(blockID)
                    # print("%s > %i" % (blockID, numID))
                    topmap[(dx, dz)] = numID
                    topcolor[(dx, dz)] = paletteColors[numID]
                    break

print("unknown blocks: %s" % str(unknownBlocks))

# topcolor = np.pad(topcolor, 16, mode='edge')
topcolor = cv2.merge(((topcolor) & 0xff, (topcolor >> 8)
                      & 0xff, (topcolor >> 16) & 0xff))

off = np.expand_dims((diffx + diffy).astype("int"), 2)
# off = np.pad(off, ((16, 16), (16, 16), (0, 0)), mode='edge')
off = off.clip(-64, 64)
topcolor += off
topcolor = topcolor.clip(0, 255)

topcolor = topcolor.astype('uint8')

topcolor = np.transpose(topcolor, (1, 0, 2))
plt_image = cv2.cvtColor(topcolor, cv2.COLOR_BGR2RGB)
imgplot = plt.imshow(plt_image)

plt.show()
