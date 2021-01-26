from mapUtils import distanceToCenter, fractalnoise, normalize, registerSetBlock, runCommand, sendBlocks, minecraft_colors
from worldLoader import WorldSlice
import numpy as np
import random

area = np.array([-53, 3, 128, 128])
slice = WorldSlice(area)

heightmap1 = np.array(slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"], dtype = np.uint8)
heightmap2 = np.array(slice.heightmaps["OCEAN_FLOOR"], dtype = np.uint8)

heightmap = np.minimum(heightmap1, heightmap2)
watermap = heightmap - heightmap2 + 128

# setup
nbh = [[i,j] for i in range(-1, 2) for j in range(-1, 2)]
nbh = np.array(list(filter(lambda a : not (a[0] == 0 and a[1] == 0), nbh)))

def inBounds(x, z):
    return x >= 0 and z >= 0 and x < area[2] and z < area[3]

def hmTest(x, z):
    if not inBounds(x, z):
        return 255
    else:
        h = int(heightmap[(x, z)])
        if h < 63:
            return 0
        return h

# hacky
backlogLength = 0

def placeBlockBatched(x, y, z, block, limit=100):
    global backlogLength
    registerSetBlock(x, y, z, block)
    backlogLength += 1
    if backlogLength >= limit:
        backlogLength = 0
        sendBlocks(area[0], 0, area[1])

def sendRemainingBlocks():
    if backlogLength > 0:
        sendBlocks(area[0], 0, area[1])

def listWhere(array): 
    tupleList = np.where(array)
    return list(zip(tupleList[0], tupleList[1]))

distToCenter = distanceToCenter(heightmap.shape)
invDistToCenter = 1 - distToCenter

largenoise = normalize(fractalnoise(heightmap.shape, 2, 3))

# working maps
colormap = np.ones(heightmap.shape, dtype=np.int) * -1
backtrackmap = np.zeros([*heightmap.shape, 2], dtype=np.int)

# find start position
print(heightmap[64,64])
startConditions = (distToCenter < 0.25) * (heightmap > 64) * invDistToCenter
maxVal = np.amax(startConditions)
tupleList = np.where(startConditions == maxVal)
possibleStartCoords = list(zip(tupleList[0], tupleList[1]))
startpos = possibleStartCoords[random.randint(0, len(possibleStartCoords) - 1)]
# p = np.array([int(startpos[0]), int(startpos[1])])
p = np.array(startpos)

# startpos = np.array([int(area[2] / 2), int(area[3] / 2)])

backfuck = [] # TODO: rename

# do a flood fill to build sense of geometry for the place
# TODO: deal with overhangs (right now its 100% heighmap based)
backfuck.append(startpos)
colormap[tuple(startpos)] = 0

for i in range(1000000):
    if len(backfuck) == 0:
        break

    # p = backfuck.pop(0) # actually dequeue
    p = backfuck.pop(random.randrange(len(backfuck))) # random dequeue
    heightHere = hmTest(*p)
    diffs = [hmTest(p[0] + d[0], p[1] + d[1]) - heightHere for d in nbh]
    filterFunc = lambda index: abs(diffs[index]) <= 1
    deltaIndeces = list(filter(filterFunc, range(len(nbh))))
    color = colormap[tuple(p)]
    newcolor = (color + random.randint(0, 1)) % len(minecraft_colors)

    for index in deltaIndeces:
        delta = nbh[index]
        newp = p + delta
        if colormap[tuple(newp)] == -1:
            backfuck.append(newp)
            colormap[tuple(newp)] = newcolor # mark as visited
            backtrackmap[tuple(newp)] = delta * -1
            # y = hmTest(*newp) - 1
            # placeBlockBatched(newp[0], y, newp[1], '%s_concrete' % minecraft_colors[newcolor])
    

# smallerHeightmap = heightmap[32:area[2]-32, 32:area[3]-32]

# get maximum height that is also within 75% radius of center and was visited previously
for variation in range(2):
    if variation == 0:
        testspace = (distToCenter < 0.36) * (colormap >= 0) * (255 - heightmap)
    else:
        testspace = (distToCenter < 0.36) * (colormap >= 0) * heightmap
    
    maxVal = np.amax(testspace) 

    tupleList = np.where(testspace == maxVal)
    listOfCordinates = list(zip(tupleList[0], tupleList[1]))

    if len(listOfCordinates) == 0:
        raise ValueError("WHAT THE FUCK IS GOING ON, NO!")

    p = listOfCordinates[random.randint(0, len(listOfCordinates) - 1)]
    p = [int(p[0]), int(p[1])]
    print(p)
    y = hmTest(*p)
    placeBlockBatched(p[0], y, p[1], "obsidian", limit=1)

    delta = backtrackmap[tuple(p)]
    counter = 0
    while delta.any(): # check if its not just [0,0]
        p = p + delta
        delta = backtrackmap[tuple(p)]
        h = hmTest(*p)
        doTorch = counter % 8 == 0
        counter += 1
        for dx in range(2):
            for dz in range(2):
                locp = p - delta * [dx, dz]
                placeBlockBatched(locp[0], h - 1, locp[1], "mossy_cobblestone")
                placeBlockBatched(locp[0], h, locp[1], "torch" if doTorch else "air")

    sendRemainingBlocks()


p = np.array([0, 0])
for d in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
    for i in range(127):
        y = hmTest(*p)
        placeBlockBatched(p[0], y, p[1], "iron_block")
        p += d

sendRemainingBlocks()

testspace = (distToCenter < 0.4)
ps = listWhere(testspace)

thickness = 12
chasm = (largenoise > 0.9) & (heightmap2 > 62)
offset = (~chasm) * thickness
startheight = heightmap2 - offset
endheight = 20 + distToCenter * 20

for p in ps:
    sh = int(startheight[tuple(p)])
    eh = int(endheight[tuple(p)])
    for i in range(sh, eh, -1):
        placeBlockBatched(p[0], i, p[1], "air")

sendRemainingBlocks()

print(runCommand('kill @e[type=minecraft:item]'))
