import cv2
import numpy as np
import sys
import os
import json
import copy
import time
from collections import Counter, deque

# --- 1. CONFIGURATION ---
ZONE_COLORS = [(100, 30, 30), (30, 100, 30), (30, 100, 100), (30, 50, 100), (30, 30, 100), (50, 30, 50)]

# --- SMART PATH FIX ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
# ----------------------

from plugin.hand_tracker import ThreadedHandTracker

class StaticPoseTemplate:
    def __init__(self, name, vector=None, fret=1, string=1, anchor_idx=8):
        self.name = name
        self.representative_vector = vector
        self.fret = fret
        self.string = string
        self.anchor_idx = anchor_idx

    @staticmethod
    def process_landmarks(hand_landmarks):
        all_pts = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
        palm_width = np.linalg.norm(all_pts[5] - all_pts[17])
        if palm_width == 0: palm_width = 1.0
        indices = list(range(5, 21))
        filtered_pts = all_pts[indices]
        ref_pt = filtered_pts[0]
        relative_vectors = (filtered_pts - ref_pt) / palm_width
        weights = np.ones((16, 3))
        weights[5:8] = 2.5 
        final_vec = (relative_vectors * weights).flatten()
        norm = np.linalg.norm(final_vec)
        return final_vec / norm if norm > 0 else final_vec

    def find_similarity(self, current_vec, current_fret, current_string, current_anchor):
        if self.representative_vector is None: return 0
        if self.fret != current_fret or self.string != current_string or self.anchor_idx != current_anchor:
            return 0
        return np.dot(current_vec, self.representative_vector)

def draw_static_fretboard_ui(frame, box):
    bx, by, bw, bh = box
    # Fret lines
    cv2.line(frame, (bx, by), (bx, by + bh), (255, 255, 255), 4) 
    fret_w = bw // 4
    for i in range(1, 5):
        cv2.line(frame, (bx + i*fret_w, by), (bx + i*fret_w, by + bh), (120, 120, 120), 2)
    # String names
    string_names = ['E', 'A', 'D', 'G', 'B', 'e'] 
    zone_h = bh / 6.0
    for i in range(6):
        y = int(by + (i * zone_h) + (zone_h / 2))
        cv2.line(frame, (bx, y), (bx + bw, y), (200,200,200), 2 if i > 2 else 3)
        cv2.putText(frame, string_names[i], (bx - 25, y + 5), 0, 0.4, (80, 80, 80), 1)

# --- NEW: STRUM UI FUNCTION ---
def draw_strum_zone(frame, y_line, is_active):
    color = (0, 255, 255) if is_active else (100, 100, 100)
    thickness = 3 if is_active else 1
    # Draw a horizontal line across the right side of the screen
    cv2.line(frame, (400, y_line), (frame.shape[1] - 50, y_line), color, thickness)
    cv2.putText(frame, "STRUM LINE", (400, y_line - 10), 0, 0.5, color, 1)

def main():
    tracker = ThreadedHandTracker(min_detection_confidence=0.7)
    neck_box = (50, 220, 240, 130) 
    strum_line_y = 300 # Vertical position of the strum trigger
    
    
    # Logic State
    library_templates = []
    # def reload_lib():
    #     nonlocal library_templates
    #     library_templates = []
    #     if not os.path.exists("templates"): os.makedirs("templates")
    #     for f in os.listdir("templates"):
    #         if f.endswith(".json"):
    #             with open(os.path.join("templates", f), 'r') as file:
    #                 d = json.load(file)
    #                 library_templates.append(StaticPoseTemplate(
    #                     d['name'], np.array(d['rep_vector']), 
    #                     d.get('fret', 1), d.get('string', 1), d.get('anchor_idx', 8)
    #                 ))
    
    # reload_lib()
    stabilizer = deque(maxlen=10)
    recording_data = []
    is_recording = False
    
    # Strumming State
    was_above_line = True
    strum_visual_timer = 0 # To make the strum effect last a few frames

    # Smoothing
    smooth_fx, smooth_fy = -1, -1

    try:
        while True:
            frame, left, right = tracker.read()
            if frame is None: continue
            h_f, w_f, _ = frame.shape
            
            draw_static_fretboard_ui(frame, neck_box)
            bx, by, bw, bh = neck_box
            
            # --- STRUM DETECTION (Right Hand) ---
            strum_triggered = False
            if right:
                # Use index finger tip (landmark 8) for strumming accuracy
                right_y = int(right.landmark[8].y * h_f)
                is_currently_above = right_y < strum_line_y
                
                if is_currently_above != was_above_line:
                    strum_triggered = True
                    strum_visual_timer = 12 
                
                was_above_line = is_currently_above
                # Draw right hand pointer
                cv2.circle(frame, (int(right.landmark[8].x * w_f), right_y), 5, (0, 255, 255), -1)

            draw_strum_zone(frame, strum_line_y, strum_visual_timer > 0)
            if strum_visual_timer > 0: strum_visual_timer -= 1

            # --- CHORD DETECTION (Left Hand) ---
            display_name = "No Hand"
            cur_fret, cur_string, cur_anchor = 0, 0, -1
            target_fx, target_fy = -1, -1

            if left:
                finger_pts = [(left.landmark[i], i) for i in range(5, 21)]
                lead_lm, lead_idx = min(finger_pts, key=lambda x: x[0].y)
                cur_anchor = lead_idx
                ix, iy = int(lead_lm.x * w_f), int(lead_lm.y * h_f)

                if bx < ix < bx + bw and by < iy < by + bh:
                    cur_fret = int((ix - bx) // (bw // 4)) + 1
                    zone_idx = int((iy - by) / (bh / 6.0))
                    cur_string = max(1, min(6, 6 - zone_idx))
                    processed = StaticPoseTemplate.process_landmarks(left)
                    
                    if is_recording:
                        recording_data.append((processed, cur_fret, cur_string, cur_anchor))
                    else:
                        best_sim, best_name = 0, "Unknown"
                        for t in library_templates:
                            sim = t.find_similarity(processed, cur_fret, cur_string, cur_anchor)
                            if sim > best_sim:
                                best_sim, best_name = sim, t.name
                        stabilizer.append(best_name if best_sim > 0.94 else "Unknown")
                        display_name = Counter(stabilizer).most_common(1)[0][0]
                    target_fx, target_fy = bx + (cur_fret-1)*(bw//4), int(by + zone_idx*(bh/6.0))
                else:
                    display_name = "Align Hand"

            # --- FINAL RENDERING ---
            if target_fx != -1:
                if smooth_fx == -1: smooth_fx, smooth_fy = target_fx, target_fy
                smooth_fx += (target_fx - smooth_fx) * 0.2
                smooth_fy += (target_fy - smooth_fy) * 0.2
                overlay = frame.copy()
                cv2.rectangle(overlay, (int(smooth_fx), int(smooth_fy)), 
                              (int(smooth_fx + bw//4), int(smooth_fy + bh/6.0)), (0, 255, 0), -1)
                cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

            # Strum Flash Effect
            if strum_visual_timer > 0:
                cv2.putText(frame, "STRUM", (450, 100), 2, 2.0, (0, 255, 255), 3)

            cv2.putText(frame, f"CHORD: {display_name}", (20, 50), 2, 1.0, (255, 255, 255), 2)
            cv2.imshow("Guitar AI - Dual Hand", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                if not is_recording: is_recording, recording_data = True, []
                else:
                    is_recording = False
                    if len(recording_data) > 10:
                        name = input("Chord Name: ")
                        vecs, frets, strs, anks = zip(*recording_data)
                        final_data = {"name": name, "rep_vector": np.median(vecs, axis=0).tolist(),
                                      "fret": int(Counter(frets).most_common(1)[0][0]),
                                      "string": int(Counter(strs).most_common(1)[0][0]),
                                      "anchor_idx": int(Counter(anks).most_common(1)[0][0])}
                        with open(f"templates/{name}.json", 'w') as f: json.dump(final_data, f)
                        reload_lib()
            elif key == 27: break
    finally:
        tracker.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()