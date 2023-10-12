import argparse
from src.engraver import Engraver

"""
    This file can be can be called from console. Call it with -h to show arguments.
    
    Otherwise, you can set up the code in python here.
    
        Basic usage setup:
        eng = Engraver()
        eng.load_settings()
        eng.add_drawing("image.png") and/or eng.add_cut("image.png")
        eng.save_gcode("output")

        Methods:
            - load_settings(filename*) - loads settings file, if no argument, default is used
            - load_header(filename*) - loads header file, if no argument or not called, default is used
            - load_footer(filename*) - loads footer file, if no argument or not called, default is used
            - set_image_properties(horizontal_size*, resolution*) - overrides basic image properties from settings
            - add_drawing(image filename) - creates GCODE for drawing
            - add_cut(image filename, show outline*) - creates GCODE for cutting
            - save_gcode(name) - saves GCODE
            - preview() - previews last generated image
            - visualize() - visualizes GCODE as plot
"""

# custom code here


if __name__ == "__main__":
    cmdparser = argparse.ArgumentParser()
    cmdparser.add_argument("-s", "--settings")
    cmdparser.add_argument("-c", "--cut")
    cmdparser.add_argument("-d", "--drawing")
    cmdparser.add_argument("-x", "--xsize")
    cmdparser.add_argument("-r", "--resolution")
    cmdparser.add_argument("-o", "--outline", action="store_true")
    cmdparser.add_argument("-v", "--visualize",  action="store_true")
    cmdparser.add_argument("-f", "--savename")
    args = cmdparser.parse_args()

    assert args.cut or args.drawing, "Either cut or drawing must be set"

    engraving = Engraver()
    print(f"Loading settings from {args.settings if args.settings else 'default file'}")
    engraving.load_settings(args.settings)
    print(f"Setting image size and resolution: {args.xsize}, {args.resolution} (None = value from settings")
    engraving.set_image_properties(horizontal_size=args.xsize, resolution=args.resolution)
    if args.outline and args.cut:
        print(f"Adding outline.")
        engraving.add_outline(args.cut)
    if args.drawing:
        print(f"Processing drawing from {args.drawing}")
        engraving.add_drawing(args.drawing)
    if args.cut:
        print(f"Processing cut from {args.cut}")
        engraving.add_cut(args.cut)
    print(f"Saving gcode as LAS_{args.savename if args.savename else 'engraving'}.gcode")
    engraving.save_gcode(args.savename if args.savename else "engraving")
    if args.visualize:
        print("Visualizing gcode. To finish the program, please close the image.")
        engraving.visualize()
    print("Done.")
