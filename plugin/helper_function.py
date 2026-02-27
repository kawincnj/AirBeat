import numpy as np

# Return [-1, 1]
def cosine_similarity(arr1, arr2):
    return np.dot(arr1, arr2)/(np.linalg.norm(arr1) * np.linalg.norm(arr2))

# Return median value of each point in vector
def representative_vector(arr, center):
    return np.median(np.array(arr) - center, axis=0)