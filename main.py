import cv2
import DroneController as dc
from CameraControllerTello import CameraController
from utils import FileManager


config_path = "data/config.json"


def get_frame(capture: cv2.VideoCapture):
    """This function is specifically customized for capturing the camera frame"""
    ret, frame = capture.read()

    if not ret:
        return None

    return frame


def main():
    config = FileManager.open_json(config_path)
    controller = dc.Controller()

    if config["camera"] == "drone":
        controller.run_camera()
        camera_controller = CameraController(
            drone_controller=controller, get_frame_function=controller.get_capture
        )

    else:
        capture = cv2.VideoCapture(config["camera"])
        camera_controller = CameraController(
            drone_controller=controller, get_frame_function=get_frame, capture=capture
        )

    camera_controller.running()


if __name__ == "__main__":
    main()
