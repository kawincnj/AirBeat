import cv2
import mediapipe as mp
import numpy as np
import helper_functions as hf
import sound_loading as sl
from time import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.7
)

# Camera setup with optimized settings
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)  # Set desired FPS
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce lag

# Declare Variable
left_hand_up = True
right_hand_up = True
left_hand_upper = None
right_hand_upper = None
threshold_upper = 0
threshold_lower = 0
Y_seperate = 0

# Calibrate Variables
is_calibrate = True
calibrate_Zpoint_upper = []
calibrate_Zpoint_lower = []
start_time = time()
time_set = 5

# Performance optimization variables
frame_skip = 0
FRAME_SKIP_COUNT = 0  # Process every frame for maximum responsiveness

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Frame skipping for non-critical rendering (disabled for max speed)
    frame_skip += 1
    process_frame = frame_skip > FRAME_SKIP_COUNT
    if process_frame:
        frame_skip = 0

    # RGB conversion
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb.flags.writeable = False
    results = hands.process(frame_rgb)
    frame_rgb.flags.writeable = True

    # RESULTS - extract once
    left_hand = None
    right_hand = None

    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_info in enumerate(results.multi_handedness):
            label = hand_info.classification[0].label  # "Left" or "Right"
            if label == "Left":
                left_hand = results.multi_hand_landmarks[idx]
            elif label == "Right":
                right_hand = results.multi_hand_landmarks[idx]


    if is_calibrate:
        try:
            left_center = (int(left_hand.landmark[9].x * w), int(left_hand.landmark[9].y * h))
            right_center = (int(right_hand.landmark[9].x * w), int(right_hand.landmark[9].y * h))
            cv2.circle(frame, left_center, 50, (0, 0, 255), 4)
            cv2.circle(frame, right_center, 50, (0, 0, 255), 4)
        except:
            pass

        sec_now = time() - start_time
        if sec_now <= time_set:
            cv2.putText(frame, 'Start calibrate in:', (90, 190), 1, 3, (20, 123, 13), 5)
            cv2.putText(frame, str(time_set - int(sec_now)), (300, 260), 1, 4, (0, 255, 0), 5)
        else:
            cv2.putText(frame, 'Start calibrate', (50, 60), 1, 3, (20, 123, 13), 5)
            try:
                calibrate_Zpoint_upper.append(min(left_hand.landmark[12].z, right_hand.landmark[12].z))
                calibrate_Zpoint_lower.append(max(left_hand.landmark[12].z, right_hand.landmark[12].z))
                if (time() - start_time >= (3 + time_set)):
                    threshold_upper = abs(np.average(calibrate_Zpoint_upper))
                    threshold_lower = abs(np.average(calibrate_Zpoint_lower))
                    Y_seperate = int(min(left_hand.landmark[1].y, right_hand.landmark[1].y) * h)
                    is_calibrate = False
            except:
                pass
    else:
        if right_hand:
            landmarks = right_hand.landmark
            z_value = landmarks[12].z
        
            right_hand_upper = int(landmarks[1].y * h) < Y_seperate
            
            is_hand_down = not hf.hand_up(right_hand_up, z_value, right_hand_upper, threshold_upper, threshold_lower)
            if right_hand_up and is_hand_down:
                if right_hand_upper:
                    sl.play_cajon_on()
                else:
                    sl.play_cajon_off()
            
            right_hand_up = not is_hand_down
  
        if left_hand:
            landmarks = left_hand.landmark
            z_value = landmarks[12].z

            left_hand_upper = int(landmarks[1].y * h) < Y_seperate
            
            is_hand_down = not hf.hand_up(left_hand_up, z_value, right_hand_upper, threshold_upper, threshold_lower)
            if left_hand_up and is_hand_down:
                if left_hand_upper:
                    sl.play_cajon_on()
                else:
                    sl.play_cajon_off()
            
            left_hand_up = not is_hand_down

        if process_frame:

            cv2.line(frame, (0, Y_seperate), (640, Y_seperate), (255,0,0), 3, 2)

            if right_hand:
                status_text = "UP" if right_hand_up else "DOWN"
                color = (0, 255, 0) if right_hand_up else (0, 0, 255)
                cv2.putText(frame, status_text, (530, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                mp_drawing.draw_landmarks(frame, right_hand, mp_hands.HAND_CONNECTIONS)
                
            if left_hand:
                status_text = "UP" if left_hand_up else "DOWN"
                color = (0, 255, 0) if left_hand_up else (0, 0, 255)
                cv2.putText(frame, status_text, (80, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                mp_drawing.draw_landmarks(frame, left_hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Optimized Full Body Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Changed to 1ms for faster response
        break

# Cleanup
hands.close()
cap.release()
cv2.destroyAllWindows()
