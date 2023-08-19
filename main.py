from image_processing import process_image_for_drawing, process_image_for_cut
from logging import info as log
from logging import warning as warn
from logging import error as error


# settings
MAX_PWR = 100
MIN_PWR = 255
LEN_X = 30  # mm
RES_X = 10  # pix/mm

img_drawing = process_image_for_drawing("test.jpg", LEN_X, RES_X, MAX_PWR, MIN_PWR)
img_cut = process_image_for_cut("test.jpg", LEN_X, RES_X)

img_drawing.show()
img_cut.show()
