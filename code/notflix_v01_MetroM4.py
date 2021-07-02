# notflix_v01.py
# from the original 2016-05-12 Arduino version by Phillip Burgess
# 2021-07-01 converted to CircuitPython by Cedar Grove Studios

import time
import random
import board
from analogio import AnalogIn
from adafruit_simplemath import map_range
import neopixel
from gamma8 import gamma8

NUM_PIXELS = 40  # Number of NeoPixels in array
BRIGHTNESS_CONTROL = True  # Enable analog input for NeoPixel brightness
DURATION = 2  # Play the movie for DURATION hours

status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
status_pixel.brightness = 0.1
status_pixel[0] = (64, 0, 64)


pixel = neopixel.NeoPixel(board.D6, NUM_PIXELS)
if NUM_PIXELS > 1:
    pixel.fill((0, 0, 0))  # Clear NeoPixels
else:
    pixel[0] = (0, 0, 0)

if BRIGHTNESS_CONTROL:
    brightness = AnalogIn(board.A0)  # Brightness control input
    pixel.brightness = map_range(brightness.value, 0, 65520, 0.1, 1)
else:
    pixel.brightness = 0.1  # Set initial brightness if no control input

prev_red = new_red = 0
prev_grn = new_grn = 0
prev_blu = new_blu = 0

colors_table_start = False
colors_table_end = False

play_movie = True

t0 = time.monotonic()
while play_movie:
    t1 = time.monotonic()
    while play_movie and (not colors_table_end):
        with open("/data.h", mode="r") as data_file:
            for line in data_file:
                if line[0:8] == "colors[]":  # Start of colors table found
                    colors_table_start = True
                    line_count = 0
                # Skip gamma8 table and test for end of colors table
                if play_movie and colors_table_start and ("};" not in line):
                    fields = line.split(",")
                    for index in range(0, len(fields) - 1, 2):
                        # convert to 24-bit (8/8/8) RGB value
                        value = (int(fields[index]) << 8) + (int(fields[index + 1]))
                        red = ((value & 0xF800) | 0x0700) >> 8
                        grn = ((value & 0x07E0) | 0x0018) >> 3
                        blu = ((value & 0x001F) << 3) | 0x07
                        # Apply gamma correction, further expand to 16/16/16 RGB value
                        new_red = int(gamma8[red] * 257)
                        new_grn = int(gamma8[grn] * 257)
                        new_blu = int(gamma8[blu] * 257)

                        # total_time: Semi-random pixel-to-pixel time (msec)
                        total_time = random.randrange(250, 2500)
                        # fade_time: Pixel-to-pixel transition time (msec)
                        fade_time = random.randrange(0, total_time)
                        total_time = total_time / 1000  # convert msec to sec
                        fade_time = fade_time / 1000  # convert msec to sec
                        if random.randrange(10) < 1:
                            fade_time = 0  # Force scene cut 10% of time
                        hold_time = total_time - fade_time  # Non-transition time

                        start_time = time.monotonic()
                        while True:  # Start scene
                            elapsed = time.monotonic() - start_time
                            if elapsed >= fade_time:
                                elapsed = fade_time

                            if fade_time:
                                # 16-bit interpolation
                                red = int(
                                    map_range(elapsed, 0, fade_time, prev_red, new_red)
                                )
                                grn = int(
                                    map_range(elapsed, 0, fade_time, prev_grn, new_grn)
                                )
                                blu = int(
                                    map_range(elapsed, 0, fade_time, prev_blu, new_blu)
                                )

                            for i in range(0, NUM_PIXELS):
                                # Quantize to 8-bit
                                red_8 = red >> 8
                                grn_8 = grn >> 8
                                blu_8 = blu >> 8
                                # Pixel count index scaled to 0 - 255
                                pixel_fraction = (i << 8) / NUM_PIXELS
                                # Boost some fraction of pixels for interpolation > 8-bit
                                if (red_8 < 255) and ((red & 0xFF) >= pixel_fraction):
                                    red_8 += 1
                                if (grn_8 < 255) and ((grn & 0xFF) >= pixel_fraction):
                                    grn_8 += 1
                                if (blu_8 < 255) and ((blu & 0xFF) >= pixel_fraction):
                                    blu_8 += 1
                                if BRIGHTNESS_CONTROL:
                                    pixel.brightness = map_range(
                                        brightness.value, 0, 65520, 0.1, 1
                                    )
                                pixel[i] = (red_8, grn_8, blu_8)
                                status_pixel[0] = (red_8, grn_8, blu_8)
                                # print((red_8, grn_8, blu_8))
                                if time.monotonic() - t0 >= (
                                    DURATION * 60 * 60
                                ):  # play for DURATION hours
                                    play_movie = False
                            if elapsed >= fade_time:  # End scene
                                break
                        time.sleep(hold_time)
                        # Previous RGB = new RGB
                        prev_red = new_red
                        prev_grn = new_grn
                        prev_blu = new_blu
                else:
                    if "};" in line:
                        colors_table_end = True
                    pass
            if not play_movie:
                break
    print("End of colors table")
    print("Time:", round((time.monotonic() - t1) / 60, 1), "min")
    print(
        "Movie:",
        round((time.monotonic() - t0) / 60, 1),
        "min",
        round((time.monotonic() - t0) / 60 / 60, 1),
        "hrs",
    )
    data_file.close()
    colors_table_start = False
    colors_table_end = False

print("End of movie")
data_file.close()  # Housekeeping: close data_file
if NUM_PIXELS > 1:
    pixel.fill((0, 0, 0))  # Clear NeoPixels
else:
    pixel[0] = (0, 0, 0)

while True:
    pixel[0] = (16, 0, 0)
    status_pixel[0] = (16, 0, 0)
    time.sleep(10)
    pixel[0] = (16, 0, 16)
    status_pixel[0] = (16, 0, 16)
    time.sleep(0.5)
