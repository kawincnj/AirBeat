import numpy as np
import json
import os

class StaticPoseTemplate:
    def __init__(self, name="Template"):
        self.name = name
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
            # Handle both mediapipe landmarks and list of dicts/lists
            if hasattr(landmarks, 'landmark'):
                pts = landmarks.landmark
            else:
                pts = landmarks

            anchor = pts[anchor_idx]
            scale_node = pts[scale_idx]

            dist = np.sqrt((scale_node.x - anchor.x)**2 + 
                           (scale_node.y - anchor.y)**2 + 
                           (scale_node.z - anchor.z)**2)
            scale_factor = dist if dist != 0 else 1

            return np.array([
                [(pt.x - anchor.x) / scale_factor, 
                 (pt.y - anchor.y) / scale_factor, 
                 (pt.z - anchor.z) / scale_factor] 
                for pt in pts
            ])
        except (AttributeError, IndexError):
            return None

    def add_reference(self, landmarks, anchor_idx=0, scale_idx=9):
        vector = self.process_landmarks(landmarks, anchor_idx, scale_idx)
        if vector is not None:
            self.reference_vectors.append(vector)

    def clear_reference_vector(self):
        self.reference_vectors = []
        self.representative_vector = None

    def calculate_representative_vector(self):
        if not self.reference_vectors: return
        self.representative_vector = np.median(np.array(self.reference_vectors), axis=0)

    # Return [-1, 1]
    def find_similarity(self, vector, compare=None):
        # ใช้ if compare is None แทนการเช็ค list ว่าง
        target = compare if compare is not None else self.representative_vector
        if target is None or vector is None: 
            return 0.0
        return StaticPoseTemplate.cosine_similarity(target, vector)

    def save(self, directory="templates"):
        if self.representative_vector is None:
            self.calculate_representative_vector()

        if self.representative_vector is None:
            return False

        if not os.path.exists(directory):
            os.makedirs(directory)

        data = {
            "name": self.name,
            "representative_vector": self.representative_vector.tolist()
        }

        with open(os.path.join(directory, f"{self.name}.json"), 'w') as f:
            json.dump(data, f)
        return True

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.name = data.get("name", "Template")
            self.representative_vector = np.array(data["representative_vector"])
            return True
        except:
            return False

''' May be will make the dynamic posture'''