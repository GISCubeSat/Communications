import board
import busio
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from picamera2 import Picamera2 #need to install?
import time
import math


i2c = busio.I2C(board.SCL, board.SDA)
sensor1 = LSM6DSOX(i2c)
camera = Picamera2()
max = 0

while True:
    accelx, accely, accelz = sensor1.acceleration
    accel_value = math.sqrt(math.pow(accelx, 2)+ math.pow(accely, 2)+ math.pow(accelz, 2))
    print(accel_value)
    if accel_value > max:
        max = accel_value
    time.sleep(1)
