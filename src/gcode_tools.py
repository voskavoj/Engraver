
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
    def __init__(self, pixels, size_x, size_y, off_pwr, min_pwr, max_pwr, res_x, overscan_dist):
        Gcode.__init__(self, off_pwr, res_x)

        self.pixels = pixels
        self.size_x = size_x
        self.size_y = size_y
        self.min_pwr = min_pwr
        self.max_pwr = max_pwr
        self.overscan_dist = overscan_dist

        self.laser_off()

    def pwr_map(self, pix_value):
        self.pwr(self._pixval_to_pwr(pix_value))

    def _pixval_to_pwr(self, pixval):
        return round(((pixval / 255) * (self.max_pwr - self.min_pwr)) + self.min_pwr)

    def is_laser_running(self):
        if self.current_pos.pwr == self.off_pwr:
            return False
        if self.min_pwr > self.max_pwr:  # inverted
            return not self.current_pos.pwr >= self.min_pwr
        else:
            return not self.current_pos.pwr <= self.min_pwr

    def is_next_pixel_far(self, pix):
        # if laser is running at or below minimal power AND the distance to the next pixel of higher power
        #   is higher than twice the overscan distance, go to overscan distance at travel speed
        return not self.is_laser_running() and (pix / self.res_x - self.current_pos.x) > (self.overscan_dist * 2)

    def go_to_overscan_distance(self, row_index):
        for x in range(self.size_x):
            if self.pixels[x, row_index] != 0:  # found non empty pixel
                idx = max(0, x - self.overscan_dist * self.res_x)
                self.go(idx, row_index)
                self.laser_off()
                return True
        return False

    def find_next_different_pwr_level(self, row_index):
        for x in range(self.current_pos.x + 1, self.size_x):
            if self._pixval_to_pwr(pixval := self.pixels[x, row_index]) != self.current_pos.pwr:
                if pixval != self._pixval_to_pwr(self.off_pwr):
                    return x, pixval

        return False, False


class LineGcode(Gcode):
    def __init__(self, cut_pwr, off_pwr, res_x):
        Gcode.__init__(self, off_pwr, res_x)
        self.cut_pwr = cut_pwr

        self.laser_off()

    def laser_on(self):
        self.pwr(self.cut_pwr)


def calculate_overscan_pixel(pixel, resolution, overscan_distance):
    return int(max(0, pixel - overscan_distance * resolution))
