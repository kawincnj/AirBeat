import cv2
import sys
import os

# --- SMART PATH FIX ---
# This allows you to run the script directly from your editor or terminal
# It finds the project root (AirBeat) and adds it to Python's search path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ----------------------

from plugin.hand_tracker import ThreadedHandTracker
from plugin.sound_manager import sound_manager
import pygame

# =========================
# CONFIG
# =========================
keys = ["C4","D4","E4","F4","G4","A4","B4","C5","D5","E5","F5","G5","A5"]

# Load sound files (convert note names to lowercase for file lookup)
# C4 -> c4.mp3 or c4.wav, D4 -> d4.mp3 or d4.wav, etc.
sound_dir = os.path.join(os.path.dirname(__file__), "sound_piano")
print(f"Loading sounds from: {sound_dir}")
for note in keys:
    # Try MP3 first, then WAV
    for ext in [".mp3", ".wav"]:
        sound_file = os.path.join(sound_dir, f"{note.lower()}{ext}")
        if os.path.exists(sound_file) and os.path.getsize(sound_file) > 0:
            sound_manager.load_sound(note, sound_file)
            print(f"✓ Loaded {note} ({ext})")
            break
    else:
        print(f"✗ Missing: {note.lower()}.mp3 or .wav")

# Track previous state to detect note on/off transitions
previous_pressed_indices = set()

# =========================
# TRACKER
# =========================
tracker = ThreadedHandTracker(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# =========================
# FUNCTION
# =========================
# Finger tip landmark IDs in MediaPipe
FINGER_TIPS = {
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20
}

FINGER_COLORS = {
    "thumb": (255, 0, 0),      # Blue
    "index": (0, 255, 0),       # Green
    "middle": (0, 255, 255),    # Yellow
    "ring": (255, 0, 255),      # Magenta
    "pinky": (255, 165, 0)      # Orange
}

def get_key_index(x, width):
    key_width = width // len(keys)
    return x // key_width

def get_all_finger_tips(hand_landmarks, w, h):
    """Get all 5 finger tips from hand landmarks"""
    finger_positions = {}
    for finger_name, landmark_id in FINGER_TIPS.items():
        landmark = hand_landmarks.landmark[landmark_id]
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        finger_positions[finger_name] = (x, y)
    return finger_positions

def draw_piano(frame, pressed_indices=None):
    """Draw piano keyboard with highlight for pressed keys"""
    if pressed_indices is None:
        pressed_indices = []
    
    h, w, _ = frame.shape
    keyboard_height = int(h * 0.15)
    key_width = w // len(keys)
    y_start = h - keyboard_height

    overlay = frame.copy()

    for i, note in enumerate(keys):
        x1 = i * key_width
        x2 = x1 + key_width
        y1 = y_start
        y2 = h

        # 🎯 highlight ถ้ากด
        if i in pressed_indices:
            cv2.rectangle(overlay, (x1,y1), (x2,y2), (0,255,0), -1)
        else:
            cv2.rectangle(overlay, (x1,y1), (x2,y2), (255,255,255), -1)

        # border
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,0), 2)

        # text
        cv2.putText(frame, note,
                    (x1 + 10, y2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,0,0),
                    2)

    # 🔥 transparency
    alpha = 0.4
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    return frame, y_start


def draw_close_button(frame):
    """Draw X button in top-right corner"""
    h, w, _ = frame.shape
    button_size = 50
    margin = 10
    
    x1 = w - button_size - margin
    y1 = margin
    x2 = w - margin
    y2 = button_size + margin
    
    # Draw button rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), -1)
    
    # Draw X
    thickness = 3
    cv2.line(frame, (x1 + 10, y1 + 10), (x2 - 10, y2 - 10), (0, 0, 255), thickness)
    cv2.line(frame, (x2 - 10, y1 + 10), (x1 + 10, y2 - 10), (0, 0, 255), thickness)
    
    return (x1, y1, x2, y2)


def check_close_button_clicked(finger_x, finger_y, button_rect):
    """Check if finger is touching the close button"""
    x1, y1, x2, y2 = button_rect
    return x1 <= finger_x <= x2 and y1 <= finger_y <= y2


# =========================
# MAIN
# =========================
try:
    close_button_rect = None
    
    while True:
        frame, left_hand, right_hand = tracker.read()
        
        if frame is None:
            continue

        h, w, _ = frame.shape

        pressed_indices = []
        played_notes = []
        should_close = False

        # วาด piano ก่อน
        frame, y_start = draw_piano(frame)
        
        # วาดปุ่ม X
        close_button_rect = draw_close_button(frame)

        # Process both hands
        for hand_landmarks in [left_hand, right_hand]:
            if hand_landmarks is not None:
                # วาดมือ
                # tracker.draw_landmarks(frame, hand_landmarks)

                # Get all 5 finger tips
                finger_positions = get_all_finger_tips(hand_landmarks, w, h)

                # Check each finger tip
                for finger_name, (x, y) in finger_positions.items():
                    color = FINGER_COLORS[finger_name]
                    
                    # วาดจุดนิ้ว
                    # cv2.circle(frame, (x, y), 10, color, -1)

                    # 🎯 เช็คว่ากด X ปุ่มหรือไม่
                    if check_close_button_clicked(x, y, close_button_rect):
                        should_close = True

                    # 🎯 เช็คว่ากด key ไหม (นิ้วอยู่ล่าง keyboard)
                    if y > y_start:
                        key_index = get_key_index(x, w)
                        
                        if 0 <= key_index < len(keys):
                            pressed_indices.append(key_index)

        # 🔥 Convert to set to detect newly pressed notes
        current_pressed_set = set(pressed_indices)
        
        # Detect NEW key presses (keys pressed this frame but not in previous frame)
        newly_pressed = current_pressed_set - previous_pressed_indices
        
        # Play sound only for newly pressed notes
        for key_index in newly_pressed:
            note = keys[key_index]
            sound_manager.play(note, volume=0.8)
            played_notes.append(note)
        
        # Update previous state for next frame
        previous_pressed_indices = current_pressed_set

        # 🔥 redraw เพื่อ highlight keys ที่กด
        frame, _ = draw_piano(frame, pressed_indices)
        
        # redraw close button
        close_button_rect = draw_close_button(frame)

        # Display all played notes
        if played_notes:
            y_offset = 50
            cv2.putText(frame, "PLAYING:", (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            for idx, note_text in enumerate(played_notes):
                cv2.putText(frame, note_text, (50, y_offset + 30 * (idx + 1)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Air Piano", frame)

        if should_close or cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    tracker.stop()
    cv2.destroyAllWindows()
    pygame.mixer.quit()