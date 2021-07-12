# notflix_display.py

notflix[47] = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    31,
    2,
    4,
    31,
    0,
    14,
    17,
    14,
    0,
    1,
    31,
    1,
    0,
    31,
    5,
    1,
    0,
    31,
    16,
    16,
    0,
    17,
    31,
    17,
    0,
    17,
    10,
    4,
    10,
    17,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]

# Display NOTFLIX graphic on startup screen
def disp_notflix():
    for i in range(0, NUM_PIXELS):  # wipe screen to dark
        pixel[i] = (0, 0, 0)
        time.sleep(0.050)
    for i in range(1, 47 - 8):
        for j in range(0, 8):

            # display rolling graphic
            if notflix[i + j] & 1:
                pixel[j] = (0, 8, 0)
            else:
                pixel[j] = (0, 0, 0)

            if notflix[i + j] & 2:
                pixel[j + 8] = (0, 8, 0)
            else:
                pixel[j + 8] = (0, 0, 0)

            if notflix[i + j] & 4:
                pixel[j + 16] = (0, 8, 0)
            else:
                pixel[j + 16] = (0, 0, 0)

            if notflix[i + j] & 8:
                pixel[j + 24] = (0, 8, 0)
            else:
                pixel[j + 24] = (0, 0, 0)

            if notflix[i + j] & 16:
                pixel[j + 32] = (0, 8, 0)
            else:
                pixel[j + 32] = (0, 0, 0)

        time.sleep(0.300)
