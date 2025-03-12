import numpy as np
import cv2
from utils import MathDrawing


class Minimap:
    __minimap = np.zeros((5000, 5000, 3), dtype=np.uint8)
    __minimap_path = []
    __minimap_path_index = 0
    __drone_rotate_degrees = 0
    __drone_position = [__minimap.shape[1] // 2, __minimap.shape[0] // 2]

    def __init__(self):
        self.__brush = MathDrawing()

    def addToPath(self, action: list[str | int]):
        self.__minimap_path.append(action)

    def clearPath(self):
        self.__minimap_path_index = 0
        self.__minimap_path = []

    def display(
        self,
        frame: np.ndarray,
        position: list[int] | tuple[int],
        size: list[int] | tuple[int],
    ):
        for i, action in enumerate(self.__minimap_path[self.__minimap_path_index :]):
            if i < self.__minimap_path_index:
                continue

            self.__minimap_path_index = i + 1

            if action[0] == "rotate":
                self.__drone_rotate_degrees += action[1]

            elif action[0] == "move":
                line = self.__brush.calculateLineByAngle(
                    self.__drone_position[0],
                    self.__drone_position[1],
                    action[1],
                    self.__drone_rotate_degrees,
                )
                self.__drone_position = line[-1]
                self.__brush.drawLine(self.__minimap, line, (0, 255, 0))

        minimap = self.__minimap.copy()
        cv2.rectangle(
            minimap,
            self.__drone_position,
            (self.__drone_position[0] + 1, self.__drone_position[1] + 1),
            (0, 0, 255),
            20,
        )
        frame_size = frame.shape

        half_frame_size = (frame_size[1] // 2, frame_size[0] // 2)
        frame = self.__brush.drawMinimapOnFrame(
            frame,
            minimap[
                self.__drone_position[1]
                - half_frame_size[1] : self.__drone_position[1]
                + half_frame_size[1],
                self.__drone_position[0]
                - half_frame_size[0] : self.__drone_position[0]
                + half_frame_size[0],
            ],
            (position[0], position[1]),
            size=size,
        )

        return frame
