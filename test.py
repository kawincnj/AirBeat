import cv2
import numpy as np
import time
import os
import sys
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from plugin.hand_tracker import ThreadedHandTracker
from plugin.sound_manager import sound_manager
import plugin.helper_function as hp

template_path = os.path.join(project_root, "templates", "Close_Open_Hand.json")
template_names = []
template_matrix = []

try:
    with open(template_path, "r") as file:
        ref_data = json.load(file)
        for item in ref_data:
            template_names.append(item["name"])

            vector = np.array(item["representative_vector"]).flatten()
            template_matrix.append(vector)
    
    template_matrix = np.array(template_matrix)

    template_norms = np.linalg.norm(template_matrix, axis=1)
    print(f"Loaded {len(template_names)} templates: {template_names}")
except Exception as e:
    print(f"Error preparing templates: {e}")
    template_matrix = None


tracker = ThreadedHandTracker(min_detection_confidence=0.7, min_tracking_confidence=0.7)

SIMILARITY_THRESHOLD = 0.88

try:
    while True:
        frame, left_hand, right_hand = tracker.read()

        if frame is None:
            time.sleep(0.01)
            continue

        tracker.draw_landmarks(frame, left_hand)
        tracker.draw_landmarks(frame, right_hand)

        current_class = "No Hand"
        display_color = (200, 200, 200)

        if right_hand and template_matrix is not None:
            processed = hp.StaticPoseTemplate.process_landmarks(right_hand)
            if processed is not None:
                hand_vector = processed.flatten()
                
                dot_products = np.dot(template_matrix, hand_vector)
                hand_norm = np.linalg.norm(hand_vector)
                similarities = dot_products / (template_norms * hand_norm)
                
                best_idx = np.argmax(similarities)
                max_sim = similarities[best_idx]
                
                if max_sim > SIMILARITY_THRESHOLD:
                    current_class = template_names[best_idx]
                    display_color = (0, 255, 0)
                    
                else:
                    current_class = "Unknown"
                    display_color = (0, 0, 255)

        cv2.putText(frame, f"Posture: {current_class}", (10, 450), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, display_color, 2)

        cv2.imshow("High-Speed Hand Posture Trigger", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

finally:
    tracker.stop()
    cv2.destroyAllWindows()
