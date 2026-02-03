import cv2
import mediapipe as mp
import numpy as np
import helper_functions as hf
import sound_loading as sl

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(640/1))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(480/1))

left_hand_up = True
right_hand_up = True

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    frame_rgb.flags.writeable = False
    results = holistic.process(frame_rgb)
    frame_rgb.flags.writeable = True

    # RESULTS
    pose = results.pose_landmarks
    left_hand = results.right_hand_landmarks
    right_hand = results.left_hand_landmarks

    if pose:
        landmarks = pose.landmark
        
        L_angle, R_angle, is_sitting = hf.is_sitting(landmarks, w, h)
        
        status_text = "IS SITTING" if is_sitting else "NOT SITTING"
        color = (0, 255, 0) if is_sitting else (0, 0, 255)
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Draw Pose Landmarks
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=1)
        )

    if right_hand: #SHOW RIGHT
        landmarks = right_hand.landmark

        if right_hand_up and (not hf.hand_up(right_hand_up, landmarks[12].z)):
            sl.play_cajon_on()

        right_hand_up = hf.hand_up(right_hand_up, landmarks[12].z)

        status_text = "UP" if right_hand_up else "DOWN"
        color = (0, 255, 0) if right_hand_up else (0, 0, 255)
        cv2.putText(frame, status_text, (530, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        mp_drawing.draw_landmarks(frame, right_hand, mp_holistic.HAND_CONNECTIONS)
        
    if left_hand: #SHOW LEFT
        landmarks = left_hand.landmark

        if left_hand_up and (not hf.hand_up(left_hand_up, landmarks[12].z)):
            sl.play_cajon_off()
        left_hand_up = hf.hand_up(left_hand_up, landmarks[12].z)

        status_text = "UP" if left_hand_up else "DOWN"
        color = (0, 255, 0) if left_hand_up else (0, 0, 255)
        cv2.putText(frame, status_text, (80, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        mp_drawing.draw_landmarks(frame, left_hand, mp_holistic.HAND_CONNECTIONS)

    cv2.imshow("Optimized Full Body Tracking", frame)

    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
        break

# Cleanup
holistic.close()
cap.release()
cv2.destroyAllWindows()