import cv2
import numpy as np
import os
import time
from hand_tracker import ThreadedHandTracker
import helper_function as hp

# Initialize
tracker = ThreadedHandTracker(min_detection_confidence=0.7, min_tracking_confidence=0.7)
templates_dir = "templates"

# Templates
current_template = hp.StaticPoseTemplate("Open_Hand")
capture_hand_side = "Right" # Default side
status_msg = "Press 'H' for help"
msg_expiry = 0

def set_status(msg, duration=60):
    global status_msg, msg_expiry
    status_msg = msg
    msg_expiry = duration

try:
    while True:
        frame, left_hand, right_hand = tracker.read()
        
        if frame is None:
            time.sleep(0.01)
            continue

        tracker.draw_landmarks(frame, left_hand)
        tracker.draw_landmarks(frame, right_hand)

        # Determine which hand is the current target
        target_hand = right_hand if capture_hand_side == "Right" else left_hand

        # UI Overlay
        cv2.putText(frame, f"Template: {current_template.name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Refs: {len(current_template.reference_vectors)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Target Hand: {capture_hand_side}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        if msg_expiry > 0:
            cv2.putText(frame, status_msg, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            msg_expiry -= 1
        else:
            cv2.putText(frame, "Press 'H' for help", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Similarity check if representative vector exists
        if target_hand and current_template.representative_vector is not None:
            processed = hp.StaticPoseTemplate.process_landmarks(target_hand)
            sim = current_template.find_similarity(processed)
            color = (0, 255, 0) if sim > 0.99 else (0, 0, 255)
            cv2.putText(frame, f"Similarity: {sim:.3f}", (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Hand Posture Template Tool", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('h'):
            print("\n--- Help ---")
            print("T: Toggle Target Hand (Left/Right)")
            print("A: Add current target hand pose as reference")
            print("W: Calculate representative vector (median)")
            print("S: Save template to disk")
            print("E: Clear references")
            print("N: Change template name")
            print("ESC: Exit")
            set_status("Help printed to console", 90)

        elif key == ord('t'):
            capture_hand_side = "Left" if capture_hand_side == "Right" else "Right"
            set_status(f"Target switched to {capture_hand_side} hand", 60)

        elif key == ord('a'):
            if target_hand:
                current_template.add_reference(target_hand)
                set_status(f"Added ref {len(current_template.reference_vectors)} from {capture_hand_side} hand", 30)
            else:
                set_status(f"No {capture_hand_side} hand detected!", 60)

        elif key == ord('w'):
            if current_template.reference_vectors:
                current_template.calculate_representative_vector()
                set_status("Representative vector calculated", 60)
            else:
                set_status("No references to calculate!", 60)

        elif key == ord('s'):
            if current_template.save(templates_dir):
                set_status(f"Saved to {templates_dir}/{current_template.name}.json", 90)
            else:
                set_status("Failed to save (no rep vector?)", 60)

        elif key == ord('e'):
            current_template.clear_reference_vector()
            set_status("References cleared", 60)

        elif key == ord('n'):
            new_name = input("Enter new template name: ")
            current_template.name = new_name
            set_status(f"Name set to: {new_name}", 60)

        elif key == 27:
            break

finally:
    tracker.stop()
    cv2.destroyAllWindows()
