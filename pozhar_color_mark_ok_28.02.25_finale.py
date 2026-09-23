
import cv2
import numpy as np
import imutils
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # Laser pin
GPIO.output(17, GPIO.HIGH)

# Initialize ServoKit
pca = ServoKit(channels=16)

# Initialize servo angles
x_position = 80
y_position = 80
pca.servo[1].angle = x_position
pca.servo[2].angle = y_position

# Define frame width and height
Wd = 480
Ht = 320

# Define patrol mode variables
patrol_delay = 0.1  # in seconds (smaller values make it faster)
patrol_speed = 1    # servo movement speed factor

# Define window coordinates (you can change these values)
#in_frame_x = 100    # X coordinate for "IN Frame"
#in_frame_y = 180    # Y coordinate for "IN Frame"
#colour_mark_x = 100  # X coordinate for "Colour_mark"
#colour_mark_y = 300  # Y coordinate for "Colour_mark"

def nothing(*arg):
    pass
cv2.namedWindow("IN Frame")
cv2.moveWindow("IN Frame", 10, 100)
cv2.namedWindow("Colour_mark")
cv2.moveWindow("Colour_mark", 500, 100)

# Create two settings windows for color adjustments
cv2.namedWindow("settings_1")
cv2.moveWindow("settings_1", 1000, 100)
cv2.createTrackbar('h1_1', 'settings_1', 0, 255, nothing)
cv2.createTrackbar('h2_1', 'settings_1', 61, 255, nothing)
cv2.createTrackbar('s1_1', 'settings_1', 0, 255, nothing)
cv2.createTrackbar('s2_1', 'settings_1', 47, 255, nothing)
cv2.createTrackbar('v1_1', 'settings_1', 210, 255, nothing)
cv2.createTrackbar('v2_1', 'settings_1', 255, 255, nothing)

cv2.namedWindow("settings_2")
cv2.moveWindow("settings_2", 1330, 100)
cv2.createTrackbar('h1_2', 'settings_2', 100, 255, nothing)
cv2.createTrackbar('h2_2', 'settings_2', 255, 255, nothing)
cv2.createTrackbar('s1_2', 'settings_2', 182, 255, nothing)
cv2.createTrackbar('s2_2', 'settings_2', 255, 255, nothing)
cv2.createTrackbar('v1_2', 'settings_2', 0, 255, nothing)
cv2.createTrackbar('v2_2', 'settings_2', 255, 255, nothing)

cv2.namedWindow("settings_3")
cv2.moveWindow("settings_3", 670, 460)
cv2.createTrackbar('min_area', 'settings_3', 500, 10000, nothing)  # Set min_area range from 0 to 10000
cv2.createTrackbar('movement_step', 'settings_3', 2, 100, nothing)
cv2.createTrackbar('accuracy_modifier', 'settings_3', 100, 1000, nothing)

# Function to control servo movements
def move_servo(x, y):
    x = max(0, min(180, x))  # Clamp x to 0-180
    y = max(0, min(180, y))  # Clamp y to 0-180
    pca.servo[1].angle = x
    pca.servo[2].angle = y

# Define global variables for patrol timing
last_patrol_time = time.time()

# Patrol movement thresholds
x_max = 150
y_max = 150

# Function to set patrol speed and delay
def set_patrol_speed_and_delay(speed, delay):
    global patrol_speed, patrol_delay
    patrol_speed = speed
    patrol_delay = delay
    print("Patrol speed set to {patrol_speed}, Patrol delay set to {patrol_delay} seconds")

# Function to patrol from left to right and bottom to top
def patrol():
    global x_position, y_position, last_patrol_time
    current_time = time.time()
    time_since_last_patrol = current_time - last_patrol_time

    print(patrol_delay)
    print(time_since_last_patrol)

    # Debugging: Print patrol timing
    print("Patrol delay: {}, Time since last patrol: {}".format(patrol_delay, time_since_last_patrol))

    # Enforce the patrol delay using time.sleep()
    if time_since_last_patrol < patrol_delay:
        print("hksdg")
        time.sleep(patrol_delay - time_since_last_patrol)
        print(patrol_delay - time_since_last_patrol)

    # Calculate movement step based on patrol_speed
    step_size = int(50 * patrol_speed)  # Adjust step size based on speed factor

    # Perform patrol movement
    if x_position < x_max:
        x_position += step_size
    else:
        x_position = 0
        y_position += step_size

    if y_position >= y_max:
        y_position = 0

    move_servo(x_position, y_position)
    last_patrol_time = time.time()

# Capture video from the camera
cap = cv2.VideoCapture(0)

# Set frame width and height
cap.set(3, Wd)
cap.set(4, Ht)

no_target_frame_counter = 0
target_detected = False

x_medium = None
y_medium = None

# Initial minimum contour area
min_area = 500

# Movement step in degrees
movement_step = 2
accuracy_modifier = 100


# Add a timer variable for contour tracking
contour_timer = None
contour_start_time = None

# Main loop
while True:
    _, frame1 = cap.read()
    frame2 = cv2.flip(frame1, -1)
    frame2 = cv2.flip(frame1, 0)

    hsvLeft = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
    bwLeft = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Read trackbar positions for both settings
    h1_1 = cv2.getTrackbarPos('h1_1', 'settings_1')
    h2_1 = cv2.getTrackbarPos('h2_1', 'settings_1')
    s1_1 = cv2.getTrackbarPos('s1_1', 'settings_1')
    s2_1 = cv2.getTrackbarPos('s2_1', 'settings_1')
    v1_1 = cv2.getTrackbarPos('v1_1', 'settings_1')
    v2_1 = cv2.getTrackbarPos('v2_1', 'settings_1')

    h1_2 = cv2.getTrackbarPos('h1_2', 'settings_2')
    h2_2 = cv2.getTrackbarPos('h2_2', 'settings_2')
    s1_2 = cv2.getTrackbarPos('s1_2', 'settings_2')
    s2_2 = cv2.getTrackbarPos('s2_2', 'settings_2')
    v1_2 = cv2.getTrackbarPos('v1_2', 'settings_2')
    v2_2 = cv2.getTrackbarPos('v2_2', 'settings_2')

    min_area = cv2.getTrackbarPos('min_area', 'settings_3')
    movement_step = cv2.getTrackbarPos('movement_step', 'settings_3')
    accuracy_modifier = cv2.getTrackbarPos('accuracy_modifier', 'settings_3')


    # Create filters for both settings
    h_min_left_1 = np.array((h1_1, s1_1, v1_1), np.uint8)
    h_max_left_1 = np.array((h2_1, s2_1, v2_1), np.uint8)
    threshLeft_1 = cv2.inRange(hsvLeft, h_min_left_1, h_max_left_1)

    h_min_left_2 = np.array((h1_2, s1_2, v1_2), np.uint8)
    h_max_left_2 = np.array((h2_2, s2_2, v2_2), np.uint8)
    threshLeft_2 = cv2.inRange(hsvLeft, h_min_left_2, h_max_left_2)

    # Combine both thresholds
    combined_thresh = cv2.bitwise_or(threshLeft_1, threshLeft_2)

    cv2.imshow("Colour_mark", combined_thresh)

    # Apply mask and find contours
    contours_detect, _ = cv2.findContours(combined_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # Сортируем контуры по площади (по убыванию)
    contours = sorted(contours_detect, key=lambda x: cv2.contourArea(x), reverse=True)

    if contours:
        # Проверяем контуры один за другим, пока не найдем достаточно большой
        valid_contour_found = False
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= min_area:
                print("target found (large contour)")
                no_target_frame_counter = 0
                target_detected = True

                # Check if this is the same contour as before
                if contour_timer is not cnt:
                    contour_timer = cnt
                    contour_start_time = time.time()

                # Check if 10 seconds have passed
                if time.time() - contour_start_time >= 10:
                    # Move to the next smaller contour
                    continue

                # Рисуем boundingRect
                (x, y, w, h) = cv2.boundingRect(cnt)
                cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)

                x_medium = int(x + w / 2)
                y_medium = int(y + h / 2)

                valid_contour_found = True
                break

        if not valid_contour_found:
            no_target_frame_counter += 1
            GPIO.output(17, GPIO.HIGH)
            if no_target_frame_counter >= 100:
                print("patrol (no valid large contour)")
                target_detected = False
                patrol()
                no_target_frame_counter = 0
    else:
        no_target_frame_counter += 1
        GPIO.output(17, GPIO.HIGH)  # Turn laser off if no target is detected
        if no_target_frame_counter >= 100:
            print("patrol")
            target_detected = False
            patrol()
            no_target_frame_counter = 0

    if target_detected and x_medium is not None and y_medium is not None:
        x_center = int(frame2.shape[1] / 2)
        y_center = int(frame2.shape[0] / 2)
        
        if (x_center - accuracy_modifier <= x_medium <= x_center + accuracy_modifier and
                y_center - accuracy_modifier <= y_medium <= y_center + accuracy_modifier):
            GPIO.output(17, GPIO.LOW)  # Turn laser ON
            print("on")
        else:
            GPIO.output(17, GPIO.HIGH)  # Turn laser OFF
            print("off")

        # Move the camera to center the target
        if x_medium < x_center - movement_step:
            x_position -= movement_step  # Move left
        elif x_medium > x_center + movement_step:
            x_position += movement_step  # Move right
        if y_medium < y_center - movement_step:
            y_position -= movement_step  # Move down
        elif y_medium > y_center + movement_step:
            y_position += movement_step  # Move up

        # Clamp the positions to valid ranges
        x_position = max(0, min(180, x_position))
        y_position = max(0, min(180, y_position))
        move_servo(x_position, y_position)  # Update servo positions

    cv2.imshow("IN Frame", frame2)

    # Exit on 'Esc' key
    if cv2.waitKey(1) == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
