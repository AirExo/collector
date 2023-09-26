import numpy as np

from easyrobot.encoder.angle import AngleEncoder

encoder = AngleEncoder(ids = [1, 2, 3, 4, 5, 6, 7, 8], port = '/dev/ttyUSB0', baudrate = 115200)

while True:
    e = encoder.fetch_info()
    print(e)
    