
# CC-Drone
This project allows you to control Tello drones using hand gestures. OpenCV captures the image from the camera, which is then transmitted to MediaPipe. MediaPipe processes the image and returns a marked image with points indicating the hand. MediaPipe marks the hand with points, four per finger and one for the base of the hand. Each point has its own coordinates in 3D space (xyz). The program then uses these coordinates to perform checks and determine certain commands based on the gestures shown by the user.

---
## Installation

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
python verifyCamera.py
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
## Drone Control Instructions

### 1. **"Wait" Command ✋**  
- **Gesture**: Vertical palm in front of the camera, with the thumb pressed against the palm.  
- **Action**: The drone will remain still (no movement).

### 2. **"Start" Command 👊**  
- **Gesture**: A closed fist.  
- **Action**: The drone will start its operation.

### 3. **"Move" Command 👉**  
- **Gesture**: Pointing with the index finger.  
  - Move the finger to the **right** to move the drone forward. You will need to indicate the distance in centimeters for how far the drone should move.  
  - Move the finger to the **left** to move the drone backward. Again, specify the distance in centimeters for the backward movement.

### 4. **"Rotate" Command 👉✋**  
- **Gesture**: Pointing with both the index finger and middle finger.  
  - Move the fingers to the **right** to rotate the drone to the left.  
  - Move the fingers to the **left** to rotate the drone to the right.  
  - The rotation angle is indicated by the distance the fingers move in either direction.

### 5. **"Stop" (Landing) Command ✋👇**  
- **Gesture**: Open palm with the thumb pointing downward.  
- **Action**: The drone will stop and land.

## How to Control the Drone

1. Ensure the drone's camera is facing your hand gestures.
2. Use the described gestures to control the drone's movement, rotation, and landing.
3. Make sure to follow the specific hand positioning for each gesture to ensure proper recognition and response.

Feel free to experiment with these gestures to control the drone more effectively!

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
