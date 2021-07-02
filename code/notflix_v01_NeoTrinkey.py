# notflix_v01_NeoTrinkey.py
# from the original 2016-05-12 Arduino version by Phillip Burgess
# 2021-06-28 converted to CircuitPython by Cedar Grove Studios

import time
import random
import board
import touchio
from adafruit_simplemath import map_range
import neopixel
from gamma8 import gamma8

NUM_PIXELS = 4  # Number of NeoPixels in array
DURATION = 2  # Play the movie for DURATION hours

pixel = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS)
pixel.fill((0, 0, 0))  # Clear NeoPixels
pixel.brightness = 1  # Set initial brightness if no control input

touch_1 = touchio.TouchIn(board.TOUCH1)
touch_2 = touchio.TouchIn(board.TOUCH2)

prev_red = new_red = 0
prev_grn = new_grn = 0
prev_blu = new_blu = 0

play_movie = True

t0 = time.monotonic()
while play_movie:
    t1 = time.monotonic()
    data_file = open("/colors.h", mode="r")
    for line in data_file:
        if play_movie and line[0:8] == "colors[]":  # Start of colors table
            print("start of colors table found")
            time.sleep(1)
        elif play_movie and ("};" in line):
            data_file.close()  # End of data_file; close and exit "for" loop
            break
        elif play_movie:
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
                        red = int(map_range(elapsed, 0, fade_time, prev_red, new_red))
                        grn = int(map_range(elapsed, 0, fade_time, prev_grn, new_grn))
                        blu = int(map_range(elapsed, 0, fade_time, prev_blu, new_blu))

                    for i in range(0, NUM_PIXELS):
                        # Quantize to 8-bit
                        red_8 = red >> 8
                        grn_8 = grn >> 8
                        blu_8 = blu >> 8
                        # Pixel count index scaled to 0 - 255
                        pixel_fraction = (i << 8) / NUM_PIXELS
                        # Boost some fraction of pixels to handle interpolation > 8-bit
                        if (red_8 < 255) and ((red & 0xFF) >= pixel_fraction):
                            red_8 += 1
                        if (grn_8 < 255) and ((grn & 0xFF) >= pixel_fraction):
                            grn_8 += 1
                        if (blu_8 < 255) and ((blu & 0xFF) >= pixel_fraction):
                            blu_8 += 1
                        pixel[i] = (red_8, grn_8, blu_8)
                        if time.monotonic() - t0 >= (
                            DURATION * 60 * 60
                        ):  # play for DURATION hours
                            play_movie = False
                    if elapsed >= fade_time:  # End scene
                        break
                time_hold_start = time.monotonic()
                while time.monotonic() - time_hold_start <= hold_time:
                    if touch_1.value:
                        pixel.brightness = pixel.brightness + 0.05
                    if touch_2.value:
                        pixel.brightness = pixel.brightness - 0.05
                    if pixel.brightness < 0.05:
                        pixel.brightness = 0.05
                    time.sleep(0.1)
                # Previous RGB = new RGB
                prev_red = new_red
                prev_grn = new_grn
                prev_blu = new_blu
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

print("End of movie")
data_file.close()  # housekeeping: close data_file
pixel.fill((0, 0, 0))  # Clear NeoPixels

while True:
    pixel[0] = (16, 0, 0)
    time.sleep(10)
    pixel[0] = (16, 0, 16)
    time.sleep(0.5)
