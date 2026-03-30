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
template_names = []
template_matrix = []

SIMILARITY_THRESHOLD = 0.60

try:
    with open(template_path, "r") as file:
        ref_data = json.load(file)
        for item in ref_data:
            template_names.append(item["name"])
            vector = np.array(item["representative_vector"]).flatten()
            template_matrix.append(vector)
    print(f"Loaded {len(template_names)} templates: {template_names}")
except Exception as e:
    print(f"Error loading templates: {e}")
    template_matrix = []

def classify_hand(hand_landmarks):
    """
    Returns the best matching template name if similarity > threshold, else None.
    """
    if hand_landmarks is None or len(template_matrix) == 0:
        return None

    processed = hp.StaticPoseTemplate.process_landmarks(hand_landmarks)
    if processed is None:
        return None

    similarities = [
        hp.StaticPoseTemplate.cosine_similarity(processed, vec)
        for vec in template_matrix
    ]

    best_idx = np.argmax(similarities)
    max_sim = similarities[best_idx]

    if max_sim > SIMILARITY_THRESHOLD:
        return template_names[best_idx]  # e.g. "up" or "down"
    return None


def run_cajon():
    # Pre-load Cajon sounds
    sound_manager.load_sound("cajon_on", r"python_logic_instruments\sounds\cajon_sound\cajon-on.wav")
    sound_manager.load_sound("cajon_off", r"python_logic_instruments\sounds\cajon_sound\cajon-off.wav")

    tracker = ThreadedHandTracker(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # Track previous pose state per hand to detect DOWN transitions
    # True = hand was "up" last frame, False = hand was "down"
    left_prev_up = True
    right_prev_up = True

    # Y threshold to split upper/lower cajon zone (middle of frame)
    # Will be set dynamically from first valid frame
    Y_separate = None

    try:
        while True:
            frame, left_hand, right_hand = tracker.read()
            if frame is None:
                time.sleep(0.01)
                continue

            h, w, _ = frame.shape

            # Set Y_separate once using frame height midpoint
            if Y_separate is None:
                Y_separate = h // 2

            # --- Right Hand ---
            if right_hand:
                pose = classify_hand(right_hand)
                is_currently_up = (pose == "up")

                # Detect falling edge: was up, now down → trigger sound
                if right_prev_up and not is_currently_up:
                    wrist_y = int(right_hand.landmark[1].y * h)
                    if wrist_y < Y_separate:
                        sound_manager.play("cajon_on")   # Upper zone
                    else:
                        sound_manager.play("cajon_off")  # Lower zone

                right_prev_up = is_currently_up

                # Draw landmarks + status
                tracker.draw_landmarks(frame, right_hand)
                status = "UP" if is_currently_up else "DOWN"
                color = (0, 255, 0) if is_currently_up else (0, 0, 255)
                cv2.putText(frame, f"R: {status}", (w - 150, 200), 1, 2, color, 2)

            # --- Left Hand ---
            if left_hand:
                pose = classify_hand(left_hand)
                is_currently_up = (pose == "up")

                # Detect falling edge: was up, now down → trigger sound
                if left_prev_up and not is_currently_up:
                    wrist_y = int(left_hand.landmark[1].y * h)
                    if wrist_y < Y_separate:
                        sound_manager.play("cajon_on")   # Upper zone
                    else:
                        sound_manager.play("cajon_off")  # Lower zone

                left_prev_up = is_currently_up

                # Draw landmarks + status
                tracker.draw_landmarks(frame, left_hand)
                status = "UP" if is_currently_up else "DOWN"
                color = (0, 255, 0) if is_currently_up else (0, 0, 255)
                cv2.putText(frame, f"L: {status}", (50, 200), 1, 2, color, 2)

            # Draw zone divider
            cv2.line(frame, (0, Y_separate), (w, Y_separate), (255, 0, 0), 3)
            cv2.putText(frame, "UPPER (cajon_on)", (10, Y_separate - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 100), 1)
            cv2.putText(frame, "LOWER (cajon_off)", (10, Y_separate + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 1)

            cv2.imshow("AirBeat - Cajon", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        tracker.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_cajon()