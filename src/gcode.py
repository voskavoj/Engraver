
class Pos:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.f = 0


class Gcode:
    def __init__(self, off_pwr, res_x):
        self.off_pwr = off_pwr
        self.res_x = res_x

        self.code = str()

        self.current_pos = Pos()
        self.current_pwr = 0

    def gox(self, x):
        self.current_pos.x = x
        self.code += f"G1 X{round(x/self.res_x, 3)}\n"

    def goy(self, y):
        self.current_pos.y = y
        self.code += f"G1 Y{round(y/self.res_x, 3)}\n"

    def gof(self, f):
        self.current_pos.f = f
        self.code += f"G1 F{f}\n"

    def goxy(self, x, y):
        self.current_pos.x = x
        self.current_pos.y = y
        self.code += f"G1 X{round(x/self.res_x, 3)} Y{round(y/self.res_x, 3)}\n"

    def goxyf(self, x, y, f):
        self.current_pos.x = x
        self.current_pos.y = y
        self.current_pos.f = f
        self.code += f"G1 X{round(x/self.res_x, 3)} Y{round(y/self.res_x, 3)} F{f}\n"

    def pwr(self, pwr, optimize=False):
        if optimize and pwr == self.current_pwr:
            return
        self.current_pwr = pwr
        self.code += f"M106 S{pwr}\n"

    def reset_position(self):
        self.current_pos.x = 0
        self.current_pos.y = 0
        self.code += f"G92 X0 Y0\n"

    def laser_off(self):
        self.pwr(self.off_pwr)


class ScanGcode(Gcode):
    def __init__(self, pixels, size_x, size_y, off_pwr, min_pwr, res_x, overscan_dist):
        Gcode.__init__(self, off_pwr, res_x)

        self.pixels = pixels
        self.size_x = size_x
        self.size_y = size_y
        self.min_pwr = min_pwr
        self.overscan_dist = overscan_dist

        self.laser_off()

    def go_to_overscan_distance(self, row_index):
        for x in range(self.size_x):
            if self.pixels[x, row_index] != self.min_pwr:  # found non empty pixel
                idx = max(0, x - self.overscan_dist * self.res_x)
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
    def __init__(self, cut_pwr, off_pwr, res_x):
        Gcode.__init__(self, off_pwr, res_x)
        self.cut_pwr = cut_pwr

        self.laser_off()

    def laser_on(self):
        self.pwr(self.cut_pwr)


def generate_scan_gcode(image, off_pwr, min_pwr, res_x, overscan_dist, drawing_speed, travel_speed, **kwargs):
    size_x, size_y = image.size

    gcode = ScanGcode(image.load(), size_x, size_y, off_pwr, min_pwr, res_x, overscan_dist)

    # bounding rectangle
    gcode.goxyf(0, 0, drawing_speed)
    gcode.bounding_rectangle()

    for row in range(size_y):  # y - row
        gcode.gof(travel_speed)
        # go to overscan distance, and if there is no pixel in row, continue to next row
        if gcode.go_to_overscan_distance(row_index=row) is False:
            continue

        gcode.gof(drawing_speed)
        # find next pixel of different value until EOL
        while gcode.go_to_next_different_pwr_level(row_index=row) is True:
            pass  # it happens in while

        # turn off laser
        gcode.laser_off()

    gcode.laser_off()
    return gcode.code


def generate_cut_gcode(cutting_lines, cut_pwr, off_pwr, cut_num, res_x,
                       cutting_speed, travel_speed, **kwargs):

    gcode = LineGcode(cut_pwr, off_pwr, res_x)
    gcode.laser_off()

    for _ in range(cut_num):
        for line in cutting_lines:
            # go to start of line
            x, y = line[0]
            gcode.laser_off()
            gcode.goxyf(x, y, travel_speed)
            gcode.gof(cutting_speed)  # set cutting speed

            # perform cut
            gcode.pwr(cut_pwr)
            for x, y in line:
                gcode.goxy(x, y)
            gcode.pwr(255)

    gcode.laser_off()
    gcode.laser_off()
    return gcode.code
