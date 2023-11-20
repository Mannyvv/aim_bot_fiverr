import tkinter as tk
from tkinter.colorchooser import askcolor
import pyautogui
import numpy as np
import cv2
import threading
import logging
import time
import keyboard

# Function capture a specific region of the screen
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

# Function to detect color and move the mouse to that location
def detect_color_and_move():
    global running
    while running:
        if keyboard.is_pressed('left shift'):
            screenshot = capture_region(region_size)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        
            mask_circle = np.zeros((region_size, region_size), np.uint8)
            cv2.circle(mask_circle, (region_size // 2, region_size // 2), region_size // 2, 255, -1)

            # tolerance for shades of color, adjust as needed
            tolerance = 20
            lower_bound = np.array([max(0, c-tolerance) for c in target_color], np.uint8)
            upper_bound = np.array([min(255, c+tolerance) for c in target_color], np.uint8)

            mask_color = cv2.inRange(frame, lower_bound, upper_bound)
            mask = cv2.bitwise_and(mask_color, mask_color, mask=mask_circle)

            #OpenCV Documentation
            #https://docs.opencv.org/3.4/d2/d96/tutorial_py_table_of_contents_imgproc.html
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > fov_size:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"]) + (pyautogui.size().width - region_size) // 2
                        cY = int(M["m01"] / M["m00"]) + (pyautogui.size().height - region_size) // 2
                        pyautogui.moveTo(cX, cY, duration=smooth_factor / 10)

                        ###Uncomment items below if you want logging and screenshots###
                        # moved_pixel_color = pyautogui.pixel(cX,cY)
                        # print(f"Mouse moved to ({cX}, {cY}) with pixel color: {moved_pixel_color}")

                        # logging.info(f"Moved to color at ({cX}, {cY})")
                        # timestamp = time.strftime("%Y%m%d%H%M%S")
                        # screenshot_path = f'screenshots/screenshot_{timestamp}.png'
                        # pyautogui.screenshot(screenshot_path)
                        # logging.info(f"Saved screenshot: {screenshot_path}")

                        break  # Moves to center of object inside target area

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

#logging
logging.basicConfig(filename='color_tracker_log.txt', level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

# Initialize UI variables
fov_size = 100 #determines miminum size of object to capture
smooth_factor = 1 #how smooth the mouse moves from point to point
target_color = (255, 0, 0)  #Default color (red) in RGB
region_size = 500  # Default region size at center of screen
running = False

# UI setup
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
