
class Pos:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.f = 0
        self.pwr = 0


class Gcode:
    def __init__(self, off_pwr, res_x):
        self.off_pwr = off_pwr
        self.res_x = res_x

        self.code = str()

        self.current_pos = Pos()

    def go(self, x=None, y=None, f=None, optimize=True):
        assert x or y or f
        out = ""

        if x:
            if optimize and self.current_pos.x == x:
                pass
            else:
                self.current_pos.x = x
                out += f" X{round(x/self.res_x, 3)}"
        if y:
            if optimize and self.current_pos.y == y:
                pass
            else:
                self.current_pos.y = y
                out += f" Y{round(y/self.res_x, 3)}"
        if f:
            if optimize and self.current_pos.f == f:
                pass  # do not write speed if it does not differ from before
            else:
                self.current_pos.f = f
                out += f" F{f}"

        if out:
            self.code += "G1" + out + "\n"

    def pwr(self, pwr, optimize=False):
        if optimize and pwr == self.current_pos.pwr:
            return
        self.current_pos.pwr = pwr
        self.code += f"M106 S{pwr}\n"

    def reset_position(self):
        self.current_pos.x = 0
        self.current_pos.y = 0
        self.code += f"G92 X0 Y0\n"

    def laser_off(self):
        self.pwr(self.off_pwr, optimize=False)


class ScanGcode(Gcode):
    def __init__(self, pixels, size_x, size_y, off_pwr, min_pwr, res_x, overscan_dist):
        Gcode.__init__(self, off_pwr, res_x)

        self.pixels = pixels
        self.size_x = size_x
        self.size_y = size_y
        self.min_pwr = min_pwr
        self.overscan_dist = overscan_dist

        self.laser_off()

    def go_to_overscan_distance(self, start_index, row_index):
        for x in range(start_index, self.size_x):
            if self.pixels[x, row_index] != self.min_pwr:  # found non empty pixel
                idx = max(0, x - self.overscan_dist * self.res_x)
                self.go(idx, row_index)
                self.laser_off()
                return True
        return False

    def find_next_different_pwr_level(self, row_index):
        for x in range(self.current_pos.x + 1, self.size_x):
            if (pixval := self.pixels[x, row_index]) != self.current_pos.pwr:  # found non empty pixel
                # self.go(x)
                # self.pwr(pixval)
                if pixval != self.off_pwr:
                    return x, pixval

        return False, False


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

    for row in range(size_y):  # y - row
        gcode.go(f=travel_speed)
        # go to overscan distance, and if there is no pixel in row, continue to next row
        if gcode.go_to_overscan_distance(row_index=row, start_index=0) is False:
            continue

        # find next pixel of different value until end of row
        while True:
            pix_idx, pix_val = gcode.find_next_different_pwr_level(row_index=row)
            if not (pix_idx and pix_val):
                break

            # if laser is running at or below minimal power AND the distance to the next pixel of higher power
            #   is higher than twice the overscan distance, go to overscan distance at travel speed
            if gcode.current_pos.pwr >= min_pwr and (pix_idx / res_x - gcode.current_pos.x) > (overscan_dist * 2):
                # calculate overscan pixel index (and move it by one to be sure that an infinite loop doesn't happen
                overscan_pix = int(((pix_idx / res_x) - overscan_dist) * res_x) + 1
                print(pix_idx, overscan_pix)
                gcode.go(x=overscan_pix, y=row, f=drawing_speed)
                gcode.pwr(min_pwr+1)
            else:
                gcode.go(x=pix_idx, y=row, f=drawing_speed)
                gcode.pwr(pix_val)

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
            gcode.go(x, y, travel_speed)

            # perform cut
            gcode.pwr(cut_pwr)
            for x, y in line:
                gcode.go(x, y, cutting_speed)
            gcode.pwr(255)

    gcode.laser_off()
    gcode.laser_off()
    return gcode.code
