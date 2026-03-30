import cv2
import numpy as np
import time
import os
import sys
import json

# --- SMART PATH FIX ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
# ----------------------

from plugin.hand_tracker import ThreadedHandTracker
from plugin.sound_manager import sound_manager
import plugin.helper_function as hp

# --- Load Templates ---
template_path = os.path.join(project_root, "templates", "up_down.json")
template_names, template_matrix = hp.StaticPoseTemplate.load_templates(template_path)

SIMILARITY_THRESHOLD = 0.60

def run_cajon():
    # Pre-load Cajon sounds
    sound_manager.load_sound("cajon_on", r"D:\CODING\AirBeat\python_logic_instruments\sounds\cajon_sound\cajon-on.wav")
    sound_manager.load_sound("cajon_off", r"D:\CODING\AirBeat\python_logic_instruments\sounds\cajon_sound\cajon-off.wav")

    tracker = ThreadedHandTracker(min_detection_confidence=0.3, min_tracking_confidence=0.7)

    # Track previous pose state per hand to detect DOWN transitions
    left_prev_up = True
    right_prev_up = True
    Y_separate = None

    try:
        while True:
            frame, left_hand, right_hand = tracker.read()
            if frame is None:
                time.sleep(0.01)
                continue

            h, w, _ = frame.shape
            if Y_separate is None:
                Y_separate = h // 2

            # --- Right Hand ---
            if right_hand:
                pose = hp.StaticPoseTemplate.classify(right_hand, template_matrix, template_names, SIMILARITY_THRESHOLD)
                is_currently_up = (pose == "up")

                if right_prev_up and not is_currently_up:
                    wrist_y = int(right_hand.landmark[1].y * h)
                    if wrist_y < Y_separate:
                        sound_manager.play("cajon_on")
                    else:
                        sound_manager.play("cajon_off")

                right_prev_up = is_currently_up
                tracker.draw_landmarks(frame, right_hand)
                status = "UP" if is_currently_up else "DOWN"
                color = (0, 255, 0) if is_currently_up else (0, 0, 255)
                cv2.putText(frame, f"R: {status}", (w - 150, 200), 1, 2, color, 2)

            # --- Left Hand ---
            if left_hand:
                pose = hp.StaticPoseTemplate.classify(left_hand, template_matrix, template_names, SIMILARITY_THRESHOLD)
                is_currently_up = (pose == "up")

                if left_prev_up and not is_currently_up:
                    wrist_y = int(left_hand.landmark[1].y * h)
                    if wrist_y < Y_separate:
                        sound_manager.play("cajon_on")
                    else:
                        sound_manager.play("cajon_off")

                left_prev_up = is_currently_up
                tracker.draw_landmarks(frame, left_hand)
                status = "UP" if is_currently_up else "DOWN"
                color = (0, 255, 0) if is_currently_up else (0, 0, 255)
                cv2.putText(frame, f"L: {status}", (50, 200), 1, 2, color, 2)

            cv2.line(frame, (0, Y_separate), (w, Y_separate), (255, 0, 0), 3)
            cv2.imshow("AirBeat - Cajon", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        tracker.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_cajon()
