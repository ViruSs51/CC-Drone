import cv2
import mediapipe as mp
import numpy as np
from typing import Callable
from dataclasses import dataclass
from utils import file_manager
from src.controllers import Controller


config_path = "data/config.json"


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


class CameraController:
    __path = (
        []
    )  # This list contains the commands that will be executed by the drone one by one.
    _run = False
    __start = False
    __started = False
    __command = None

    def __init__(
        self,
        get_frame_function: Callable[[], np.ndarray],
        drone_controller: Controller | None = None,
        show_information: bool = True,
        show_landmarks: bool = True,
        *args,
        **kwargs,
    ):
        """Interface for controlling the drone using hand gestures.

        ## Instructions
        The drone recognizes specific hand gestures, which are translated into commands.
        - **Only the right hand** can be used to perform these gestures.
        - **"Wait"**, **"Start"** and **"Stop"** commands execute instantly.
        - **"Move"** and **"Rotate"** commands are queued and executed sequentially once the **"Start"** command is given again while the drone is flying.

        #### 1. **"Wait" Command ✋**
        - **Gesture**: Vertical palm in front of the camera, with the thumb pressed against the palm.
        - **Action**: The drone will remain still (no movement).

        #### 2. **"Start" Command 👊**
        - **Gesture**: A closed fist.
        - **Action**: The drone will start its operation.
          - If the drone is already flying and you show this command again, it will start executing the queued **"Move"** and **"Rotate"** commands in sequence.

        #### 3. **"Move" Command 👉**
        - **Gesture**: Pointing with the index finger.
          - Move the finger to the **right** to move the drone forward. You will need to indicate the distance in centimeters for how far the drone should move.
          - Move the finger to the **left** to move the drone backward. Again, specify the distance in centimeters for the backward movement.
        - **Action**: The movement command is added to the queue.

        #### 4. **"Rotate" Command 👉✋**
        - **Gesture**: Pointing with both the index finger and middle finger.
          - Move the fingers to the **right** to rotate the drone to the left.
          - Move the fingers to the **left** to rotate the drone to the right.
          - The rotation angle is indicated by the distance the fingers move in either direction.
        - **Action**: The rotation command is added to the queue.

        ### 5. **"Stop" (Landing) Command ✋👇**
        - **Gesture**: Open palm with the thumb pointing downward.
        - **Action**: The drone will stop and land.

        :param get_frame_function: Custom function that should return the frame with the image taken from the video camera.
        :param drone_controller: Instance of the **Controller** class.
        :param ...: Any other parameter will be as a parameter for **get_frame_function**
        """
        self.__get_frame_function = get_frame_function
        self.__func_params = [args, kwargs]
        self.__drone_controller = drone_controller
        self.show_information, self.show_landmarks = show_information, show_landmarks

        self.__hands = Hands()
        self.config = file_manager.open_json(filename=config_path)

    def updateFrame(self, frame: np.ndarray):
        """Updates the global frame of the instance

        :param frame: A numpy array containing the image frame you want to place the landmarks on
        """
        self.__frame = frame
        self.shape = self.__frame.shape[:2] if self.__frame is not None else None

    def showFrame(self):
        """Create a window with the video stream from the global frame of the instance via OpenCV.

        **To close the window, respectively this interface, it is necessary to press the _Q_ button**
        """
        cv2.imshow("Video Capture", self.__frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.__run = False

            return self.__run

        return True

    def __runPath(self):
        """Iterates through each element in **self.__path** and then executes the indicated command, finally emptying the list"""
        for action in self.__path:
            if action[0] == "move":
                if action[1] > 0:  # Move forward
                    self.__drone_controller.move("forward", action[1])

                else:  # Move back
                    self.__drone_controller.move("back", abs(action[1]))

            elif action[0] == "rotate":
                if action[1] > 0:  # Rotate left
                    self.__drone_controller.rotate("left", action[1])

                else:  # Rotate right
                    self.__drone_controller.rotate("right", abs(action[1]))

        self.__path = []

    def command_to_drone(self, command: str) -> bool:
        """Execute special interface commands to control the drone

        :param command: The command you want to execute. Available commands: start, stop, fly?, run-path
        """
        if not self.__drone_controller:
            return None

        if command == "start":
            self.__drone_controller.run()

        elif command == "stop":
            self.__drone_controller.stop()

        elif command == "fly?":
            height = self.__drone_controller.get_height()

            if height > 0:
                return True
            else:
                return False

        elif command == "run-path":
            self.__runPath()

        return True

    def running(self):
        """It starts a cycle through which it processes the video stream captured by the camera and performs certain checks for the classification of hand gestures and the control of the drone."""
        self.__run, retry = True, 0

        while self.__run:
            # Retrieve the frame through the custom function and use it as a global parameter of the instance
            self.updateFrame(
                self.__get_frame_function(
                    *self.__func_params[0], **self.__func_params[1]
                )
            )

            if self.__frame is None:
                retry += 1

                continue

            elif retry >= 300:
                break

            retry = 0

            # OpenCV captures the image from the drone in RGB format, which is why it needs to be converted to BGR to ensure the image is displayed correctly.
            if self.config["camera"] == "drone":
                self.__frame = cv2.cvtColor(self.__frame, cv2.COLOR_RGB2BGR)

            self.__frame = cv2.flip(self.__frame, 1)
            rgb_frame = cv2.cvtColor(self.__frame, cv2.COLOR_BGR2RGB)

            hands = self.__hands.getHands(rgb_frame=rgb_frame)
            if hands is not None:
                # Processing is performed for each hand identified by MediaPipe.
                for i, hand_handedness in enumerate(hands.multi_handedness):
                    hand_landmarks = hands.multi_hand_landmarks[i]
                    label = hand_handedness.classification[0].label

                    if (
                        label == "Right"
                    ):  # Processing is performed only with the right hand.
                        if self.show_landmarks:
                            self.__hands.drawOnFrame(
                                frame=self.__frame, hand_landmarks=hand_landmarks
                            )

                        hand = self.__hands.getHand(
                            hand_landmarks=hand_landmarks, frame_shape=self.shape
                        )

                        self.__functionControl(hand=hand)

                        break  # The loop is exited to avoid any issues with drone control, ensuring that only one hand can control the drone at a time.

            if not self.showFrame():
                cv2.destroyAllWindows()
                break

    def displayInformation(self, text: str, position: list[int] | tuple[int]):
        if self.show_information:
            cv2.putText(
                self.__frame,
                text,
                position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )

    def __functionControl(self, hand: Hand):
        """It performs all the necessary checks to identify a hand gesture or any global command or action within the instance."""
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
                self.displayInformation(
                    "Start",
                    (50, 50),
                )

                self.__start = True
                self.__command = ["start"]

            elif (
                hand.THUMB_TIP["coord"][1] - 50 > hand.INDEX_FINGER_MCP["coord"][1]
                and hand.INDEX_FINGER_MCP["coord"][1]
                > hand.INDEX_FINGER_DIP["coord"][1]
                and hand.MIDDLE_FINGER_MCP["coord"][1]
                > hand.MIDDLE_FINGER_DIP["coord"][1]
                and hand.RING_FINGER_MCP["coord"][1] > hand.RING_FINGER_DIP["coord"][1]
                and hand.PINKY_MCP["coord"][1] > hand.PINKY_DIP["coord"][1]
            ):
                self.displayInformation(
                    "Stop",
                    (50, 50),
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
                self.displayInformation(
                    "Wait...",
                    (50, 50),
                )

                self.__command = ["wait"]

            elif (
                hand.INDEX_FINGER_MCP["coord"][1] > hand.INDEX_FINGER_DIP["coord"][1]
                and hand.MIDDLE_FINGER_MCP["coord"][1]
                < hand.MIDDLE_FINGER_DIP["coord"][1]
                and hand.RING_FINGER_MCP["coord"][1] < hand.RING_FINGER_DIP["coord"][1]
                and hand.PINKY_MCP["coord"][1] < hand.PINKY_DIP["coord"][1]
            ):
                self.displayInformation(
                    "Move",
                    (50, 50),
                )

                index_tip_x = hand.INDEX_FINGER_TIP["coord"][0]
                if self.__command and self.__command[0] == "move":
                    distance = index_tip_x - self.__command[1]

                    if self.__path and self.__path[-1][0] == "move":
                        self.__path[-1][1] += distance
                        self.displayInformation(
                            f"{self.__path[-1][1]}",
                            (110, 50),
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
                self.displayInformation(
                    "Rotate",
                    (50, 50),
                )

                index_tip_x = hand.INDEX_FINGER_TIP["coord"][0]
                if self.__command and self.__command[0] == "rotate":
                    rotate_degrees = index_tip_x - self.__command[1]

                    if self.__path and self.__path[-1][0] == "rotate":
                        self.__path[-1][1] += rotate_degrees
                        self.displayInformation(
                            f"{self.__path[-1][1]}",
                            (120, 50),
                        )

                    else:
                        self.__path.append(["rotate", rotate_degrees])

                self.__command = ["rotate", index_tip_x]

        if self.__start and not self.__started:
            self.command_to_drone(command="start")
            self.__started = True

        elif self.__started and self.command_to_drone(command="fly?") is False:
            self.__started = False

        elif (
            self.__command
            and self.__command[0] == "start"
            and self.__started
            and self.__path
        ):
            self.command_to_drone(command="run-path")

        elif not self.__start and self.__started:
            self.command_to_drone(command="stop")
            self.__started = False
