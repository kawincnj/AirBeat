import cv2
import numpy as np
import sys
import os
import json
import time
from collections import Counter, deque

# --- SMART PATH FIX ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from plugin.hand_tracker import ThreadedHandTracker
from plugin.sound_manager import sound_manager

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

# --- NEW: AUDIO SETUP FUNCTION ---
def setup_audio():
    """Loads all chord sounds from the assets folder."""
    audio_path = os.path.join(project_root, "assets", "sounds")
    if os.path.exists(audio_path):
        sound_manager.load_directory(audio_path)
        print(f"Audio system ready. Loaded sounds from: {audio_path}")
    else:
        print(f"Warning: Audio directory not found at {audio_path}")

def draw_fretboard_ui(frame, box):
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
        cv2.line(frame, (bx, y), (bx + bw, y), (180,180,180), 2 if i > 2 else 3)
        cv2.putText(frame, string_names[i], (bx - 25, y + 5), 0, 0.5, (50, 50, 50), 1)

def draw_strum_zone(frame, y_line, is_active):
    color = (0, 255, 255) if is_active else (100, 100, 100)
    cv2.line(frame, (400, y_line), (frame.shape[1] - 20, y_line), color, 3)

def main():
    tracker = ThreadedHandTracker(min_detection_confidence=0.7)
    setup_audio() # Initialize the SoundManager
    
    neck_box = (50, 220, 240, 130)
    strum_line_y = 300
    templates = []
    current_fret, current_string, current_anchor = 1,1,8
    template_dir = os.path.join(project_root, "templates")

    # Smoothing variables for the green overlay
    smooth_fx, smooth_fy = -1, -1

    def load_templates():
        nonlocal templates
        templates = []
        if os.path.exists(template_dir):
            for f in os.listdir(template_dir):
                if f.endswith(".json"):
                    with open(os.path.join(template_dir, f), 'r') as file:
                        data = json.load(file)
                        
                        # --- FIX STARTS HERE ---
                        # If the JSON is a list of chords, loop through them
                        if isinstance(data, list):
                            items = data
                        else:
                            # If it's a single dictionary chord, put it in a list
                            items = [data]
                            
                        for d in items:
                            # Use .get() to avoid KeyErrors if some fields are missing
                            name = d.get('name', 'Unknown')
                            # Check for both 'rep_vector' (new) and 'representative_vector' (old)
                            vector = d.get('rep_vector') or d.get('representative_vector')
                            
                            if vector is not None:
                                templates.append(StaticPoseTemplate(
                                    name, 
                                    np.array(vector), 
                                    int(d.get('fret', 1)), 
                                    int(d.get('string', 1)), 
                                    int(d.get('anchor_idx', 8))
                                ))
                        # --- FIX ENDS HERE ---

    def record_chord(name, vector, fret, string, anchor):
        data = {
            'name': name,
            'rep_vector': vector.tolist(),
            'fret': fret,
            'string': string,
            'anchor_idx': anchor
        }
        filename = f"{name}.json"
        with open(os.path.join(template_dir, filename), 'w') as f:
            json.dump(data, f)
        print(f"Loaded {len(templates)} chord templates.")

    load_templates()
    stabilizer = deque(maxlen=5) # Shorter deque for faster chord switching response
    strum_active_timer = 0
    was_above = True
    current_chord = "Unknown"

    try:
        while True:
            frame, left, right = tracker.read()
            if frame is None: continue
            h, w, _ = frame.shape
            bx, by, bw, bh = neck_box

            draw_fretboard_ui(frame, neck_box)
            draw_strum_zone(frame, strum_line_y, strum_active_timer > 0)

            # 1. Left Hand: Chord & Smoothing Logic
            current_chord = "Unknown"
            target_fx, target_fy = -1, -1 

            if left:
                finger_pts = [(left.landmark[i], i) for i in range(5, 21)]
                lead_lm, lead_idx = min(finger_pts, key=lambda x: x[0].y)
                lx, ly = int(lead_lm.x * w), int(lead_lm.y * h)

                if bx < lx < bx + bw and by < ly < by + bh:
                    # Calculate Fret and String
                    f_idx = int((lx - bx) // (bw // 4))
                    s_idx = int((ly - by) / (bh / 6.0))
                    fret = f_idx + 1
                    string = max(1, min(6, 6 - s_idx))
                    current_fret = fret
                    current_string = string
                    current_anchor = lead_idx
                    
                    # Coordinate for smoothing highlight
                    target_fx = bx + (f_idx * (bw // 4))
                    target_fy = int(by + (s_idx * (bh / 6.0)))

                    # Process Landmarks & Match Template
                    processed = StaticPoseTemplate.process_landmarks(left)
                    best_sim, best_name = 0, "Unknown"
                    for t in templates:
                        sim = t.find_similarity(processed, fret, string, lead_idx)
                        if sim > best_sim:
                            best_sim, best_name = sim, t.name
                    
                    stabilizer.append(best_name if best_sim > 0.92 else "Unknown")
                    current_chord = Counter(stabilizer).most_common(1)[0][0]
                else:
                    # Hand is on screen but not on the fretboard
                    current_chord = "Align to Neck"

            # --- RENDER SMOOTHING OVERLAY ---
            if target_fx != -1:
                if smooth_fx == -1: smooth_fx, smooth_fy = target_fx, target_fy
                smooth_fx += (target_fx - smooth_fx) * 0.2
                smooth_fy += (target_fy - smooth_fy) * 0.2
                
                overlay = frame.copy()
                cv2.rectangle(overlay, (int(smooth_fx), int(smooth_fy)), 
                              (int(smooth_fx + bw//4), int(smooth_fy + bh/6.0)), (0, 255, 0), -1)
                cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
            else:
                smooth_fx, smooth_fy = -1, -1

            # 2. Right Hand: Strum Detection
            if right:
                tip_y = int(right.landmark[8].y * h)
                is_above = tip_y < strum_line_y
                if is_above != was_above:
                    if not is_above:
                        if current_chord not in ["Unknown", "Align to Neck", "No Hand"]:
                            sound_manager.play(current_chord)
                        else:
                            sound_manager.play("muted_strum")
                        strum_active_timer = 30
                    was_above = is_above
                cv2.circle(frame, (int(right.landmark[8].x * w), tip_y), 6, (0, 255, 255), -1)
            key = cv2.waitKey(1) & 0xFF
            if key == 27: break
            elif key == ord('r') and left:
                name = input("Enter chord name: ")
                if name:
                    processed = StaticPoseTemplate.process_landmarks(left)
                    record_chord(name, processed, current_fret, current_string, current_anchor)
                    load_templates()

            # UI Rendering
            if strum_active_timer > 0:
                cv2.putText(frame, "STRUM", (w - 150, 80), 1, 2.0, (0, 255, 255), 2)
                strum_active_timer -= 2

            cv2.putText(frame, f"CHORD: {current_chord}", (20, 50), 1, 2, (255, 255, 255), 2)
            cv2.imshow("AirBeat Guitar", frame)
            if cv2.waitKey(1) & 0xFF == 27: break
    finally:
        tracker.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()