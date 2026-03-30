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
try:
    with open(template_path, "r") as file:
        ref_vector = json.load(file)
except Exception as e:
    print(f"Error loading template: {e}")
    ref_vector = []

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
        
        if right_hand:
            processed = hp.StaticPoseTemplate.process_landmarks(right_hand)
            if processed is not None:
                maxx = -2
                is_class = "Unknown"
                
                for classes in ref_vector:
                    rep_vec = np.array(classes["representative_vector"])
                    sim = hp.StaticPoseTemplate.cosine_similarity(rep_vec, processed)
                    
                    if sim > maxx:
                        maxx = sim
                        if sim > 0.8:
                            is_class = f"{classes['name']} ({sim:.2f})"
                        else:
                            is_class = f"Low Match ({sim:.2f})"

        cv2.putText(frame, is_class, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Hand Posture Classifier", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

finally:
    tracker.stop()
    cv2.destroyAllWindows()
