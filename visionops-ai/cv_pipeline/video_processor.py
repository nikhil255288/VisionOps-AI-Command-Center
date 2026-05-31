import sys
from pathlib import Path

import cv2
import supervision as sv
from ultralytics import YOLO

from database.db import save_event, save_tracking_point, save_alert
from cv_pipeline.event_generator import generate_events
from cv_pipeline.visitor_counter import count_visitors


# -----------------------------
# Resolve video path safely
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

video_path = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else PROJECT_ROOT / "sample_data" / "road_traffic.mp4"
)

if not video_path.is_absolute():
    video_path = PROJECT_ROOT / video_path

video_path = str(video_path)

session_id = int(sys.argv[2]) if len(sys.argv) > 2 else None

print("Video path:", video_path)
print("Session ID:", session_id)



model = YOLO("yolov8n.pt")
tracker = sv.ByteTrack()

box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()


cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ Could not open video:", video_path)
    sys.exit(1)

print("✅ Video opened successfully")


last_active_people = 0
last_total_visitors = 0
saved_event_keys = set()

while cap.isOpened():
    success, frame = cap.read()

    if not success or frame is None:
        print("✅ Video ended or empty frame received")
        break

    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)

    detections = detections[detections.class_id == 0]

    tracked_detections = tracker.update_with_detections(detections)
    if session_id is not None and tracked_detections.tracker_id is not None:
        for box, tracker_id in zip(tracked_detections.xyxy, tracked_detections.tracker_id):
            x1, y1, x2, y2 = box

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            save_tracking_point(session_id, tracker_id, center_x, center_y)

    track_ids = tracked_detections.tracker_id

    total_visitors = count_visitors(track_ids)
    active_people = len(tracked_detections)
    if active_people >= 5:
        save_alert(
            "crowd_congestion",
            f"Crowd congestion detected: {active_people} people active in frame",
            "high"
        )

    last_active_people = active_people
    last_total_visitors = total_visitors

    events = generate_events(active_people, total_visitors)

    for event in events:
        print("EVENT:", event)

        event_key = (
            event.get("event_type"),
            event.get("zone"),
            event.get("severity"),
            session_id
        )

        if event_key not in saved_event_keys:
            if session_id is not None:
                save_event(event, session_id)
                print("✅ Event saved to DB")
            else:
                print("⚠️ No session_id provided, event not saved to DB")

            saved_event_keys.add(event_key)

    labels = [
        f"Person #{tracker_id}"
        for tracker_id in tracked_detections.tracker_id
    ]

    annotated_frame = box_annotator.annotate(
        scene=frame.copy(),
        detections=tracked_detections
    )

    annotated_frame = label_annotator.annotate(
        scene=annotated_frame,
        detections=tracked_detections,
        labels=labels
    )

    cv2.rectangle(annotated_frame, (20, 20), (430, 100), (0, 0, 0), -1)

    cv2.putText(
        annotated_frame,
        f"Active People: {active_people}",
        (35, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Unique Visitors: {total_visitors}",
        (35, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow("VisionOps AI - Visitor Tracking", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()

print("✅ Processing completed")
print("Final active people:", last_active_people)
print("Final unique visitors:", last_total_visitors)