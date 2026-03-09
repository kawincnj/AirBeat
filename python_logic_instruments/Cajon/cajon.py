import cv2
import numpy as np
import time
import os
import sys

# --- SMART PATH FIX ---
# This allows you to run the script directly from your editor or terminal
# It finds the project root (AirBeat) and adds it to Python's search path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
# ----------------------

from plugin.hand_tracker import ThreadedHandTracker
from plugin.sound_manager import sound_manager
import python_logic_instruments.Cajon.helper_functions as hf

def run_cajon():
    # Pre-load Cajon sounds
    sound_manager.load_sound("cajon_on", "python_logic_instruments/sounds/cajon-on.wav")
    sound_manager.load_sound("cajon_off", "python_logic_instruments/sounds/cajon-off.wav")

    # Initialize Tracker
    tracker = ThreadedHandTracker(min_detection_confidence=0.3, min_tracking_confidence=0.7)
    
    # Declare Variable
    left_hand_up = True
    right_hand_up = True
    threshold_upper = 0
    threshold_lower = 0
    Y_seperate = 0

    # Calibrate Variables
    is_calibrate = True
    calibrate_Zpoint_upper = []
    calibrate_Zpoint_lower = []
    start_time = time.time()
    time_set = 5

    try:
        while True:
            frame, left_hand, right_hand = tracker.read()
            if frame is None:
                time.sleep(0.01)
                continue

            h, w, c = frame.shape

            if is_calibrate:
                if left_hand and right_hand:
                    left_center = (int(left_hand.landmark[9].x * w), int(left_hand.landmark[9].y * h))
                    right_center = (int(right_hand.landmark[9].x * w), int(right_hand.landmark[9].y * h))
                    cv2.circle(frame, left_center, 50, (0, 0, 255), 4)
                    cv2.circle(frame, right_center, 50, (0, 0, 255), 4)

                sec_now = time.time() - start_time
                if sec_now <= time_set:
                    cv2.putText(frame, 'Start calibrate in:', (90, 190), 1, 3, (20, 123, 13), 5)
                    cv2.putText(frame, str(time_set - int(sec_now)), (300, 260), 1, 4, (0, 255, 0), 5)
                else:
                    cv2.putText(frame, 'Start calibrate', (50, 60), 1, 3, (20, 123, 13), 5)
                    if left_hand and right_hand:
                        calibrate_Zpoint_upper.append(min(left_hand.landmark[12].z, right_hand.landmark[12].z))
                        calibrate_Zpoint_lower.append(max(left_hand.landmark[12].z, right_hand.landmark[12].z))
                        
                        if (time.time() - start_time >= (3 + time_set)):
                            threshold_upper = abs(np.median(calibrate_Zpoint_upper))
                            threshold_lower = abs(np.median(calibrate_Zpoint_lower))
                            Y_seperate = int(min(left_hand.landmark[1].y, right_hand.landmark[1].y) * h)
                            is_calibrate = False
            else:
                # Right Hand Logic
                if right_hand:
                    landmarks = right_hand.landmark
                    z_value = landmarks[12].z
                    right_hand_upper = int(landmarks[1].y * h) < Y_seperate
                    
                    is_hand_down = not hf.hand_up(right_hand_up, z_value, right_hand_upper, threshold_upper, threshold_lower)
                    if right_hand_up and is_hand_down:
                        if right_hand_upper: sound_manager.play("cajon_on")
                        else: sound_manager.play("cajon_off")
                    right_hand_up = not is_hand_down

                # Left Hand Logic
                if left_hand:
                    landmarks = left_hand.landmark
                    z_value = landmarks[12].z
                    left_hand_upper = int(landmarks[1].y * h) < Y_seperate
                    
                    is_hand_down = not hf.hand_up(left_hand_up, z_value, left_hand_upper, threshold_upper, threshold_lower)
                    if left_hand_up and is_hand_down:
                        if left_hand_upper: sound_manager.play("cajon_on")
                        else: sound_manager.play("cajon_off")
                    left_hand_up = not is_hand_down

                # Visuals
                cv2.line(frame, (0, Y_seperate), (w, Y_seperate), (255,0,0), 3, 2)
                if right_hand:
                    status = "UP" if right_hand_up else "DOWN"
                    cv2.putText(frame, status, (w-110, 200), 1, 2, (0, 255, 0) if right_hand_up else (0, 0, 255), 2)
                    tracker.draw_landmarks(frame, right_hand)
                if left_hand:
                    status = "UP" if left_hand_up else "DOWN"
                    cv2.putText(frame, status, (50, 200), 1, 2, (0, 255, 0) if left_hand_up else (0, 0, 255), 2)
                    tracker.draw_landmarks(frame, left_hand)

            cv2.imshow("AirBeat - Cajon", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        tracker.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_cajon()
