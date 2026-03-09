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
#from plugin.sound_manager import sound_manager

def run_ukulele():

    tracker = ThreadedHandTracker(min_detection_confidence=0.3, min_tracking_confidence=0.7)

    try:
        while True:
            frame, left_hand, right_hand = tracker.read()
            if frame is None:
                time.sleep(0.01)
                continue

            h, w, c = frame.shape

            tracker.draw_landmarks(frame, right_hand)
            tracker.draw_landmarks(frame, left_hand)
            
            cv2.imshow("AirBeat - Cajon", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        tracker.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_ukulele()