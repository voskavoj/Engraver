import math
from PIL import Image, ImageOps, ImageFilter
from logging import info as log
from logging import warning as warn
from logging import error as error
import cv2

# settings
MAX_PWR = 100
MIN_PWR = 255
LEN_X = 30  # mm
RES_X = 10  # pix/mm

# open image file
image = Image.open("test.jpg")
org_size_x, org_size_y = image.size
aspect_ratio = org_size_x / org_size_y

# resize
size_x = round(LEN_X * RES_X)
size_y = round(size_x * 1 / aspect_ratio)
log(size_x, size_y)

if size_x > org_size_x or size_y > org_size_y:
    warn("New image is larger")

image = image.resize((size_x, size_y))

# convert to BW and invert
image = ImageOps.grayscale(image)
image = ImageOps.invert(image)

# map to min, max power
image_pixels = image.load()
for i in range(1, size_x):
    for j in range(1, size_y):
        val = image_pixels[i, j]
        # normalized value = (value / OLD_MAX) * NEW_MAX - SHIFT, where NEW_MAX is from 0
        image_pixels[i, j] = round(((val / 255) * (MAX_PWR - MIN_PWR)) + MIN_PWR)

# to GCODE
image.show()


import cv2
import numpy as np

# Let's load a simple image with 3 black squares
image = cv2.imread('test2.png')

# Grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Find Canny edges
edged = cv2.Canny(gray, 30, 200)
cv2.waitKey(0)

# Finding Contours
# Use a copy of the image e.g. edged.copy()
# since findContours alters the image
contours, hierarchy = cv2.findContours(edged,
                                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#
# cv2.imshow('Canny Edges After Contouring', edged)
# cv2.waitKey(0)

print("Number of Contours found = " + str(len(contours)))

# Draw all contours
# -1 signifies drawing all contours
cv2.drawContours(image, contours, -1, (0, 0, 255), 1)

cv2.imshow('Contours', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
