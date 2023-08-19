from PIL import Image, ImageOps

from logging import info as log
from logging import warning as warn
from logging import error as error


def generate_scan_gcode(image, MAX_PWR, MIN_PWR):
    pass


def generate_line_gcode(image, CUT_PWR, OFF_PWR, CUT_NUM):
    pass


def _header():
    pass


def _footer():
    pass


def _gox(x):
    return f"G1 X{round(x, 3)}"


def _goy(y):
    return f"G1 Y{round(y, 3)}"


def _goxy(x, y):
    return f"G1 X{round(x, 3)} Y{round(y, 3)}"


def _goxyf(x, y, f):
    return f"G1 X{round(x, 3)} Y{round(y, 3)} F{f}"


def _pwr(pwr):
    return f"M106 S{pwr}"

