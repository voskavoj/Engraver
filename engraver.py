import configparser

from gcode import generate_scan_gcode, generate_cut_gcode, Gcode
from image_processing import process_image_for_drawing, process_image_for_cut

DEFAULT_SETTINGS_FILE = "settings.ini"
DEFAULT_HEADER_FILE = "default_header.txt"
DEFAULT_FOOTER_FILE = "default_footer.txt"


class Engraver:
    def __init__(self):
        self.settings = dict()
        self.header = None
        self.footer = None
        self.gcode = str()

        self.preview_image = None

    def load_settings(self, settings_file=None):
        settings_parser = configparser.ConfigParser()
        if settings_file is None:
            settings_file = DEFAULT_SETTINGS_FILE
        settings_parser.read(settings_file)

        # reformat and convert values
        for section in settings_parser.keys():
            self.settings.update(settings_parser[section])
        for key, value in self.settings.items():
            try:  # try to convert to integer
                self.settings[key] = int(value)
            except ValueError:  # not an integer, try float
                try:
                    self.settings[key] = float(value)
                except ValueError:  # not a float either, leave it be
                    pass

    def load_header(self, header_file=None):
        if header_file is None:
            header_file = DEFAULT_HEADER_FILE
        with open(header_file, "r") as f:
            self.header = f.read()

    def load_footer(self, footer_file=None):
        if footer_file is None:
            footer_file = DEFAULT_FOOTER_FILE
        with open(footer_file, "r") as f:
            self.footer = f.read()

    def move_to_start(self):
        gcode = Gcode(self.settings["off_pwr"])
        gcode.laser_off()
        gcode.goxyf(self.settings["offset_x"],
                    self.settings["offset_y"],
                    self.settings["travel_speed"])
        gcode.reset_position()

        self.gcode += gcode.code

    def add_drawing(self, filename):
        img_drawing = process_image_for_drawing(filename,
                                                self.settings["len_x"],
                                                self.settings["res_x"],
                                                self.settings["max_pwr"],
                                                self.settings["min_pwr"])
        self.preview_image = img_drawing
        gcode_drawing = generate_scan_gcode(img_drawing, self.settings["off_pwr"])
        self.gcode += gcode_drawing

    def add_cut(self, filename, show=True):
        img_cut, lines_cut = process_image_for_cut(filename,
                                                   self.settings["len_x"],
                                                   self.settings["res_x"])
        self.preview_image = img_cut
        gcode_cut = generate_cut_gcode(lines_cut,
                                       self.settings["cut_pwr"],
                                       self.settings["off_pwr"],
                                       self.settings["cut_num"],
                                       SHOW_PWR=self.settings["min_pwr"] if show else None)
        self.gcode += gcode_cut

    def preview(self):
        if self.preview_image is not None:
            self.preview_image.show()
        else:
            print("No image to preview")

    def visualize(self):
        # todo
        print("Not implemented yet")

    def save_gcode(self, filename):
        if self.header is None:
            self.load_header()
        if self.footer is None:
            self.load_footer()

        gcode = self.header + self.gcode + self.footer
        with open("LAS_" + filename, "w") as output:
            output.write(gcode)
