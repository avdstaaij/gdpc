import cv2
import matplotlib.pyplot as plt
import numpy as np

import interfaceUtils
from worldLoader import WorldSlice
import blockColors

rect = (0, 0, 128, 128)  # default build area of example.py

buildArea = interfaceUtils.requestBuildArea()
if buildArea != -1:
    x1 = buildArea["xFrom"]
    z1 = buildArea["zFrom"]
    x2 = buildArea["xTo"]
    z2 = buildArea["zTo"]
    # DEBUG: print(buildArea)
    rect = (x1, z1, x2 - x1, z2 - z1)
    # DEBUG: print(rect)

slice = WorldSlice(rect)

heightmap1 = np.array(
    slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"], dtype=np.uint8)
heightmap2 = np.array(slice.heightmaps["OCEAN_FLOOR"], dtype=np.uint8)
heightmap = np.minimum(heightmap1, heightmap2)

dx = cv2.Scharr(heightmap, cv2.CV_16S, 1, 0)
dy = cv2.Scharr(heightmap, cv2.CV_16S, 0, 1)

# diff
img = heightmap
diffx = cv2.Scharr(img, cv2.CV_16S, 1, 0)
diffy = cv2.Scharr(img, cv2.CV_16S, 0, 1)

palette = {}

for hex, blocks in blockColors.PALETTE.items():
    for block in blocks:
        palette[block] = hex

topcolor = np.zeros((rect[2], rect[3]), dtype='int')

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
                if blockID in blockColors.TRANSPARENT:
                    continue
                else:
                    if blockID not in palette:
                        unknownBlocks.add(blockID)
                    else:
                        topcolor[(dx, dz)] = palette[blockID]
                    break

if len(unknownBlocks) > 0:
    print("Unknown blocks: " + str(unknownBlocks))

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

plt.imshow(plt_image)
plt.show()
