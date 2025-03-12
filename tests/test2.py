from djitellopy import Tello

drone = Tello()
drone.connect()

drone.takeoff()

drone.move_up(50)

for i in range(4):
    drone.curve_xyz_speed(70, 0, 70, 140, 0, 0, 50)
    drone.curve_xyz_speed(70, 0, -70, 140, 0, 0, 50)

for i in range(10):
    drone.curve_xyz_speed(70, 0, 70, 140, 0, 0, 50)
    drone.curve_xyz_speed(-70, 0, -70, -140, 0, 0, 50)

drone.land()