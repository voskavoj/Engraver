from image_processing import process_image_for_drawing, process_image_for_cut
from gcode import generate_scan_gcode, generate_cut_gcode
from logging import info as log
from logging import warning as warn
from logging import error as error


# file
IMG_FILENAME = "dragon.png"

# settings
CUT_PWR = 0
MAX_PWR = 100
MIN_PWR = 255
OFF_PWR = 255
LEN_X = 30  # mm
RES_X = 10  # pix/mm

# GCODE header, footer
GCODE_HEADER = ""
GCODE_FOOTER = ""

img_drawing = process_image_for_drawing(IMG_FILENAME, LEN_X, RES_X, MAX_PWR, MIN_PWR)
img_cut, lines_cut = process_image_for_cut(IMG_FILENAME, LEN_X, RES_X)

# img_drawing.show()
# img_cut.show()

gcode_drawing = generate_scan_gcode(img_drawing, OFF_PWR)
gcode_cut = generate_cut_gcode(lines_cut, CUT_PWR, OFF_PWR, 16, SHOW_PWR=MIN_PWR)

out_file = open("LD_" + IMG_FILENAME.rsplit(".", 1)[0] + ".gcode", "w")
out_file.write(gcode_drawing)
out_file.close()

out_file = open("LC_" + IMG_FILENAME.rsplit(".", 1)[0] + ".gcode", "w")
out_file.write(gcode_cut)
out_file.close()

