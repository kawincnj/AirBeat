import numpy as np

def angle_between_vectors(v1, v2):
    return np.degrees(np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1) * np.linalg.norm(v2))))

def hand_up(hand_up, z, threshold = 0.02):
    z = abs(z)
    if z >= threshold:
        hand_up = True
    else:
        hand_up = False
    return hand_up

def is_sitting(landmarks, w, h):
    SITTING_ANGLE = 120
    R_hip = landmarks[23]
    R_knee = landmarks[25]
    R_ankle = landmarks[27]

    L_hip = landmarks[24] 
    L_knee = landmarks[26] 
    L_ankle = landmarks[28]

    R_knee = np.array([R_knee.x * w, R_knee.y * h, R_knee.z])
    R_hip = np.array([R_hip.x * w, R_hip.y * h, R_hip.z])
    R_ankle = np.array([R_ankle.x * w, R_ankle.y * h, R_ankle.z])

    L_knee = np.array([L_knee.x * w, L_knee.y * h, L_knee.z])
    L_hip = np.array([L_hip.x * w, L_hip.y * h, L_hip.z])
    L_ankle = np.array([L_ankle.x * w, L_ankle.y * h, L_ankle.z])

    L_v1 = L_hip - L_knee
    L_v2 = L_ankle - L_knee
    R_v1 = R_hip - R_knee
    R_v2 = R_ankle - R_knee

    L_angle = angle_between_vectors(L_v1, L_v2)
    R_angle = angle_between_vectors(R_v1, R_v2)

    return L_angle, R_angle, (L_angle <= SITTING_ANGLE and R_angle <= SITTING_ANGLE)