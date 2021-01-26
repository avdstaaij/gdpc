import requests
import random
import math as m
import worldLoader
import asyncOperations


startPos = [-58, 64, 36]
neighborhood = [[-1,-1], [0,-1], [1,-1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]
wools = ["white_wool", "orange_wool", "magenta_wool", "light_blue_wool", "yellow_wool", "lime_wool", "pink_wool", "gray_wool", "light_gray_wool", "cyan_wool", "purple_wool", "blue_wool", "brown_wool", "green_wool", "red_wool", "black_wool"]

# def tentacle(x, y, z, length, block, dir):
#     for i in range(length):
#         asyncOperations.setBlock(x, y, z, block)
#         testedBlock = worldLoader.getBlock(x, y-1, z)
        
#         if testedBlock == "minecraft:air":
#             y -= 1
#         else:
#             moddir = (dir + random.randint(-1, 1)) % 8
#             delta = neighborhood[moddir]
#             x += delta[0]
#             z += delta[1]

# for i in range(8):  
#     tentacle(*startPos, 64, "minecraft:green_concrete", i)


for y in range(32):
    for x in range(32):
        for z in range(32):
            xx = x + startPos[0]
            yy = y + startPos[1]
            zz = z + startPos[2]
            asyncOperations.setBlockAsync(xx, yy, zz, wools[random.randint(0, len(wools)-1)])

asyncOperations.processRequests()
