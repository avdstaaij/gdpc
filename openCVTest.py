import cv2
import numpy as np

rng = np.random.default_rng()

img = np.zeros((2,2), dtype = np.float64)

for i in range(4):
    img = cv2.pyrUp(img)
    # noise = rng.integers(0, 128**(1/(i+1)), img.size, dtype = 'uint8')
    noise = rng.random(img.size, dtype = np.float64)
    noise = noise * 2**(-(i+1))
    # noise = np.random.normal(0, 1, img.size)
    noise = noise.reshape(img.shape)
    img = cv2.add(noise, img)

for i in range(3):
    img = cv2.pyrUp(img)

# clip and convert. Simulates minecraft conditions (0 - 255, terrain between 64 and 128)
img = (img - img.min()) / (img.max() - img.min())
img = img.clip(0, 1)
orig = img
img2 = img.astype(np.uint8) >> 4 << 4
img = (1-orig) * img2 + (orig) * img
# img = (64 + img * 64)
img = img * 255
img = img.astype(np.uint8)

# first derivative building criterium
# Scharr: 32 is about 1 steepness, i think
# for i in range(4):
dx = cv2.Scharr(img, cv2.CV_16S, 1, 0)
dy = cv2.Scharr(img, cv2.CV_16S, 0, 1)
dmag = np.absolute(dx) + np.absolute(dy)
thres = 32
dmag = dmag - thres
dmag = dmag.clip(0, 1)
dmag = dmag * 255
dmag = dmag.astype('uint8')
cv2.imshow('dst', dmag)

# Display the images
cv2.imshow('a', img); cv2.waitKey(0)

cv2.destroyAllWindows()