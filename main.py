import cv2
import numpy as np
from utils import file_manager
from src.controllers import Controller
from src.controllers import CameraController


config_path = "data/config.json"


def get_frame(capture: cv2.VideoCapture) -> np.ndarray:
    """This function is specifically customized for capturing the camera frame"""
    ret, frame = capture.read()

    if not ret:
        return None

    return frame


def main():
    config = file_manager.open_json(config_path)
    controller = Controller() if config["connect_drone"] else None

    # If the controller is not exist, the image from the simple camera will be captured, and the controller with the camera will be started without sending any commands to the drone.
    if controller is not None and config["camera"] == "drone":
        controller.run_camera()
        camera_controller = CameraController(
            get_frame_function=controller.get_capture,
            drone_controller=controller,
            show_information=True,
            show_minimap=True,
            show_landmarks=True,
        )

    elif config["camera"] != "drone" and type(config["camera"]) is int:
        capture = cv2.VideoCapture(config["camera"])
        camera_controller = CameraController(
            get_frame_function=get_frame,
            drone_controller=controller,
            show_information=True,
            show_minimap=True,
            show_landmarks=True,
            capture=capture,
        )

    camera_controller.running()


if __name__ == "__main__":
    main()
