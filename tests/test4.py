from djitellopy import Tello
from math import cos, sin
from time import sleep

drone = Tello()
drone.connect()
drone.takeoff()


for x in range(-100, 100):
    drone.send_rc_control(int(sin(x) * 200), 50, int(cos(x) * 200), 0)
    sleep(0.5)


drone.land()
drone.end()
