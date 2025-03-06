
# CC-Drone
This project allows you to control Tello drones using hand gestures. OpenCV captures the image from the camera, which is then transmitted to MediaPipe. MediaPipe processes the image and returns a marked image with points indicating the hand. MediaPipe marks the hand with points, four per finger and one for the base of the hand. Each point has its own coordinates in 3D space (xyz). The program then uses these coordinates to perform checks and determine certain commands based on the gestures shown by the user.

---

## 🎛️ Drone Control Instructions
The drone recognizes specific hand gestures, which are translated into commands.  
- **Only the right hand** can be used to perform these gestures.  
- **"Wait"**, **"Start"** and **"Stop"** commands execute instantly.  
- **"Move"** and **"Rotate"** commands are queued and executed sequentially once the **"Start"** command is given again while the drone is flying.
        
### 1. **"Wait" Command ✋**  
- **Gesture**: Vertical palm in front of the camera, with the thumb pressed against the palm.  
- **Action**: The drone will remain still (no movement).

### 2. **"Start" Command 👊**  
- **Gesture**: A closed fist.  
- **Action**: The drone will start its operation.
  - If the drone is already flying and you show this command again, it will start executing the queued **"Move"** and **"Rotate"** commands in sequence.

### 3. **"Move" Command 👉**  
- **Gesture**: Pointing with the index finger.  
  - Move the finger to the **right** to move the drone forward. You will need to indicate the distance in centimeters for how far the drone should move.  
  - Move the finger to the **left** to move the drone backward. Again, specify the distance in centimeters for the backward movement.
- **Action**: The movement command is added to the queue.

### 4. **"Rotate" Command 👉✋**  
- **Gesture**: Pointing with both the index finger and middle finger.  
  - Move the fingers to the **right** to rotate the drone to the left.  
  - Move the fingers to the **left** to rotate the drone to the right.  
  - The rotation angle is indicated by the distance the fingers move in either direction.
- **Action**: The rotation command is added to the queue.

### 5. **"Stop" (Landing) Command ✋👇**  
- **Gesture**: Open palm with the thumb pointing downward.  
- **Action**: The drone will stop and land.

## How to Control the Drone

1. Ensure the drone's camera is facing your hand gestures.
2. Use the described gestures to control the drone's movement, rotation, and landing.
3. Make sure to follow the specific hand positioning for each gesture to ensure proper recognition and response.

Feel free to experiment with these gestures to control the drone more effectively!

---

## 📂 Repository Structure

```
📦 tello-controller
 ┣ 📂 src
 ┃ ┗ 📂 controllers
 ┃   ┣ 📜 __init__.py
 ┃   ┣ 📜 camera_controller.py
 ┃   ┣ 📜 drone_dontroller.py
 ┃ 
 ┣ 📂 utils
 ┃ ┣ 📜 __init__.py
 ┃ ┗ 📜 file_manager.py
 ┣ 📂 tests
 ┣ 📜 requirements.txt
 ┣ 📜 README.md
 ┣ 📜 main.py
```

---

## 🚀 Installation

### 1. Install Python  
Ensure you have the latest version of Python installed. If not, download it from the official website: [Python Downloads](https://www.python.org/downloads/).  
> *Recommendation:* During installation, check the **"Add Python to PATH"** option to make Python accessible from the command line.

### 2. Clone the repository  
Download the project using Git:  
```bash
git clone https://github.com/ViruSs51/CC-Drone.git
```  
If you don't have Git installed, you can manually download the repository as a `.zip` file from GitHub and extract it into a folder.

### 3. Create and activate a virtual environment  
Navigate to the project folder:  
```bash
cd CC-Drone
```
Create a virtual environment:  
```bash
python -m venv venv
```
Activate the virtual environment:  
- **On Windows**:  
  ```bash
  venv\Scripts\activate
  ```
- **On macOS/Linux**:  
  ```bash
  source venv/bin/activate
  ```

### 4. Install dependencies  
Install all required libraries from `requirements.txt`:  
```bash
pip install -r requirements.txt
```

### 5. Verify and select the camera  
Run the following command to check and select the camera the application will use:  
```bash
python verify_camera.py
```
This script will display available cameras. Select the desired camera index according to the instructions in the terminal.

### 6. Connect to the Tello drone and run the application  
- Connect to the Tello drone’s Wi-Fi (check the name in the drone’s manual).  
- Once connected, run the main application:  
  ```bash
  python main.py
  ```

If everything is configured correctly, the application will begin capturing video frames and interpreting gestures for drone control.

**Note:** If you encounter issues, make sure all libraries are installed correctly and that you have the necessary permissions to access the camera and network.

---

## 🔧 Use

### Imports
```python
import cv2
import numpy as np
from src.controllers import Controller
from src.controllers import CameraController
```


### Example 1: Testing without a drone 🚀
#### 1. Creating a custom function to capture video frames
  - This method is useful for **testing functionality** without connecting to a drone.
```python
def get_frame_custom_function(capture: cv2.VideoCapture) -> np.ndarray:
    """This function is specifically customized for capturing the camera frame"""
    ret, frame = capture.read() # Reading the frame from the video camera

    # If the frame could not be retrieved, None is returned.
    return frame if ret else None
```

#### 2. Initializing the video camera
```python
capture = cv2.VideoCapture(0) # To check which camera index is available for you, you can run the verify_camera.py file.
```


#### 3. Creating the instance for **CameraControl**
```python
camera_controller = CameraController(
    get_frame_function=get_frame_custom_function, # Custom function to retrieve frame
    drone_controller=None, # Instance of the src.controllers.drone_controller.Controller class
    show_information=True, # If you want to display information about the commands executed on the screen
    show_landmarks=True, # If you want to display hand markings on the screen
    capture=capture # Parameter for the custom frame fetch function
)
```


#### 4. Starting the controller loop
```python
camera_controller.running()
```


### Example 2: Controlling the drone with hand gestures ✋🚁
#### 1. Creating an instance for the **Controller**
```python
controller = Controller()
```


#### 2. Creating the instance for CameraControl
```python
camera_controller = CameraController(
    get_frame_function=ontroller.get_capture, # Custom function to retrieve frame
    drone_controller=controller, # Instance of the src.controllers.drone_controller.Controller class
    show_information=True, # If you want to display information about the commands executed on the screen
    show_landmarks=True, # If you want to display hand markings on the screen
    capture=capture # Parameter for the custom frame fetch function
)
```

#### 3. Starting the drone control loop
```python
camera_controller.running()
```


### 💡 Additional Notes
 - If the drone does not respond to commands, check the connection and compatibility.

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
