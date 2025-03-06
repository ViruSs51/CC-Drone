from djitellopy import Tello
import keyboard
import numpy as np


class Controller:
    capture = None

    def __init__(self):
        """Interface for controlling the drone via the djitellopy module"""
        self.drone = Tello()
        self.drone.connect()

    def get_battery(self) -> int:
        """:return: The percentage of how charged the battery is currently between 0-100"""
        return self.drone.get_battery()

    def run_camera(self):
        """Starts streaming from the drone's front camera and saves the video stream from the camera to **self.capture**"""
        self.drone.streamon()
        self.capture = self.drone.get_frame_read()

    def get_capture(self) -> np.ndarray | None:
        """Too frame with image from video stream (**self.capture**)"""
        if self.capture:
            return self.capture.frame

        return None

    def get_height(self):
        """:return: Current height in cm"""
        return self.drone.get_height()

    def run(self):
        """Running drone"""
        self.drone.takeoff()

    def stop(self):
        """Landing drone"""
        self.drone.land()

    def move(self, direction: str, d: int | float):
        """
        :param direction: it can contain left, right, forward or back
        :param d: the distance it will travel
        """

        if d < 40:
            d = 40

        match direction:
            case "left":
                self.drone.move_left(d)
            case "right":
                self.drone.move_right(d)
            case "forward":
                self.drone.move_forward(d)
            case "back":
                self.drone.move_back(d)
            case "up":
                self.drone.move_up(d)
            case "down":
                self.drone.move_down(d)

    def rotate(self, direction: str, d: int | float):
        """
        :param direction: it can contain left or right
        :param d: degrees of rotation
        """

        match direction:
            case "left":
                self.drone.rotate_counter_clockwise(d)
            case "right":
                self.drone.rotate_clockwise(d)

    def __keyboard_press(self, last_pressed: str, key: str) -> str:
        press = ""

        if keyboard.is_pressed(key):
            if key != last_pressed:
                press = key

        return press

    def qwerty_control_run(self):
        """Allows control of the drone via the keyboard.

        :esc: Landing drone and exiting the method
        :shift: Move up 10 cm
        :ctrl: Move down 10 cm
        :w: Move forward 50 cm
        :a: Move left 50 cm
        :s: Move back 50 cm
        :d: Move right 50 cm
        :q: Rotate left 10 degrees
        :e: Rotate right 10 degrees
        """
        run = True
        self.run()

        while run:
            if keyboard.is_pressed("esc"):
                run = False
                self.stop()
                break

            elif keyboard.is_pressed("a"):
                self.move(direction="left", d=50)

            elif keyboard.is_pressed("d"):
                self.move(direction="right", d=50)

            elif keyboard.is_pressed("w"):
                self.move(direction="forward", d=50)

            elif keyboard.is_pressed("s"):
                self.move(direction="back", d=50)

            elif keyboard.is_pressed("q"):
                self.rotate(direction="left", d=10)

            elif keyboard.is_pressed("e"):
                self.rotate(direction="right", d=10)

            elif keyboard.is_pressed("shift"):
                self.move(direction="up", d=10)

            elif keyboard.is_pressed("ctrl"):
                self.move(direction="down", d=10)
