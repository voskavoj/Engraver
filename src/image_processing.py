from PIL import Image, ImageOps
import cv2
import numpy as np

from logging import info as log
from logging import warning as warn


def _open_and_resize_image(filename, len_x, res_x):
    image = Image.open(filename)
    org_size_x, org_size_y = image.size
    aspect_ratio = org_size_x / org_size_y

    # resize
    size_x = round(len_x * res_x)
    size_y = round(size_x * 1 / aspect_ratio)
    log(size_x, size_y)

    if size_x > org_size_x or size_y > org_size_y:
        warn("New image is larger")

    image = image.resize((size_x, size_y))

    return image


def process_image_for_drawing(filename, len_x, res_x, max_pwr, min_pwr, **kwargs):
    image = _open_and_resize_image(filename, len_x, res_x)

    size_x, size_y = image.size
    # convert to BW and invert
    image = ImageOps.grayscale(image)
    image = ImageOps.invert(image)

    # map to min, max power
    image_pixels = image.load()
    for i in range(size_x):
        for j in range(size_y):
            val = image_pixels[i, j]
            # normalized value = (value / OLD_MAX) * NEW_MAX - SHIFT, where NEW_MAX is from 0
            image_pixels[i, j] = round(((val / 255) * (max_pwr - min_pwr)) + min_pwr)

    return image


def process_image_for_cut(filename, len_x, res_x, **kwargs):
    image = _open_and_resize_image(filename, len_x, res_x)

    image = np.asarray(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find Canny edges
    edged = cv2.Canny(image, 30, 200)

    # Finding Contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    log("Number of Contours found = " + str(len(contours)))
    # for c in contours:
    #     np.savetxt("foo" + str(len(c)) + ".csv", c[:,0,:], delimiter=";")

    # Draw all contours
    image = np.ones(image.shape[:2], dtype="uint8") * 255
    cv2.drawContours(image, contours, -1, (0, 0, 0), 1)

    image = Image.fromarray(image)
    image = ImageOps.grayscale(image)

    list_of_contours = list()
    for c in contours:
        list_of_contours.extend(c[:, 0, :].tolist())

    return image, list_of_contours
