from matplotlib.pyplot import plot
from numpy import random
from numpy.core.defchararray import mod
from numpy.lib.function_base import diff
import requests
from worldLoader import WorldSlice, setBlock
import cv2
import numpy as np
import matplotlib.pyplot as plt
from math import ceil, copysign, log2

# rect = (-64, -92 - 218-92, 80+64, 218-92)
# rect = (-32, -32, 64, 64)
# rect = (-200 + 255, -200 - 60, 401, 401)
# rect = (-32-64, -32-64-128, 64, 64)
rect = (-128, -128, 256, 256)

slice = WorldSlice(rect)

heightmap1 = np.array(slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"], dtype = np.uint8)
heightmap2 = np.array(slice.heightmaps["OCEAN_FLOOR"], dtype = np.uint8)

heightmap = np.minimum(heightmap1, heightmap2)



watermap = heightmap - heightmap2 + 128

bHM = cv2.blur(heightmap, (7, 7))

dx = cv2.Scharr(heightmap, cv2.CV_16S, 1, 0)
dy = cv2.Scharr(heightmap, cv2.CV_16S, 0, 1)
atan = np.arctan2(dx, dy, dtype=np.float64) * 5 / 6.283
atan = atan % 5
atan = atan.astype('uint8')

# finalHM = bHM + ((bHM.astype('int8') - 4 + 2) % 5 - 2) * -1
# # finalHM = bHM
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
# finalHM	= cv2.dilate(finalHM, kernel)
# finalHM	= cv2.erode(finalHM, kernel)

finalHM = cv2.medianBlur(heightmap, 7)

diffmap = finalHM.astype('float64') - heightmap.astype('float64')
# diffmap = diffmap * perlin
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
]
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
]
paletteReverseLookup = {}
for i in range(len(palette)):
    paletteReverseLookup[palette[i]] = i

topmap = np.zeros((rect[2],rect[3]), dtype='int')
topcolor = np.zeros(topmap.shape, dtype="int")


unknownBlocks = set()

for dx in range(rect[2]):
    for dz in range(rect[3]):
        for dy in range(5):
            x = rect[0] + dx
            z = rect[1] + dz
            y = int(heightmap1[(dx,dz)]) - dy

            blockCompound = slice.getBlockCompoundAt((x,y,z))
            
            if blockCompound != None:
                blockID = blockCompound["Name"].value
                if(blockID in ["minecraft:air", "minecraft:cave_air"]):
                    continue
                else:
                    numID = paletteReverseLookup.get(blockID, 0)
                    if(numID == 0): unknownBlocks.add(blockID)
                    # print("%s > %i" % (blockID, numID))
                    topmap[(dx, dz)] = numID
                    topcolor[(dx, dz)] = paletteColors[numID]
                    break

print("unknown blocks: %s" % str(unknownBlocks))

# topcolor = np.pad(topcolor, 16, mode='edge')
topcolor = cv2.merge(((topcolor) & 0xff, (topcolor >> 8) & 0xff, (topcolor >> 16) & 0xff))

off = np.expand_dims((diffx + diffy).astype("int"), 2)
# off = np.pad(off, ((16, 16), (16, 16), (0, 0)), mode='edge')
off = off.clip(-64, 64)
topcolor += off
topcolor = topcolor.clip(0, 255)

topcolor = topcolor.astype('uint8')

topcolor = np.transpose(topcolor, (1,0,2))
plt_image = cv2.cvtColor(topcolor, cv2.COLOR_BGR2RGB)
imgplot = plt.imshow(plt_image)

plt.show()

def runCommand(command):
    # print("running cmd %s" % command)
    response = requests.post('http://localhost:9000/command', bytes(command, "utf-8"))
    return response.text

# for i in range(100):
#     dx = int(random.randint(rect[2]/2) + rect[2]/4)
#     dz = int(random.randint(rect[3]/2) + rect[3]/4)
#     y = heightmap[(dx, dz)] + 1
#     x = rect[0] + dx
#     z = rect[1] + dz

#     wx = int(random.randint(5,9))
#     wxhalf = int(wx/2)
#     wz = int(random.randint(5,9))
#     wzhalf = int(wz/2)
#     h = int(random.randint(5,12))

#     extends = (x-wxhalf, y-2, z-wzhalf, x-wxhalf+wx, y-2+h, z-wzhalf+wz)
    
#     print(runCommand("fill %i %i %i %i %i %i minecraft:white_wool replace" % extends))


# plt.figure()
# topmap = topmap.astype('uint8')
# plt_image = cv2.cvtColor(topmap * 16, cv2.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)


# plotting
# diffmap_d = 128 + diffmap * (127 / 5)
# perlin_d = perlin * 255

# plt.figure()
# plt_image = cv2.cvtColor(diffmap_d.astype('uint8') + 128, cv2.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)


# plt_image = cv2.cvtColor(perlin_d.astype('uint8'), cv2.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)


# cut and fill #
# for dx in range(rect[2]):
#     for dz in range(rect[3]):
#         x = rect[0] + dx
#         z = rect[1] + dz
#         deltaY = diffmap[(dx, dz)]
#         if deltaY > 0:
#             # fill
#             for dy in range(deltaY):
#                 setBlock(x, heightmap[(dx, dz)] + dy, z, "minecraft:dirt")
#         elif deltaY < 0:
#             # cut
#             for dy in range(-1, deltaY - 1, -1):
#                 y = heightmap[(dx, dz)] + dy
#                 if y > 62:
#                     setBlock(x, y, z, "minecraft:air")
#                 else:
#                     setBlock(x, y, z, "minecraft:water") # TODO lol not like this



'''

5           d  0 7 2  0
4          dd +1 6 1 -1
3         ddd +2 5 0 -2
2        dddd -2 4 4  2
1       ddddd -1 3 3  1
0 ddddddddddd  0 2 2  0

+2 %5 -2 *-1

'''
