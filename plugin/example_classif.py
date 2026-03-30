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
import plugin.helper_function as hp

template_path = os.path.join(project_root, "templates", "Close_Open_Hand.json")
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
    print(f"Error preparing templates: {e}")
    template_matrix = []

tracker = ThreadedHandTracker(min_detection_confidence=0.7, min_tracking_confidence=0.7)

try:
    while True:
        frame, left_hand, right_hand = tracker.read()

        if frame is None:
            time.sleep(0.01)
            continue

        tracker.draw_landmarks(frame, left_hand)
        tracker.draw_landmarks(frame, right_hand)

        is_class = "No Hand"
        display_color = (200, 200, 200)
        
        if right_hand and len(template_matrix) > 0:
            processed = hp.StaticPoseTemplate.process_landmarks(right_hand)
            if processed is not None:
                similarities = []
                for vec in template_matrix:
                    sim = hp.StaticPoseTemplate.cosine_similarity(processed, vec)
                    similarities.append(sim)

                best_idx = np.argmax(similarities)
                max_sim = similarities[best_idx]
                    
                if max_sim > SIMILARITY_THRESHOLD:
                    is_class = f"{template_names[best_idx]} ({max_sim:.2f})"
                    display_color = (0, 255, 0)
                else:
                    is_class = f"Unknown ({max_sim:.2f})"
                    display_color = (0, 0, 255)

        cv2.putText(frame, is_class, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, display_color, 2)

        cv2.imshow("Hand Posture Classifier", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

finally:
    tracker.stop()
    cv2.destroyAllWindows()
