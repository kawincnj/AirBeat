import cv2

# --- Setup Configuration ---
num_keys = 14
w_width, w_height = 40, 200
b_width, b_height = 25, 120
start_x, start_y = 50, 50

white_keys = []
black_keys = []

# 1. Pre-calculate White Keys
for i in range(num_keys):
    x1 = start_x + (i * w_width)
    # Store as: [x1, y1, x2, y2, is_pressed]
    white_keys.append({"rect": (x1, start_y, x1 + w_width, start_y + w_height), "pressed": False})

# 2. Pre-calculate Black Keys
for i in range(num_keys - 1):
    if i % 7 in [2, 6]: # Skip gaps between E-F and B-C
        continue
    x1 = start_x + (i * w_width) + (w_width - b_width // 2)
    black_keys.append({"rect": (x1, start_y, x1 + b_width, start_y + b_height), "pressed": False})

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    # frame = cv2.flip(frame, 1) # Mirror for natural interaction
    frame = cv2.flip(frame, -1)

    # 3. Draw White Keys
    for k in white_keys:
        x1, y1, x2, y2 = k["rect"]
        color = (200, 200, 200) if k["pressed"] else (255, 255, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)

    # 4. Draw Black Keys
    for k in black_keys:
        x1, y1, x2, y2 = k["rect"]
        color = (50, 50, 50) if k["pressed"] else (0, 0, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    
    cv2.imshow('Virtual Piano Map', frame)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()