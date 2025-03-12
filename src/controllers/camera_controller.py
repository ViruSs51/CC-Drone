import cv2
import numpy as np
import asyncio
from typing import Callable
from utils import file_manager
from ai_core.vision import Hand, Hands
from src.controllers import Controller, Minimap


config_path = "data/config.json"


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
        show_minimap: bool = True,
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

        #### 5. **"Stop" (Landing) Command ✋👇**
        - **Gesture**: Open palm with the thumb pointing downward.
        - **Action**: The drone will stop and land.

        :param get_frame_function: Custom function that should return the frame with the image taken from the video camera.
        :param drone_controller: Instance of the **Controller** class.
        :param ...: Any other parameter will be as a parameter for **get_frame_function**
        """
        self.__get_frame_function = get_frame_function
        self.__func_params = [args, kwargs]
        self.__drone_controller = drone_controller
        self.show_information, self.show_minimap, self.show_landmarks = (
            show_information,
            show_minimap,
            show_landmarks,
        )

        self.__hands = Hands()
        self.config = file_manager.open_json(filename=config_path)

        if self.show_minimap:
            self.minimap = Minimap()

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

    def __runPath(self):
        """Iterates through each element in **self.__path** and then executes the indicated command, finally emptying the list"""
        if self.commandToDrone(command="fly?") is True:
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

        self.minimap.clearPath()
        self.__path = []

    def commandToDrone(self, command: str = "") -> bool:
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

            if self.show_minimap:
                self.__frame = self.minimap.display(
                    frame=self.__frame,
                    position=(self.__frame.shape[1] - 50 * 2 - 20, 20),
                    size=50,
                )

            if not self.showFrame():
                cv2.destroyAllWindows()
                break

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

                    self.minimap.addToPath(action=["move", distance])

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

                    self.minimap.addToPath(action=["rotate", rotate_degrees])

                self.__command = ["rotate", index_tip_x]

        if self.__start and not self.__started:
            self.commandToDrone(command="start")
            self.__started = True

        elif self.__started and self.commandToDrone(command="fly?") is False:
            self.__started = False

        elif (
            self.__command
            and self.__command[0] == "start"
            and self.__started
            and self.__path
        ):
            self.__runPath()

        elif not self.__start and self.__started:
            self.commandToDrone(command="stop")
            self.__started = False
