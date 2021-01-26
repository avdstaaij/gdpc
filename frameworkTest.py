from matplotlib.pyplot import plot
from numpy import random
from worldLoader import WorldSlice
import cv2
import numpy as np
import matplotlib.pyplot as plt

# you can edit the area here
# (x, y, width, height)
rect = (-32, -32, 64, 64)

slice = WorldSlice(rect)
# heightmap = np.zeros((rect[2],rect[3]), dtype = np.uint8)

# for lx in range(rect[2]):
#     x = rect[0] + lx
#     for lz in range(rect[3]):
#         z = rect[1] + lz
#         for y in range(127, -1, -1):
#             block = slice.getBlockAt((x, y, z))
#             if block != None and block["Name"].value != "minecraft:air":
#                 heightmap[lx, lz] = y # + random.uniform(0, 16)
#                 break

heightmap = np.array(slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"], dtype = np.uint8)
heightmap2 = np.array(slice.heightmaps["OCEAN_FLOOR"], dtype = np.uint8)

watermap = 255 - ((heightmap+1 >> 6) % 2) * 255



# # clip and convert. Simulates minecraft conditions (0 - 255, terrain between 64 and 128)
# img = (img - img.min()) / (img.max() - img.min())
# img = img.clip(0, 1)
# orig = img
# img2 = img.astype(np.uint8) >> 4 << 4
# img = (1-orig) * img2 + (orig) * img
# # img = (64 + img * 64)
# img = img * 255
# img = img.astype(np.uint8)

# first derivative building criterium
# Scharr: 32 is about 1 steepness, i think
# for i in range(4):
img = heightmap
dx = cv2.Scharr(img, cv2.CV_16S, 1, 0)
dy = cv2.Scharr(img, cv2.CV_16S, 0, 1)
dmag = np.absolute(dx) + np.absolute(dy)
# thres = 32
# dmag = dmag - thres
dmag = dmag.clip(0, 255)
dmag = dmag.astype('uint8')
# dmag = dmag * 255

atan = np.arctan2(dx, dy, dtype=np.float64) * (360/6.283)
atan = atan % 360
atan = atan / 2
atan = atan.astype('uint8')
# atan = atan * 255 / 6.283
atan = cv2.merge((
    np.minimum(atan, 255 - watermap), # hue
    np.ones(atan.shape, dtype=atan.dtype) * 255, # saturation
    np.maximum(np.ones(atan.shape, dtype=atan.dtype) * dmag, watermap) # value
    ))
atan = cv2.cvtColor(atan, cv2.COLOR_HSV2RGB)

# atan = atan.clip(0, 255)
# atan = atan.astype('uint8')
# Display the images


# cv2.imshow('dst', dmag)
# plt_image = cv2.cvtColor(dmag, cv2.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)
# # plt.title("Heightmap")
# # plt.show()
# plt.figure()

plt_image = cv2.cvtColor(atan, cv2.COLOR_BGR2RGB)
imgplot = plt.imshow(plt_image)

# plt.figure()
# plt_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)

# plt.figure()
# plt_image = cv2.cvtColor(watermap, cv2.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)

# plt.figure()
# hmdiff = heightmap - heightmap2 + 128
# plt_image = cv2.cvtColor(hmdiff, cv2.COLOR_BGR2RGB)
# imgplot = plt.imshow(plt_image)

plt.show()


# cv2.imshow('a', img)
# cv2.waitKey(0)
# plt.waitforbuttonpress()




print("blocks:")

# for i in range(0, 100):
#     blockCompound = slice.getBlockAt((0, i, 0))
#     if blockCompound != -1:
#         print(blockCompound["Name"])
#     else:
#         print("nothing")

# print(slice.getBlockAt((0, 64, 0)))
# print(slice.getBlockAt((0, 68, 0)))
# print(slice.getBlockAt((0, 70, 0)))


# for i in         range(-1, 1):
#     for j in     range(0, 1):
#         for k in range(-1, 1):
#             comp = slice.getBlockAt((i, 68 + j, k ))
#             # if not str(comp["Name"]) in ["minecraft:water", "minecraft:air", "minecraft:oak_planks"]:
#             print(str((i, j, k)) + " " + str(comp["Name"]))



# print(slice.getBlockAt((0, 0, 0)))
# print(slice.getBlockAt((0, 0, 0)))