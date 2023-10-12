from src.gcode_tools import *


def generate_scan_gcode(image, off_pwr, min_pwr, max_pwr, res_x, overscan_dist, drawing_speed, travel_speed, **kwargs):
    size_x, size_y = image.size
    pixels = image.load()

    gcode = ScanGcode(res_x, off_pwr, min_pwr, max_pwr)
    gcode.laser_off()

    # x and y are in PIXELS
    for y in range(size_y):  # y - row

        # go to overscan distance, and if there is no pixel in row, continue to next row
        for i in range(size_x):
            if val := pixels[i, y] != 0:  # found non empty pixel
                x = calculate_overscan_pixel(i, res_x, overscan_dist)
                break
        else:
            continue

        gcode.go(x, y, travel_speed)
        gcode.pwr_map(val)

        # scan row
        skipped = 0
        while x + 1 < size_x:
            x += 1
            old_val = val

            val = pixels[x, y]

            # if laser is currently off, we skip the pixel but mark it
            if old_val == 0 and val == 0 and overscan_dist > 0:
                skipped += 1
            # if laser was off, but now isn't, and the skipped distance is twice the overscan, we go to overscan quickly
            elif old_val == 0 and val != 0 and skipped > 2 * overscan_dist * res_x:
                x = calculate_overscan_pixel(x, res_x, overscan_dist)
                gcode.go(x, f=travel_speed)
                skipped = 0
            # if the next pixel is of the same power as the previous, we skip it
            elif pixels[x, y] == old_val:
                continue
            # we go to the next pixel and set laser to its value
            else:
                val = pixels[x, y]
                gcode.go(x, f=drawing_speed)
                gcode.pwr_map(val)

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
            gcode.laser_off()

    gcode.laser_off()
    gcode.laser_off()
    return gcode.code
