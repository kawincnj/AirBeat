import cv2
import mediapipe as mp
import threading
import time

class ThreadedHandTracker:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5, src=0):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        self.frame = None
        self.left_hand = None
        self.right_hand = None
        self.running = True
        
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()

    def _update(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                self.running = False
                break
            
            # Flip and convert to RGB
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            results = self.hands.process(frame_rgb)
            frame_rgb.flags.writeable = True
            
            l_hand = None
            r_hand = None
            
            if results.multi_hand_landmarks and results.multi_handedness:
                for idx, hand_info in enumerate(results.multi_handedness):
                    label = hand_info.classification[0].label
                    if label == "Left":
                        l_hand = results.multi_hand_landmarks[idx]
                    elif label == "Right":
                        r_hand = results.multi_hand_landmarks[idx]
            
            self.frame = frame
            self.left_hand = l_hand
            self.right_hand = r_hand

    def read(self):
        return self.frame, self.left_hand, self.right_hand

    def draw_landmarks(self, frame, hand_landmarks):
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()
        self.hands.close()
