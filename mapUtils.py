from matplotlib.pyplot import plot
from numpy import random
from numpy.core.shape_base import block
from numpy.lib.function_base import diff
import requests
from worldLoader import WorldSlice
import cv2
import numpy as np
import matplotlib.pyplot as plt
from math import atan2, ceil, log2
import time

rng = np.random.default_rng()

minecraft_colors  = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]


def fractalnoise(shape, minFreq=0, maxFreq=0):
    """creates a array of size <shape> filled with perlin-noise (might not technically be perlin noise?). The noise is created by starting with a 1x1 noise, upsampling it by 2, then adding a 2x2 noise, upsampling again, then 4x4, etc. until a big enough size is reached and it's cropped down to the correct size.
    Each additional noise layer has half the amplitude of the previous, so that small features aren't over-emphasized.

    Args:
        shape (tuple): size of the output array, must be 2d. For example (400,200)

    Raises:
        Raises ValueError if <shape> is not twodimensional

    Returns:
        ndarray of shape <shape>, of type float64 with values between 0 and 1
    """
    if len(shape) != 2:
        raise ValueError("Shape needs to have length 2. Only 2d noise is supported")

    depth = ceil(log2(max(shape)))

    noise = np.zeros((1,1), dtype = np.float64)

    for i in range(depth):
        noise = cv2.pyrUp(noise)
        if i >= minFreq and i < (depth - maxFreq):
            # noise = rng.integers(0, 128**(1/(i+1)), img.size, dtype = 'uint8')
            noiseLayer = rng.random(noise.size, dtype = np.float64)
            noiseLayer = noiseLayer * 2**(-(i+1))
            # noise = np.random.normal(0, 1, img.size)
            noiseLayer = noiseLayer.reshape(noise.shape)
            noise = cv2.add(noise, noiseLayer)

    # for i in range(3):
    #     perlin = cv2.pyrUp(perlin)

    # perlin = (perlin - perlin.min()) / (perlin.max() - perlin.min())
    noise = noise[0:shape[0], 0:shape[1]]
    noise = noise.clip(0, 1)

    return noise
    # perlin = perlin * 255
    # perlin = perlin.astype(np.uint8)

def distanceToCenter(shape):
    if len(shape) != 2:
        raise ValueError("Shape needs to have length 2. Only 2d is supported")
    
    return np.array([[((x/shape[0]-0.5)**2 + (y/shape[1]-0.5)**2)**0.5 for x in range(shape[0])] for y in range(shape[1])])

def angleToCenter(shape):
    if len(shape) != 2:
        raise ValueError("Shape needs to have length 2. Only 2d is supported")
    
    return np.array([[atan2(y/shape[1]-0.5, x/shape[0]-0.5) for x in range(shape[0])] for y in range(shape[1])])

def normalize(array):
    return (array - array.min()) / (array.max() - array.min())

def visualize(*arrays, title=None, autonormalize=True):
    for array in arrays:
        if autonormalize:
            array = (normalize(array) * 255).astype(np.uint8)

        plt.figure()
        if title:
            plt.title(title)
        plt_image = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        imgplot = plt.imshow(plt_image)
    plt.show()

# def showAnimationFrame(array, title=None, autonormalize=True):
#     time.sleep(0.05)
#     if autonormalize:
#         array = (normalize(array) * 255).astype(np.uint8)
#     # frame = cv2.resize(frame, (500,500), interpolation=cv2.INTER_NEAREST)
#     cv2.imshow(title, array)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

def calcGoodHeightmap(worldSlice):    
    hm_mbnl = np.array(worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"], dtype = np.uint8)
    heightmapNoTrees = hm_mbnl[:]
    area = worldSlice.rect

    for x in range(area[2]):
        for z in range(area[3]):
            while True:
                y = heightmapNoTrees[x, z]
                block = worldSlice.getBlockAt((area[0] + x, y - 1, area[1] + z))
                if block[-4:] == '_log':
                    heightmapNoTrees[x,z] -= 1
                else:
                    break

    return np.array(np.minimum(hm_mbnl, heightmapNoTrees))
