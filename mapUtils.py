from matplotlib.pyplot import plot
from numpy import random
from numpy.lib.function_base import diff
import requests
from worldLoader import WorldSlice, setBlock
import cv2
import numpy as np
import matplotlib.pyplot as plt
from math import atan2, ceil, log2

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


# BLOCK BUFFER STUFF

blockBuffer = ""

# clear the block buffer
def clearBlockBuffer():
    global blockBuffer
    blockBuffer = ""

# write a block update to the buffer
def registerSetBlock(x, y, z, str):
    global blockBuffer
    blockBuffer += '~%i ~%i ~%i %s \n' % (x, y, z, str)

# send the buffer to the server and clear it
def sendBlocks(x, y, z):
    global blockBuffer
    url = 'http://localhost:9000/blocks?x=%i&y=%i&z=%i&doBlockUpdates=false' % (x, y, z)
    response = requests.put(url, blockBuffer)
    blockBuffer = ""
    return response.text


def runCommand(command):
    # print("running cmd %s" % command)
    url = 'http://localhost:9000/command'
    response = requests.post(url, bytes(command, "utf-8"))
    return response.text

def visualize(*arrays, title=None, autonormalize=True):
    for array in arrays:
        if autonormalize:
            array = (normalize(array) * 255).astype(np.uint8)

        plt.figure()
        if title:
            plt.title("trees bro")
        plt_image = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        imgplot = plt.imshow(plt_image)
    plt.show()