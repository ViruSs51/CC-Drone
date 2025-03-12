from djitellopy import Tello

drone = Tello()
drone.connect()


drone.streamon()

drone.set_video_direction(Tello.CAMERA_DOWNWARD)

frame_read = drone.get_frame_read()
frame = frame_read.frame

import cv2

while True:
    cv2.imshow("Test", frame)
    if cv2.waitKey(0):
        break

drone.streamoff()
drone.end()
