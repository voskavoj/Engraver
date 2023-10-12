
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
    def __init__(self, res_x, off_pwr, min_pwr, max_pwr):
        Gcode.__init__(self, off_pwr, res_x)

        self.min_pwr = min_pwr
        self.max_pwr = max_pwr

        self.laser_off()

    def pwr_map(self, pixval):
        pwr = round(((pixval / 255) * (self.max_pwr - self.min_pwr)) + self.min_pwr)
        self.pwr(pwr)


class LineGcode(Gcode):
    def __init__(self, cut_pwr, off_pwr, res_x):
        Gcode.__init__(self, off_pwr, res_x)
        self.cut_pwr = cut_pwr

        self.laser_off()

    def laser_on(self):
        self.pwr(self.cut_pwr)


def calculate_overscan_pixel(pixel, resolution, overscan_distance):
    return int(max(0, pixel - overscan_distance * resolution))
