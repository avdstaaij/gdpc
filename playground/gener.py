from playground.asyncOperations import setBlockAsync
from numpy.core.defchararray import array
from mapUtils import distanceToCenter
from math import cos, sin
import numpy as np
import requests
from worldLoader import WorldSlice, setBlock
import random

# buffer for the request body
blockBuffer = ""

# very basic undo buffer, doesn't actually undo :p
deleteBuffer = "" 

# write a block update to the buffer
def registerSetBlock(x, y, z, str):
    global blockBuffer, deleteBuffer
    blockBuffer += '~%i ~%i ~%i %s \n' % (x, y, z, str)
    deleteBuffer += '~%i ~%i ~%i %s \n' % (x, y, z, "air")

# send the buffer to the server and clear it
def sendBlocks(x, y, z):
    global blockBuffer
    url = 'http://localhost:9000/blocks?x=%i&y=%i&z=%i' % (x, y, z)
    response = requests.put(url, blockBuffer)
    blockBuffer = ""
    return response.text

def deleteBlocks(x, y, z):
    global deleteBuffer
    url = 'http://localhost:9000/blocks?x=%i&y=%i&z=%i' % (x, y, z)
    response = requests.put(url, deleteBuffer)
    deleteBuffer = ""
    return response.text

area = [108, -119, 128, 128]

slice = WorldSlice(area)

heightmap1 = np.array(slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"], dtype = np.uint8)
heightmap2 = np.array(slice.heightmaps["OCEAN_FLOOR"], dtype = np.uint8)

heightmap = np.minimum(heightmap1, heightmap2)
watermap = heightmap - heightmap2 + 128



ringNBH = [[x,y] for x in range(-3, 4) for y in range(-3, 4)]
ringNBH = [a for a in filter(lambda a : max(abs(a[0]), abs(a[1])) == 3, ringNBH)]

# walker
minVal = max(63, np.amin(heightmap))
tupleList = np.where(heightmap == minVal)
listOfCordinates = list(zip(tupleList[0], tupleList[1]))
if len(listOfCordinates) == 0:
    minVal = np.amin(heightmap)
    tupleList = np.where(heightmap == minVal)
    listOfCordinates = list(zip(tupleList[0], tupleList[1]))

p = listOfCordinates[random.randint(0, len(listOfCordinates) - 1)]

p = [int(p[0]), int(p[1])]
print(p)

# p = [64, 64] # relative !!! coordinates

for i in range(5):
    registerSetBlock(p[0], minVal + i, p[1], "stone_bricks")
    
sendBlocks(area[0], 0, area[1])


def inBounds(x, z):
    return x >= 0 and z >= 0 and x < area[2] and z < area[3]

def hmTest(x, z):
    if not inBounds(x, z):
        return 255
    else:
        return int(heightmap[(x, z)])

def placeSlab(x, y, z):
    for dy in range(4):
        block = 'yellow_wool' if dy == 0 else 'air'
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                registerSetBlock(x+dx, y+dy, z+dz, block)
    sendBlocks(0, 0, 0)

pp = [0, 0]
for d in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
    for i in range(127):
        registerSetBlock(pp[0], hmTest(*pp), pp[1], "white_concrete")
        pp[0] += d[0]
        pp[1] += d[1]
sendBlocks(area[0], 0, area[1])

for j in range(1):
    delta = ringNBH[0]
    for i in range(100):
        heightHere = hmTest(*p)
        placeSlab(area[0] + p[0], heightHere-1, area[1] + p[1])

        # registerSetBlock(p[0], heightHere-1, p[1], 'red_wool')

        hdiff = lambda d : hmTest(p[0] + d[0], p[1] + d[1])
        diffs = [hdiff(d) - heightHere for d in ringNBH]

        candidates = list(filter(lambda a : a > 0, diffs))
        if(len(candidates) > 0): 
            minDiff = min(candidates)
            deltaIndeces = list(filter(lambda a : diffs[a] == minDiff, range(len(ringNBH))))
            index = deltaIndeces[random.randint(0, len(deltaIndeces) - 1)]
            delta = ringNBH[index]
        p[0] += delta[0]
        p[1] += delta[1]


# sendBlocks(area[0], 0, area[1])

# input()
# deleteBlocks(area[0], 0, area[1])