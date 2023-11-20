import tkinter as tk
from tkinter.colorchooser import askcolor
import pyautogui
import numpy as np
import cv2
import threading
import logging
import time
import keyboard

# Function to update settings
def update_settings(fov, smoothing, color_rgb):
    global fov_size, smooth_factor, target_color
    fov_size = fov.get()
    smooth_factor = smoothing.get()
    target_color = color_rgb  # RGB color
    print(f"Settings updated: FOV={fov_size}, Smoothing={smooth_factor}, Color={target_color}")

# Function to choose a color
def choose_color():
    global target_color
    color_code = askcolor(title="Choose color")
    if color_code[0]:
        target_color = tuple(map(int, color_code[0]))
        print(f"Color chosen: {target_color}")
        target_color = target_color[::-1]

# Function to detect color and move the mouse
# def detect_color_and_move():
#     global running
#     while running:
#         if keyboard.is_pressed('left shift'):
#             print("Shift pressed, looking for color:", target_color)
#             screen_width, screen_height = pyautogui.size()
#             screenshot = pyautogui.screenshot()
#             frame = np.array(screenshot)
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#             # Define a small tolerance for color matching
#             tolerance = 20
#             lower_bound = np.array([max(0, c-tolerance) for c in target_color], np.uint8)
#             upper_bound = np.array([min(255, c+tolerance) for c in target_color], np.uint8)

#             mask = cv2.inRange(frame, lower_bound, upper_bound)
#             matches = np.where(mask)

#             if len(matches[0]) > 0 and len(matches[1]) > 0:
#                 scaled_x = int(matches[1][0] * (screen_width / frame.shape[1]))
#                 scaled_y = int(matches[0][0] * (screen_height / frame.shape[0]))

#                 pyautogui.moveTo(scaled_x, scaled_y, duration=smooth_factor / 10)

#                 # Retrieve and print the color of the pixel where the mouse moved
#                 moved_pixel_color = pyautogui.pixel(scaled_x, scaled_y)
#                 print(f"Mouse moved to ({scaled_x}, {scaled_y}) with pixel color: {moved_pixel_color}")

#                 logging.info(f"Moved to color at ({scaled_x}, {scaled_y})")
#                 timestamp = time.strftime("%Y%m%d%H%M%S")
#                 screenshot_path = f'screenshots/screenshot_{timestamp}.png'
#                 pyautogui.screenshot(screenshot_path)
#                 logging.info(f"Saved screenshot: {screenshot_path}")

            
#         time.sleep(0.1)
def detect_color_and_move():
    global running
    while running:
        if keyboard.is_pressed('left shift'):
            print("Shift pressed, looking for color:", target_color)
            screen_width, screen_height = pyautogui.size()
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            tolerance = 20
            lower_bound = np.array([max(0, c-tolerance) for c in target_color], np.uint8)
            upper_bound = np.array([min(255, c+tolerance) for c in target_color], np.uint8)

            mask = cv2.inRange(frame, lower_bound, upper_bound)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) > fov_size:
                    x, y, w, h = cv2.boundingRect(contour)
                    pyautogui.moveTo(x + w // 2, y + h // 2, duration=smooth_factor / 10)

                    moved_pixel_color = pyautogui.pixel(x + w // 2, y + h // 2)
                    print(f"Mouse moved to ({x + w // 2}, {y + h // 2}) with pixel color: {moved_pixel_color}")

                    logging.info(f"Moved to color at ({x + w // 2}, {y + h // 2})")
                    timestamp = time.strftime("%Y%m%d%H%M%S")
                    screenshot_path = f'screenshots/screenshot_{timestamp}.png'
                    pyautogui.screenshot(screenshot_path)
                    logging.info(f"Saved screenshot: {screenshot_path}")

                    break  # Stop after moving to the first area larger than fov_size
        time.sleep(0.1)


# Start and stop functions
def start_detection():
    global running, detection_thread
    running = True
    detection_thread = threading.Thread(target=detect_color_and_move, daemon=True)
    detection_thread.start()
    print("Detection started")

def stop_detection():
    global running
    running = False
    if detection_thread.is_alive():
        detection_thread.join()
    print("Detection stopped")

# Set up logging
logging.basicConfig(filename='color_tracker_log.txt', level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

# Initialize global variables
fov_size = 100
smooth_factor = 5
target_color = (255, 0, 0)  # Default color (red) in RGB
running = False

# GUI setup
root = tk.Tk()
root.title("Game Color Tracker Settings")

fov = tk.Scale(root, from_=50, to=500, orient='horizontal', label='Field of View')
fov.pack()

smoothing = tk.Scale(root, from_=1, to=10, orient='horizontal', label='Smoothing')
smoothing.pack()

color_button = tk.Button(root, text="Choose Color", command=choose_color)
color_button.pack()

update_button = tk.Button(root, text="Update Settings", command=lambda: update_settings(fov, smoothing, target_color))
update_button.pack()

start_button = tk.Button(root, text="Start Detection", command=start_detection)
start_button.pack()

stop_button = tk.Button(root, text="Stop Detection", command=stop_detection)
stop_button.pack()

root.mainloop()
