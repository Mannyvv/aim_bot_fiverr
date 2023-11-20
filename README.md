# Game Color Tracker

## Description
This Python script is designed to detect a specific color within a defined region at the center of the screen and move the mouse cursor to the centroid of the first sizable area of the detected color. It is especially useful in gaming scenarios or applications where quick color detection and cursor movement are needed.

## Features
- Detects a user-defined color within a circular region at the center of the screen.
- Moves the mouse cursor to the center of the first sizable detected color area.
- Allows users to select the color, adjust the field of view (FOV), smoothing factor, and region size through a graphical user interface (GUI).

## Requirements
- Python 3.x
- Libraries: Tkinter, PyAutoGUI, NumPy, OpenCV (cv2), threading, logging, time, keyboard
- Install required libraries using `pip install opencv-python pyautogui numpy keyboard`

## Installation and Setup
1. Ensure Python 3.x is installed on your system.
2. Install the required Python libraries:
3. Download the script file to your local machine.

## Usage
1. Run the script: python aimbot_python.py
2. Use the GUI to choose the target color and adjust the settings for FOV, smoothing, and region size.
3. Press Update Settings to confirm any changes to above settings.
4. Press the 'Start Detection' button in the GUI.
5. Activate the detection by holding the 'left shift' key.

## Notes
- Take screenshot and obtain RGB code for desired color
- Delete print statements as needed
- The script's performance might vary based on system capabilities, screen resolution, and the complexity of the screen content.
- Continuous running of the script can be resource-intensive.


