import cv2
import mediapipe as mp
import numpy as np
from typing import Callable
from dataclasses import dataclass
import DroneController as dc
from utils import FileManager


config_path = "data/config.json"


@dataclass
class Hand:
    # Baza mâinii, punctul care conectează toate degetele
    WRIST: dict[str, list | tuple | dict]

    # Degetul mare (Thumb)
    THUMB_CMC: dict[str, list | tuple | dict]  # Baza degetului mare
    THUMB_MCP: dict[str, list | tuple | dict]  # Articulația metacarpo-falangiană
    THUMB_IP: dict[str, list | tuple | dict]  # Articulația interfalangiană
    THUMB_TIP: dict[str, list | tuple | dict]  # Vârful degetului mare

    # Degetul arătător (Index Finger)
    INDEX_FINGER_MCP: dict[str, list | tuple | dict]  # Articulația metacarpo-falangiană
    INDEX_FINGER_PIP: dict[str, list | tuple | dict]  # Articulația proximală
    INDEX_FINGER_DIP: dict[str, list | tuple | dict]  # Articulația distală
    INDEX_FINGER_TIP: dict[str, list | tuple | dict]  # Vârful degetului arătător

    # Degetul mijlociu (Middle Finger)
    MIDDLE_FINGER_MCP: dict[str, list | tuple | dict]  # Articulația metacarpo-falangiană
    MIDDLE_FINGER_PIP: dict[str, list | tuple | dict]  # Articulația proximală
    MIDDLE_FINGER_DIP: dict[str, list | tuple | dict]  # Articulația distală
    MIDDLE_FINGER_TIP: dict[str, list | tuple | dict]  # Vârful degetului mijlociu

    # Degetul inelar (Ring Finger)
    RING_FINGER_MCP: dict[str, list | tuple | dict]  # Articulația metacarpo-falangiană
    RING_FINGER_PIP: dict[str, list | tuple | dict]  # Articulația proximală
    RING_FINGER_DIP: dict[str, list | tuple | dict]  # Articulația distală
    RING_FINGER_TIP: dict[str, list | tuple | dict]  # Vârful degetului inelar

    # Degetul mic (Pinky)
    PINKY_MCP: dict[str, list | tuple | dict]  # Articulația metacarpo-falangiană
    PINKY_PIP: dict[str, list | tuple | dict]  # Articulația proximală
    PINKY_DIP: dict[str, list | tuple | dict]  # Articulația distală
    PINKY_TIP: dict[str, list | tuple | dict]  # Vârful degetului mic


class Hands:
    __to_coord = lambda self, obj, shape: [
        int(obj.x * 100 * (shape[1] / 100)),
        int(obj.y * 100 * (shape[0] / 100)),
        int(obj.z * 100),
    ]
    hands = None

    def __init__(self):
        self.__mp_hands = mp.solutions.hands
        self.__mp_drawing = mp.solutions.drawing_utils
        self.__hands = self.__mp_hands.Hands(
            min_detection_confidence=0.7, min_tracking_confidence=0.7
        )

    def getHands(self, rgb_frame: np.ndarray):
        hands = self.__hands.process(rgb_frame)

        if hands.multi_hand_landmarks:
            self.hands = hands

            return self.hands

        self.hands = None

        return None

    def drawOnFrame(self, frame: np.ndarray, hand_landmarks):
        self.__mp_drawing.draw_landmarks(
            frame, hand_landmarks, self.__mp_hands.HAND_CONNECTIONS
        )

    def __getDictWithFingerPart(
        self, hand_landmarks, frame_shape: list | tuple, part: str
    ):
        return {
            "mediapipe": hand_landmarks.landmark[
                self.__mp_hands.HandLandmark.__dict__[part]
            ],
            "coord": self.__to_coord(
                hand_landmarks.landmark[self.__mp_hands.HandLandmark.__dict__[part]],
                frame_shape,
            ),
        }

    def getHand(self, hand_landmarks, frame_shape: list | tuple):
        hand_landmark_names = (
            "WRIST",
            "THUMB_CMC",
            "THUMB_MCP",
            "THUMB_IP",
            "THUMB_TIP",
            "INDEX_FINGER_MCP",
            "INDEX_FINGER_PIP",
            "INDEX_FINGER_DIP",
            "INDEX_FINGER_TIP",
            "MIDDLE_FINGER_MCP",
            "MIDDLE_FINGER_PIP",
            "MIDDLE_FINGER_DIP",
            "MIDDLE_FINGER_TIP",
            "RING_FINGER_MCP",
            "RING_FINGER_PIP",
            "RING_FINGER_DIP",
            "RING_FINGER_TIP",
            "PINKY_MCP",
            "PINKY_PIP",
            "PINKY_DIP",
            "PINKY_TIP",
        )

        hand = Hand(
            **{
                name: self.__getDictWithFingerPart(hand_landmarks, frame_shape, name)
                for name in hand_landmark_names
            }
        )

        return hand


class CameraController:
    __path = []
    _run = False
    __start = False
    __started = False
    __command = None

    def __init__(
        self,
        drone_controller: dc.Controller,
        get_frame_function: Callable[[], np.ndarray],
        *args,
        **kwargs,
    ):
        self.__get_frame_function = get_frame_function
        self.__func_params = [args, kwargs]
        self.__drone_controller = drone_controller

        self.__hands = Hands()
        self.config = FileManager.open_json(filename=config_path)

    def updateFrame(self, frame):
        self.__frame = frame
        self.shape = self.__frame.shape[:2] if self.__frame is not None else None

    def showFrame(self):
        cv2.imshow("Laptop Cam", self.__frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.__run = False

            return self.__run

        return True

    def __runPath(self):
        for action in self.__path:
            if action[0] == "move":
                if action[1] > 0:
                    print(f"Moving - {action[1]} cm to forward")
                    self.__drone_controller.move("forward", action[1])

                else:
                    print(f"Moving - {abs(action[1])} cm to back")
                    self.__drone_controller.move("back", abs(action[1]))

            elif action[0] == "rotate":
                if action[1] > 0:
                    print(f"Rotate - {action[1]} degrees to left")
                    self.__drone_controller.rotate("left", action[1])

                else:
                    print(f"Rotate - {abs(action[1])} degrees to right")
                    self.__drone_controller.rotate("right", abs(action[1]))

        self.__path = []

    def running(self):
        self.__run = True

        while self.__run:
            self.updateFrame(
                self.__get_frame_function(
                    *self.__func_params[0], **self.__func_params[1]
                )
            )

            if self.__frame is None:
                continue
            
            if self.config["camera"] == "drone":
                self.__frame = cv2.cvtColor(self.__frame, cv2.COLOR_RGB2BGR)

            self.__frame = cv2.flip(self.__frame, 1)
            rgb_frame = cv2.cvtColor(self.__frame, cv2.COLOR_BGR2RGB)

            hands = self.__hands.getHands(rgb_frame=rgb_frame)
            if hands is not None:
                self.__draw_points = []
                for i, hand_handedness in enumerate(hands.multi_handedness):
                    hand_landmarks = hands.multi_hand_landmarks[i]
                    label = hand_handedness.classification[0].label

                    if label == "Right":
                        self.__hands.drawOnFrame(
                            frame=self.__frame, hand_landmarks=hand_landmarks
                        )

                        hand = self.__hands.getHand(
                            hand_landmarks=hand_landmarks, frame_shape=self.shape
                        )

                        self.functionControl(hand=hand)

                        break

            if self.__start and not self.__started:
                print("START")
                self.__drone_controller.run()

                self.__started = True

            elif (
                self.__command
                and self.__command[0] == "start"
                and self.__started
                and self.__path
            ):
                print("RUN PATH")
                self.__runPath()

            elif not self.__start and self.__started:
                print("STOP")
                self.__drone_controller.stop()

                self.__started = False

            if not self.showFrame():
                cv2.destroyAllWindows()
                break

    def functionControl(self, hand: Hand):
        if (
            hand.WRIST["coord"][1] > hand.INDEX_FINGER_DIP["coord"][1]
            and hand.WRIST["coord"][1] > hand.MIDDLE_FINGER_DIP["coord"][1]
            and hand.WRIST["coord"][1] > hand.RING_FINGER_DIP["coord"][1]
            and hand.WRIST["coord"][1] > hand.PINKY_DIP["coord"][1]
        ):
            if (
                hand.INDEX_FINGER_MCP["coord"][1] < hand.INDEX_FINGER_DIP["coord"][1]
                and hand.MIDDLE_FINGER_MCP["coord"][1]
                < hand.MIDDLE_FINGER_DIP["coord"][1]
                and hand.RING_FINGER_MCP["coord"][1] < hand.RING_FINGER_DIP["coord"][1]
                and hand.PINKY_MCP["coord"][1] < hand.PINKY_DIP["coord"][1]
            ):
                cv2.putText(
                    self.__frame,
                    "Start",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )
                self.__start = True
                self.__command = ["start"]

            elif (
                hand.THUMB_TIP["coord"][1] > hand.INDEX_FINGER_MCP["coord"][1]
                and hand.INDEX_FINGER_MCP["coord"][1]
                > hand.INDEX_FINGER_DIP["coord"][1]
                and hand.MIDDLE_FINGER_MCP["coord"][1]
                > hand.MIDDLE_FINGER_DIP["coord"][1]
                and hand.RING_FINGER_MCP["coord"][1] > hand.RING_FINGER_DIP["coord"][1]
                and hand.PINKY_MCP["coord"][1] > hand.PINKY_DIP["coord"][1]
            ):
                cv2.putText(
                    self.__frame,
                    "Stop",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )
                self.__start = False
                self.__command = ["stop"]

            elif (
                hand.INDEX_FINGER_MCP["coord"][1] > hand.INDEX_FINGER_DIP["coord"][1]
                and hand.MIDDLE_FINGER_MCP["coord"][1]
                > hand.MIDDLE_FINGER_DIP["coord"][1]
                and hand.RING_FINGER_MCP["coord"][1] > hand.RING_FINGER_DIP["coord"][1]
                and hand.PINKY_MCP["coord"][1] > hand.PINKY_DIP["coord"][1]
            ):
                cv2.putText(
                    self.__frame,
                    "Wait...",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )
                self.__command = ["wait"]

            elif (
                hand.INDEX_FINGER_MCP["coord"][1] > hand.INDEX_FINGER_DIP["coord"][1]
                and hand.MIDDLE_FINGER_MCP["coord"][1]
                < hand.MIDDLE_FINGER_DIP["coord"][1]
                and hand.RING_FINGER_MCP["coord"][1] < hand.RING_FINGER_DIP["coord"][1]
                and hand.PINKY_MCP["coord"][1] < hand.PINKY_DIP["coord"][1]
            ):
                cv2.putText(
                    self.__frame,
                    "Move to forward or back",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

                index_tip_x = hand.INDEX_FINGER_TIP["coord"][0]
                if self.__command and self.__command[0] == "move":
                    distance = index_tip_x - self.__command[1]

                    if self.__path and self.__path[-1][0] == "move":
                        self.__path[-1][1] += distance
                        cv2.putText(
                            self.__frame,
                            f"{self.__path[-1][1]}",
                            (275, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2,
                        )

                    else:
                        self.__path.append(["move", distance])

                self.__command = ["move", index_tip_x]

            elif (
                hand.INDEX_FINGER_MCP["coord"][1] > hand.INDEX_FINGER_DIP["coord"][1]
                and hand.MIDDLE_FINGER_MCP["coord"][1]
                > hand.MIDDLE_FINGER_DIP["coord"][1]
                and hand.RING_FINGER_MCP["coord"][1] < hand.RING_FINGER_DIP["coord"][1]
                and hand.PINKY_MCP["coord"][1] < hand.PINKY_DIP["coord"][1]
            ):
                cv2.putText(
                    self.__frame,
                    "Rotate",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

                index_tip_x = hand.INDEX_FINGER_TIP["coord"][0]
                if self.__command and self.__command[0] == "rotate":
                    rotate_degrees = index_tip_x - self.__command[1]

                    if self.__path and self.__path[-1][0] == "rotate":
                        self.__path[-1][1] += rotate_degrees
                        cv2.putText(
                            self.__frame,
                            f"{self.__path[-1][1]}",
                            (120, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2,
                        )

                    else:
                        self.__path.append(["rotate", rotate_degrees])

                self.__command = ["rotate", index_tip_x]
