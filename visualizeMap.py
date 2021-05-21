# ! /usr/bin/python3
"""### Displays a map of the build area."""
__all__ = ['WorldSlice']
__version__ = 'v4.2_dev'

import cv2
import interface
import lookup
import matplotlib.pyplot as plt
import numpy as np
from toolbox import loop2d
from worldLoader import WorldSlice

if __name__ == '__main__':
    # see if a different build area was defined ingame
    x1, _, z1, x2, _, z2 = interface.requestBuildArea()

    # load the world data and extract the heightmap(s)
    slice = WorldSlice(x1, z1, x2, z2)

    heightmap = np.array(slice.heightmaps["OCEAN_FLOOR"], dtype=int)

    # calculate the gradient (steepness)
    decrementor = np.vectorize(lambda a: a - 1)
    cvheightmap = np.clip(decrementor(heightmap), 0, 255).astype(np.uint8)
    gradientX = cv2.Scharr(cvheightmap, cv2.CV_16S, 1, 0)
    gradientY = cv2.Scharr(cvheightmap, cv2.CV_16S, 0, 1)

    # create a dictionary mapping block ids ("minecraft:...") to colors
    palette = lookup.PALETTELOOKUP

    # create a 2d map containing the surface block colors
    topcolor = np.zeros((x2 - x1 + 1, z2 - z1 + 1), dtype='int')
    unknownBlocks = set()

    for x, z in loop2d(x1, z1, x2, z2):
        # check up to 5 blocks below the heightmap
        for dy in range(5):
            # calculate absolute coordinates
            y = int(heightmap[(x, z)]) - dy

            blockID = slice.getBlockAt(x, y, z)
            if blockID in lookup.MAPTRANSPARENT:
                # transparent blocks are ignored
                continue
            else:
                if blockID not in palette:
                    # unknown blocks remembered for debug purposes
                    unknownBlocks.add(blockID)
                else:
                    topcolor[(x, z)] = palette[blockID]
                break

    if len(unknownBlocks) > 0:
        print("Unknown blocks: " + str(unknownBlocks))

    # separate the color map into three separate color channels
    topcolor = cv2.merge(((topcolor) & 0xff, (topcolor >> 8)
                          & 0xff, (topcolor >> 16) & 0xff))

    # calculate a brightness value from the gradient
    brightness = np.expand_dims((gradientX + gradientY).astype("int"), 2)
    brightness = brightness.clip(-64, 64)

    topcolor += brightness
    topcolor = topcolor.clip(0, 255)

    # display the map
    topcolor = topcolor.astype('uint8')
    topcolor = np.transpose(topcolor, (1, 0, 2))
    plt_image = cv2.cvtColor(topcolor, cv2.COLOR_BGR2RGB)

    plt.imshow(plt_image)
    plt.show()
