import tkinter as tk
from tkinter.colorchooser import askcolor
import pyautogui
import numpy as np
import cv2
import threading
import logging
import time
import keyboard

# Function to capture a specific region of the screen
def capture_region(region_size):
    screen_width, screen_height = pyautogui.size()
    left = (screen_width - region_size) // 2
    top = (screen_height - region_size) // 2
    return pyautogui.screenshot(region=(left, top, region_size, region_size))

# Function to update settings
def update_settings(fov, smoothing, region_sz):
    global fov_size, smooth_factor, region_size
    fov_size = fov.get()
    smooth_factor = smoothing.get()
    region_size = region_sz.get()
    print(f"Settings updated: FOV={fov_size}, Smoothing={smooth_factor}, Region Size={region_size}")

# Function to choose a color
def choose_color():
    global target_color
    color_code = askcolor(title="Choose color")
    if color_code[0]:
        target_color = tuple(map(int, color_code[0]))
        target_color = target_color[::-1]  # Flip to BGR
        print(f"Color chosen: {target_color}")

# Function to detect color and move the mouse
def detect_color_and_move():
    global running
    while running:
        if keyboard.is_pressed('left shift'):
            # print("Shift pressed, looking for color:", target_color)
            screenshot = capture_region(region_size)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create a circular mask
            mask_circle = np.zeros((region_size, region_size), np.uint8)
            cv2.circle(mask_circle, (region_size // 2, region_size // 2), region_size // 2, 255, -1)

            tolerance = 20
            lower_bound = np.array([max(0, c-tolerance) for c in target_color], np.uint8)
            upper_bound = np.array([min(255, c+tolerance) for c in target_color], np.uint8)

            mask_color = cv2.inRange(frame, lower_bound, upper_bound)
            mask = cv2.bitwise_and(mask_color, mask_color, mask=mask_circle)
            matches = np.where(mask)

            if len(matches[0]) > 0 and len(matches[1]) > 0:
                scaled_x = int(matches[1][0] + (pyautogui.size().width - region_size) / 2)
                scaled_y = int(matches[0][0] + (pyautogui.size().height - region_size) / 2)

                pyautogui.moveTo(scaled_x, scaled_y, duration=smooth_factor / 10)

                # moved_pixel_color = pyautogui.pixel(scaled_x, scaled_y)
                # print(f"Mouse moved to ({scaled_x}, {scaled_y}) with pixel color: {moved_pixel_color}")

                # logging.info(f"Moved to color at ({scaled_x}, {scaled_y})")
                # timestamp = time.strftime("%Y%m%d%H%M%S")
                # screenshot_path = f'screenshots/screenshot_{timestamp}.png'
                # pyautogui.screenshot(screenshot_path)
                # logging.info(f"Saved screenshot: {screenshot_path}")

        # time.sleep(0.1)

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
region_size = 500  # Default region size, adjustable via GUI
running = False

# GUI setup
root = tk.Tk()
root.title("Game Color Tracker Settings")

fov = tk.Scale(root, from_=50, to=500, orient='horizontal', label='Field of View')
fov.pack()

smoothing = tk.Scale(root, from_=1, to=10, orient='horizontal', label='Smoothing')
smoothing.pack()

region_size_slider = tk.Scale(root, from_=100, to=1000, orient='horizontal', label='Region Size')
region_size_slider.set(region_size)  # Set default value
region_size_slider.pack()

color_button = tk.Button(root, text="Choose Color", command=choose_color)
color_button.pack()

update_button = tk.Button(root, text="Update Settings", command=lambda: update_settings(fov, smoothing, region_size_slider))
update_button.pack()

start_button = tk.Button(root, text="Start Detection", command=start_detection)
start_button.pack()

stop_button = tk.Button(root, text="Stop Detection", command=stop_detection)
stop_button.pack()

root.mainloop()
