import cv2
import mediapipe as mp
import numpy as np
import helper_functions as hf

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

while cap.isOpened():
    success, frame = cap.read()
    h, w, c = frame.shape

    if not success:
        print("Ignoring empty camera frame.")
        continue
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(frame_rgb)

    # Get the coordinates
    if results.pose_landmarks:

        landmarks = results.pose_landmarks.landmark

        right_hip = landmarks[24]
        right_knee = landmarks[26]
        right_ankle = landmarks[28]

        knee = np.array([right_knee.x * w, right_knee.y * h, right_knee.z])
        hip = np.array([right_hip.x * w, right_hip.y * h, right_hip.z])
        ankle = np.array([right_ankle.x * w, right_ankle.y * h, right_ankle.z])

        v1 = hip - knee
        v2 = ankle - knee

        angle = hf.angle_between_vectors(v1, v2)
        print("Right knee angle:", angle)




    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0,255,0), thickness=2),
            mp_drawing.DrawingSpec(color=(0,0,255), thickness=2)
        )

    frame = cv2.flip(frame, 1)
    cv2.imshow("Full Body Tracking - MediaPipe Pose", frame)

    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
        break

# Cleanup
pose.close()
cap.release()
cv2.destroyAllWindows()
