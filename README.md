# CC-Drone
This repository is about a project that enables controlling Tello drones through hand gestures. It uses Google's MediaPipe for hand tracking and OpenCV for real-time video streaming from the camera.

---
## Installation:

### 1. Install Python  
Make sure you have the latest version of Python installed. If it's not installed, download it from the official website: [Python Downloads](https://www.python.org/downloads/).  
During installation, check the **"Add Python to PATH"** option to be able to use Python from the command line.

### 2. Download the repository from GitHub  
Clone the repository using the command:  
```bash
git clone https://github.com/ViruSs51/CC-Drone.git
```  
Replace `https://github.com/ViruSs51/CC-Drone.git` with the actual repository link.

If you don't have Git installed, you can manually download the repository as a `.zip` file from GitHub and extract it into a folder.

### 3. Create a virtual environment  
Navigate to the project folder in the terminal:  
```bash
cd CC-Drone
```
Create a virtual environment using the command:  
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

### 4. Install required libraries  
Install all dependencies from `requirements.txt`:  
```bash
pip install -r requirements.txt
```
If you encounter `pip` errors, make sure you have the latest version by running:  
```bash
pip install --upgrade pip
```

### 5. Select the camera for the application  
To check and set the camera that the application will use, run the command:  
```bash
python verifyCamera.py
```
This script will display the available cameras. Select the desired camera index and save it according to the terminal instructions.

### 6. Connect to the Tello drone and run the application  
- Connect to the Tello drone's Wi-Fi (check the name in the drone's manual).  
- Once connected to the drone's Wi-Fi, run the main application:  
  ```bash
  python main.py
  ```
If everything is configured correctly, the application will start capturing video frames and interpreting gestures for drone control.

---
**Note:** If you encounter issues, ensure all libraries are installed correctly and that you have permissions to access the camera and network.
