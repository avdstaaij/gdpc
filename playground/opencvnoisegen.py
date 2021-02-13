import cv2
from mapUtils import angleToCenter, distanceToCenter, fractalnoise, normalize
import numpy as np
import matplotlib.pyplot as plt


def get_image():
    # image2 = normalize(angleToCenter((300, 300)))
    image1 = 1 - normalize(distanceToCenter((300, 300)))
    image3 = normalize(fractalnoise((300, 300), 2))
    image = image1 * image3
    thres = 0.3
    image = np.clip((image - thres) * 100.0 + thres, 0, 1)

    # normalize

    image = image * 255
    image = image.astype(np.uint8)
    image = np.transpose(image)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # imgplot = plt.imshow(plt_image)

plt_image = get_image()

# toggle = True

def onclick(event):
    global plt_image
    plt_image = get_image()

    # toggle = not toggle
    event.canvas.figure.clear()

    axes = event.canvas.figure.gca()

    axes.imshow(plt_image)

    event.canvas.draw()

# plt.figure()
fig = plt.figure()
fig.canvas.mpl_connect('button_press_event', onclick)

plt.imshow(plt_image)
plt.show()

# plt.show()