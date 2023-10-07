from src.gcode_tools import *


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
            if not (pix_idx and pix_val):  # row is empty
                break

            # if laser is running at or below minimal power AND the distance to the next pixel of higher power
            #   is higher than twice the overscan distance, go to overscan distance at travel speed
            if gcode.current_pos.pwr >= min_pwr and (pix_idx / res_x - gcode.current_pos.x) > (overscan_dist * 2):
                # calculate overscan pixel index (and move it by one to be sure that an infinite loop doesn't happen
                overscan_pix = calculate_overscan_pixel(pix_idx, res_x, overscan_dist) + 1
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
