import numpy as np

class StaticPoseTemplate:
    def __init__(self):
        self.representative_vector = None
        self.reference_vectors = []

    @staticmethod # Not to pass 'self': Normally it will pass 'self' into the function so the parameters will over
    def cosine_similarity(arr1, arr2):
        if arr1 is None or arr2 is None: return 0

        v1 = arr1.ravel() # ravel similar to flatten() but faster
        v2 = arr2.ravel()
        try:
            return np.dot(v1, v2)/(np.linalg.norm(v1) * np.linalg.norm(v2))
        except:
            return 0.0

    @staticmethod
    # Normalize landmarks
    def process_landmarks(landmarks, anchor_idx=0, scale_idx=9):
        if landmarks is None: return None
        try:
            anchor = landmarks[anchor_idx]
            scale_node = landmarks[scale_idx]
            
            dist = np.sqrt((scale_node.x - anchor.x)**2 + 
                           (scale_node.y - anchor.y)**2 + 
                           (scale_node.z - anchor.z)**2)
            scale_factor = dist if dist != 0 else 1

            return np.array([
                [(pt.x - anchor.x) / scale_factor, 
                 (pt.y - anchor.y) / scale_factor, 
                 (pt.z - anchor.z) / scale_factor] 
                for pt in landmarks
            ])
        except (AttributeError, IndexError):
            return None

    def add_reference(self, landmarks, anchor_idx=0, scale_idx=9):
        vector = self.process_landmarks(landmarks, anchor_idx, scale_idx)
        if vector is not None:
            self.reference_vectors.append(vector)
    
    def clear_reference_vector(self):
        self.reference_vectors = []
    
    def calculate_representative_vector(self):
        if not self.reference_vectors: return
        self.representative_vector = np.median(np.array(self.reference_vectors), axis=0)

    # Return [-1, 1]
    def find_similarity(self, vector):
        if self.representative_vector is None or vector is None: return 0

        return StaticPoseTemplate.cosine_similarity(self.representative_vector, vector)
    
''' May be will make the dynamic posture'''