from ultralytics import YOLO
import cv2

model = YOLO(model="test/best.pt")

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret,frame = cap.read()
    if not ret:
        break
    result = model.predict(frame)
    cv2.imshow("orginal",frame)
    annotated = result[0].plot()
    cv2.imshow("annotated",annotated)
    cv2.waitKey(10)