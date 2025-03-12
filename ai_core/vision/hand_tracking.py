from dataclasses import dataclass
import mediapipe as mp
import numpy as np


@dataclass
class Hand:
    """Dataclass containing all the points at hand marked by mediapipe"""

    # The base of the hand, the point that connects all the fingers
    WRIST: dict[str, list | tuple | dict]

    # Thumb
    THUMB_CMC: dict[str, list | tuple | dict]  # Base of the thumb
    THUMB_MCP: dict[str, list | tuple | dict]  # Metacarpophalangeal joint
    THUMB_IP: dict[str, list | tuple | dict]  # Interphalangeal joint
    THUMB_TIP: dict[str, list | tuple | dict]  # Tip of the thumb

    # Index Finger
    INDEX_FINGER_MCP: dict[str, list | tuple | dict]  # Metacarpophalangeal joint
    INDEX_FINGER_PIP: dict[str, list | tuple | dict]  # Proximal joint
    INDEX_FINGER_DIP: dict[str, list | tuple | dict]  # Distal joint
    INDEX_FINGER_TIP: dict[str, list | tuple | dict]  # Tip of the index finger

    # Middle Finger
    MIDDLE_FINGER_MCP: dict[str, list | tuple | dict]  # Metacarpophalangeal joint
    MIDDLE_FINGER_PIP: dict[str, list | tuple | dict]  # Proximal joint
    MIDDLE_FINGER_DIP: dict[str, list | tuple | dict]  # Distal joint
    MIDDLE_FINGER_TIP: dict[str, list | tuple | dict]  # Tip of the index finger

    # Ring Finger
    RING_FINGER_MCP: dict[str, list | tuple | dict]  # Metacarpophalangeal joint
    RING_FINGER_PIP: dict[str, list | tuple | dict]  # Proximal joint
    RING_FINGER_DIP: dict[str, list | tuple | dict]  # Distal joint
    RING_FINGER_TIP: dict[str, list | tuple | dict]  # Tip of the index finger

    # Pinky
    PINKY_MCP: dict[str, list | tuple | dict]  # Metacarpophalangeal joint
    PINKY_PIP: dict[str, list | tuple | dict]  # Proximal joint
    PINKY_DIP: dict[str, list | tuple | dict]  # Distal joint
    PINKY_TIP: dict[str, list | tuple | dict]  # Tip of the index finger


class Hands:
    # This function passes the mediapipe point and dimensions to the frame/image, then returns the 3D dimensional coordinates of this point based on the image.
    __to_coord = lambda self, obj, shape: [
        int(obj.x * 100 * (shape[1] / 100)),
        int(obj.y * 100 * (shape[0] / 100)),
        int(obj.z * 100),
    ]
    hands = None

    def __init__(self):
        """Interface for mediapipe, which allows working with mediapipe necessary to get the marked hand and the rib cords"""
        self.__mp_hands = mp.solutions.hands
        self.__mp_drawing = mp.solutions.drawing_utils
        self.__hands = self.__mp_hands.Hands(
            min_detection_confidence=0.7, min_tracking_confidence=0.7
        )

    def getHands(self, rgb_frame: np.ndarray):
        """It takes the frame, after which mediapipe processes it and finally returns an instance that contains all the data about the marked hand, including the coordinates

        :param rgb_frame: A numpy matrix that contains the image frame (of type RGB) taken by Opencv
        :return: An instance that contains the parameters of the hand identified in the image/frame
        """
        hands = self.__hands.process(rgb_frame)

        if hands.multi_hand_landmarks:
            self.hands = hands

            return self.hands

        self.hands = None

        return None

    def drawOnFrame(self, frame: np.ndarray, hand_landmarks):
        """Add all points to marked hands on image frame

        :param frame: A numpy array containing the image frame you want to place the landmarks on
        :param hand_landmarks: list of landmarks. Example: **hands.multi_hand_landmarks[i]**; hands is returned by getHands.
        """
        self.__mp_drawing.draw_landmarks(
            frame, hand_landmarks, self.__mp_hands.HAND_CONNECTIONS
        )

    def __getDictWithFingerPart(
        self, hand_landmarks, frame_shape: list | tuple, part: str
    ) -> dict:
        """:param hand_landmarks: list of landmarks. Example: **hands.multi_hand_landmarks[i]**; hands is returned by getHands.
        :param frame_shape: A vector with 2 values, the width and height of the frame. Example: **frame.shape[:2]**
        :param part: Name of the part of the finger/hand that is present in the Hand dataclass
        :return: Returns a dict containing the format at a point on the mediapipe and the coordinates themselves on the frame
        """
        return {
            "mediapipe": hand_landmarks.landmark[
                self.__mp_hands.HandLandmark.__dict__[part]
            ],
            "coord": self.__to_coord(
                hand_landmarks.landmark[self.__mp_hands.HandLandmark.__dict__[part]],
                frame_shape,
            ),
        }

    def getHand(self, hand_landmarks, frame_shape: list | tuple) -> Hand:
        """Creates an instance of the **Hand** dataclass.

        :param hand_landmarks: list of landmarks. Example: **hands.multi_hand_landmarks[i]**; hands is returned by getHands.
        :param frame_shape: A vector with 2 values, the width and height of the frame. Example: **frame.shape[:2]**
        :return: Returns an instance of the Hand dataclass
        """
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
