from PIL import Image, ImageOps
from logging import info as log
from logging import warning as warn
from logging import error as error

OVERSCAN_DIST = 3
RES_X = 10
DRAWING_SPEED = 3000  # todo
CUTTING_SPEED = 3000


class Pos:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.f = 0


class Gcode:
    def __init__(self, off_pwr):
        self.off_pwr = off_pwr

        self.code = str()

        self.current_pos = Pos()
        self.current_pwr = 0

    def header(self):
        self.code += ""

    def footer(self):
        self.code += ""

    def gox(self, x):
        self.current_pos.x = x
        self.code += f"G1 X{round(x/RES_X, 3)}\r\n"

    def goy(self, y):
        self.current_pos.y = y
        self.code += f"G1 Y{round(y/RES_X, 3)}\r\n"

    def goxy(self, x, y):
        self.current_pos.x = x
        self.current_pos.y = y
        self.code += f"G1 X{round(x/RES_X, 3)} Y{round(y/RES_X, 3)}\r\n"

    def goxyf(self, x, y, f):
        self.current_pos.x = x
        self.current_pos.y = y
        self.current_pos.f = f
        self.code += f"G1 X{round(x/RES_X, 3)} Y{round(y/RES_X, 3)} F{f}\r\n"

    def pwr(self, pwr, optimize=False):
        if optimize and pwr == self.current_pwr:
            return
        self.current_pwr = pwr
        self.code += f"M106 S{pwr}\r\n"

    def laser_off(self):
        self.pwr(self.off_pwr)


class ScanGcode(Gcode):
    def __init__(self, pixels, size_x, size_y, off_pwr):
        Gcode.__init__(self, off_pwr)

        self.pixels = pixels
        self.size_x = size_x
        self.size_y = size_y

        self.laser_off()

    def bounding_rectangle(self):
        self.goxy(0, 0)
        self.goxy(self.size_x, 0)
        self.goxy(self.size_x, self.size_y)
        self.goxy(0, self.size_y)
        self.goxy(0, 0)

    def go_to_overscan_distance(self, row_index):
        for x in range(self.size_x):
            if self.pixels[x, row_index] != self.off_pwr:  # found non empty pixel
                idx = min(0, x - OVERSCAN_DIST * RES_X)
                self.goxy(idx, row_index)
                self.laser_off()
                return True

        return False

    def go_to_next_different_pwr_level(self, row_index):
        for x in range(self.current_pos.x + 1, self.size_x):
            if (pixval := self.pixels[x, row_index]) != self.current_pwr:  # found non empty pixel
                self.gox(x)
                self.pwr(pixval)
                return True

        return False


class LineGcode(Gcode):
    def __init__(self, cut_pwr, off_pwr):
        Gcode.__init__(self, off_pwr)
        self.cut_pwr = cut_pwr

        self.laser_off()

    def laser_on(self):
        self.pwr(self.cut_pwr)


def generate_scan_gcode(image, OFF_PWR):
    size_x, size_y = image.size

    gcode = ScanGcode(image.load(), size_x, size_y, OFF_PWR)

    # header
    gcode.header()

    # bounding rectangle
    gcode.goxyf(0, 0, DRAWING_SPEED)
    gcode.bounding_rectangle()

    for row in range(size_y):  # y - row
        # go to overscan distance, and if there is no pixel in row, continue to next row
        if gcode.go_to_overscan_distance(row_index=row) is False:
            continue

        # find next pixel of different value until EOL
        while gcode.go_to_next_different_pwr_level(row_index=row) is True:
            pass  # it happens in while

        # turn off laser
        gcode.laser_off()

    # footer
    gcode.footer()

    return gcode.code


def generate_cut_gcode(cutting_line, CUT_PWR, OFF_PWR, CUT_NUM, SHOW_PWR=None):
    gcode = LineGcode(CUT_PWR, OFF_PWR)

    gcode.header()
    gcode.goxyf(0, 0, CUTTING_SPEED)

    # prepare list of cutting powers
    cut_list = [CUT_PWR] * CUT_NUM
    if SHOW_PWR is not None:
        cut_list.insert(0, SHOW_PWR)

    # for each cutting power (cycle), draw a line
    for pwr in cut_list:
        for x, y in cutting_line:
            gcode.goxy(x, y)
            gcode.pwr(pwr)
        gcode.laser_off()

    gcode.laser_off()
    gcode.footer()

    print(gcode.code)
    return gcode.code

