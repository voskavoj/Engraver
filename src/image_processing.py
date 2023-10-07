from PIL import Image, ImageOps, ImageDraw
import cv2
import numpy as np

from logging import warning as warn


def _open_and_resize_image(filename, len_x, res_x):
    image = Image.open(filename)
    org_size_x, org_size_y = image.size
    aspect_ratio = org_size_x / org_size_y

    # resize
    size_x = round(len_x * res_x)
    size_y = round(size_x * 1 / aspect_ratio)
    print(size_x, size_y)

    if size_x > org_size_x or size_y > org_size_y:
        warn("New image is larger")

    image = image.resize((size_x, size_y))
    image = ImageOps.mirror(image)  # flip image to preserve actual alignment

    return image


def process_image_for_drawing(filename, len_x, res_x, max_pwr, min_pwr, **kwargs):
    image = _open_and_resize_image(filename, len_x, res_x)

    size_x, size_y = image.size
    # convert to BW and invert
    image = ImageOps.grayscale(image)
    image = ImageOps.invert(image)

    return image


def process_image_for_cut(filename, len_x, res_x, **kwargs):
    image = _open_and_resize_image(filename, len_x, res_x)

    image = np.asarray(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find Canny edges
    edged = cv2.Canny(image, 30, 200)

    # Finding Contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Number of contours: {len(contours)}")

    # Draw all contours
    image = np.ones(image.shape[:2], dtype="uint8") * 255
    cv2.drawContours(image, contours, -1, (0, 0, 0), 1)

    image = Image.fromarray(image)
    image = ImageOps.grayscale(image)

    list_of_contours = list()
    for c in contours:
        list_of_contours.append(c[:, 0, :].tolist())

    return image, list_of_contours


def visualize_gcode_as_image(gcode: str, resolution):
    gcode = gcode.split("\n")
    # prepare list of points
    x, y, pwr = 0, 0, 0
    xs = []
    ys = []
    powers = []

    for cmd in gcode:
        if cmd.startswith("M106"):
            pwr = int(cmd.split("S")[1])
        elif cmd.startswith("G1"):
            coords = cmd.split(" ")
            for coord in coords:
                if coord.startswith("X"):
                    x = int(float(coord[1:]) * resolution)
                elif coord.startswith("Y"):
                    y = int(float(coord[1:]) * resolution)
            xs.append(x)
            ys.append(y)
            powers.append(pwr)

    image = Image.new('L', (max(xs), max(ys)), 200)
    draw = ImageDraw.Draw(image)

    for i in range(1, len(xs)):
        if powers[i] <= 250:  # todo min power
            draw.line((xs[i-1], ys[i-1], xs[i], ys[i]), fill=powers[i])

    image = ImageOps.mirror(image)  # flip image to not confuse the user
    return image
