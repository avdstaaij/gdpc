from ast import walk
import cv2
import numpy as np
import time
import wfc_implementation
import mapUtils
from worldLoader import WorldSlice
import math

tiles = np.array([
    [[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2]],[[2,2,1,0,0],[2,2,1,0,0],[1,1,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[2,2,2,2,2],[2,2,2,2,2]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,1,2,2],[0,0,1,2,2],[1,1,1,2,2],[2,2,2,2,2],[2,2,2,2,2]],[[0,1,1,1,0],[1,1,1,1,0],[1,1,1,1,1],[1,1,1,1,2],[0,0,1,2,2]],[[0,1,1,1,0],[1,1,1,1,0],[1,1,1,1,0],[1,1,1,0,0],[0,0,0,0,0]],[[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1],[2,2,2,2,2]],[[2,2,1,0,0],[2,1,1,0,0],[1,1,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,1,2,2],[0,1,1,2,2],[1,1,2,2,2],[2,2,2,2,2],[2,2,2,2,2]],[[0,0,1,2,2],[0,0,1,2,2],[0,0,1,1,1],[0,0,1,2,2],[0,0,1,2,2]],[[0,0,1,2,2],[1,1,1,2,2],[1,1,1,1,1],[1,1,1,2,2],[0,0,1,2,2]],[[0,0,1,2,2],[0,0,1,2,2],[0,0,1,2,2],[0,0,1,2,2],[0,0,1,2,2]],[[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1],[2,2,2,2,2],[2,2,2,2,2]],[[0,0,1,2,2],[1,1,1,2,2],[1,2,2,2,2],[1,1,1,2,2],[0,0,1,2,2]],[[2,2,1,2,2],[2,2,1,2,2],[1,1,1,1,1],[2,2,2,2,2],[2,2,2,2,2]],[[0,1,1,1,0],[0,1,2,1,0],[0,1,2,1,0],[0,1,2,1,0],[0,1,1,1,0]],[[0,0,1,2,2],[0,0,1,2,2],[1,1,1,1,1],[2,2,2,2,2],[2,2,2,2,2]],[[2,2,1,0,0],[2,2,1,0,0],[1,1,1,1,1],[2,2,2,2,2],[2,2,2,2,2]],[[0,0,1,2,2],[0,1,1,1,2],[1,1,1,1,1],[2,1,1,1,0],[2,2,1,0,0]]])


tiles = wfc_implementation.expandRotations(tiles)

# w = h = 15
w = h = 5
layers = 3
area = [700, -750, w*5*3, h*5*3]
slice = WorldSlice(area)
strctElmt3x3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
# crossKernel3x3 = np.array([[0,1,0],[1,1,1],[0,1,0])
kernel1x3 = np.array([[1,1,1]])
kernel3x1 = np.transpose(kernel1x3)
kernel3x3 = kernel3x1 * kernel1x3
heightmap = np.array(slice.heightmaps["WORLD_SURFACE"], dtype = np.uint8)

floorWallMappings = [
#   [f,w,c,s] (floor, wall, ceiling, space)
    [1,1,1], # 0: wall
    [1,0,0], # 1: walkway
    [0,0,0], # 2: void
    [1,0,1],  # 3: floor/ceiling
    [1,1,1]  # 4: seawall
]

absoluteFloor = 60

for i in range(layers):
    image = wfc_implementation.runWFC(tiles, w, h, 2)
    image = image.astype('uint8')
    image = cv2.resize(image, (area[2],area[3]), interpolation=cv2.INTER_NEAREST)

    buildings = (image == 0).astype(np.uint8)
    void = (image == 2).astype(np.uint8)
    railings = void - cv2.erode(void, strctElmt3x3)
    hrailings = (cv2.filter2D(railings, -1, kernel1x3) == 3).astype(np.uint8)
    vrailings = (cv2.filter2D(railings, -1, kernel3x1) == 3).astype(np.uint8)
    crailings = railings - hrailings - vrailings
    buildingsdilated = cv2.dilate(buildings, strctElmt3x3)
    walkwdeco = cv2.dilate(buildings, strctElmt3x3) - buildings
    walkwdx = (cv2.filter2D(buildings, cv2.CV_16S, np.array([[-1,0,1]])) * walkwdeco + 1) # 0,1,2
    walkwdy = (cv2.filter2D(buildings, cv2.CV_16S, np.array([[-1],[0],[1]])) * walkwdeco + 1) # # 0,1,2
    walkwMap = walkwdx * 3 + walkwdy
    walkwoc = (cv2.filter2D(buildingsdilated, -1, kernel3x3) == 4) * walkwdeco
    walkwoc = (cv2.dilate(walkwoc, strctElmt3x3) - walkwoc) * walkwdeco
    # walls: 1,0 1,2 0,1 2,1  =  3, 5, 1, 7
    # neutral: 4
    # inner corners: 0,0 0,2 2,0 2,2  = 0, 2, 6, 8

    # make it so that walkWMap is '10' at outer corners:
    walkwMap = np.where(walkwoc, 10, walkwMap)

    mapUtils.visualize(walkwMap, walkwoc)

    image = image + cv2.erode(buildings, strctElmt3x3) * 3 # basically insides of buildings (0) to floor/ceiling (3)
    cv2.rectangle(image, (0,0), (image.shape[0]-1, image.shape[1]-1), (4), 1) # build seawall

    # mapUtils.visualize(image, railings, vrailings, hrailings, crailings)
    mapUtils.visualize(image)

    startHeights = [
        absoluteFloor - 20 if i == 0 else absoluteFloor + 12 * i,
        absoluteFloor + 12 * i + 1,
        absoluteFloor + 12 * i + 12,
        absoluteFloor + 12 * (i) + 13
    ] # [floor, wall, ceiling, space, next level]

    # cardinals = ["east", "south", "north", "west"]
    cardinals = ["north", "west", "east", "south"]

    # do construction
    for x in range(area[2]):
        for z in range(area[3]):
            yTerrain = int(heightmap[(x,z)])
            buildType = int(image[(x,z)])

            for j in range(len(startHeights) - 1):
                buildingBlock = "air" if floorWallMappings[buildType][j] == 0 else "gray_concrete" if buildType == 0 or buildType == 3 else "blackstone"
                y1 = startHeights[j]
                # TODO this is a hack to allwo overlapping layers, this will not work long term!
                if j == 0 and buildingBlock == "air":
                    y1 += 1
                y2 = startHeights[j + 1]
                if buildType == 4:
                    y2 = min(y2, yTerrain)
                for y in range(y1, y2):
                    mapUtils.placeBlockBatched(area[0] + x, y, area[1] + z, buildingBlock, 1000)
            
            # railings
            ry = startHeights[1]
            if hrailings[(x,z)]:
                mapUtils.placeBlockBatched(area[0] + x, ry, area[1] + z, "end_rod[facing=north]", 1000)
            elif vrailings[(x,z)]:
                mapUtils.placeBlockBatched(area[0] + x, ry, area[1] + z, "end_rod[facing=east]", 1000)
            elif crailings[(x,z)]:
                for i in range(2):
                    mapUtils.placeBlockBatched(area[0] + x, ry - 1 + i, area[1] + z, "gray_concrete", 1000)
            # walkway decoration
            wmapVal = int(walkwMap[(x,z)])
            if wmapVal % 2 == 1:
                # wall adjacent
                dir = int((wmapVal - 1) / 2)
                cdir1 = cardinals[dir]
                cdir2 = cardinals[(dir + 2) % 4]
                mapUtils.placeBlockBatched(area[0] + x, ry, area[1] + z, "polished_blackstone_stairs[facing=%s]" % cdir1, 1000)
                mapUtils.placeBlockBatched(area[0] + x, ry+1, area[1] + z, "end_rod[facing=%s]" % cdir2, 1000)
                mapUtils.placeBlockBatched(area[0] + x, ry+2, area[1] + z, "polished_blackstone_slab", 1000)
            elif wmapVal % 2 == 0 and wmapVal != 4:
                # inner corner
                for i in range(3):
                    mapUtils.placeBlockBatched(area[0] + x, ry + i, area[1] + z, "polished_blackstone", 1000)

    mapUtils.sendBlocks() # send remaining blocks in buffer