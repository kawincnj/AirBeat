import cv2
import numpy as np
import mediapipe as mp
import helper_function as hp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 60)  # Set desired FPS
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce lag

# Declare
open_hand = hp.StaticPoseTemplate()

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # RGB conversion
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb.flags.writeable = False
    results = hands.process(frame_rgb)
    frame_rgb.flags.writeable = True

    left_hand = None
    right_hand = None

    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_info in enumerate(results.multi_handedness):
            label = hand_info.classification[0].label  # "Left" or "Right"
            if label == "Left":
                left_hand = results.multi_hand_landmarks[idx]
            elif label == "Right":
                right_hand = results.multi_hand_landmarks[idx]

    if right_hand:
        mp_drawing.draw_landmarks(frame, right_hand, mp_hands.HAND_CONNECTIONS)
        r_landmarks = right_hand.landmark

    if left_hand: mp_drawing.draw_landmarks(frame, left_hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Tracking", frame)

    key = cv2.waitKey(1)

    if key == ord('a'):
        open_hand.add_reference(r_landmarks)
    elif key == ord('l'):
        print(len(open_hand.reference_vector))
    elif key == ord('e'):
        open_hand.clear_reference_vector()
    elif key == ord('w'):
        open_hand.calculate_representative_vector()
        print(open_hand.representative_vector)
    elif key == ord('c'):
        print(open_hand.find_similarity(hp.StaticPoseTemplate.process_landmarks(r_landmarks)))

    if key == 27:
        break