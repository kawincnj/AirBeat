import numpy as np

def angle_between_vectors(v1, v2):
    return np.degrees(np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1) * np.linalg.norm(v2))))