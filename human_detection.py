from ultralytics import YOLO
import cv2
import keyboard

model = YOLO("yolo11n.pt")  # First run downloads the model

# Use webcam (0), or IP stream like "http://192.168.1.12:8080/video"
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Run detection
    results = model(frame, verbose=False)

    # Check if any detection is class "person" (COCO class 0)
    person_detected = any(cls == 0 for cls in results[0].boxes.cls.int().tolist())

    print("Human detected!" if person_detected else "No human")

    annotated_frame = results[0].plot()
    cv2.imshow("YOLOv5 Human Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if keyboard.is_pressed('esc'):
        print("Exit key pressed.")
        break

cap.release()
cv2.destroyAllWindows()
