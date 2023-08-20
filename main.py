from engraver import Engraver


# file
IMG_FILENAME = "dragon.png"

engraving = Engraver()
engraving.load_settings()
engraving.move_to_start()
engraving.add_drawing(IMG_FILENAME)
engraving.preview()
engraving.add_cut(IMG_FILENAME)
engraving.preview()
engraving.save_gcode(IMG_FILENAME + ".gcode")
engraving.visualize()


