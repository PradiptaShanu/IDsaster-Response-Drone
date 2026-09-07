import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)
log_file = open("coordinates_log.txt", "w")

def draw_grid(frame, grid_size=50):
    h, w, _ = frame.shape
    for x in range(0, w, grid_size):
        cv2.line(frame, (x, 0), (x, h), (100, 100, 100), 1)
    for y in range(0, h, grid_size):
        cv2.line(frame, (0, y), (w, y), (100, 100, 100), 1)
    return frame

def draw_arrow(frame, cx, cy, fx, fy, threshold=30):
    dx = cx - fx
    dy = cy - fy
    if abs(dx) > threshold or abs(dy) > threshold:
        direction = (int(fx + dx * 0.5), int(fy + dy * 0.5))
        cv2.arrowedLine(frame, (fx, fy), direction, (0, 0, 255), 2, tipLength=0.3)
        cv2.putText(frame, "Adjust Camera", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    input_frame = cv2.resize(frame, (1280,720))
    results = model(input_frame)[0]
    fx = input_frame.shape[1] // 2
    fy = input_frame.shape[0] // 2
    cv2.circle(input_frame, (fx, fy), 5, (255, 255, 0), -1)

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        if label.lower() != 'person':
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        log_file.write(f"{cx},{cy}\n")
        cv2.rectangle(input_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(input_frame, f'Human ({cx},{cy})', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.circle(input_frame, (cx, cy), 4, (0, 0, 255), -1)
        draw_arrow(input_frame, cx, cy, fx, fy)

    input_frame = draw_grid(input_frame)
    cv2.imshow('YOLOv8 Human Detection with Direction', input_frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
log_file.close()
cv2.destroyAllWindows()
