from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect(frame):
    results = model(frame)

    detections = []

    for result in results:
        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == 0:  # person

                detections.append({
                    "bbox": box.xyxy[0].tolist(),
                    "confidence": float(box.conf[0])
                })

    return detections