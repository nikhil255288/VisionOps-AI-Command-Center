import sys
from pathlib import Path

import cv2
import supervision as sv
from ultralytics import YOLO

from database.db import save_event, save_tracking_point, save_alert
from cv_pipeline.event_generator import generate_events
from cv_pipeline.visitor_counter import count_visitors


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

model = YOLO(str(PROJECT_ROOT / "yolov8n.pt"))
tracker = sv.ByteTrack()

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ Could not open video:", video_path)
    sys.exit(1)

print("✅ Video opened successfully")

last_active_people = 0
last_total_visitors = 0
saved_event_keys = set()
frame_count = 0

while cap.isOpened():
    success, frame = cap.read()

    if not success or frame is None:
        print("✅ Video ended or empty frame received")
        break

    frame_count += 1

    # Process only every 5th frame for Render speed
    if frame_count % 5 != 0:
        continue

    results = model(frame, imgsz=416, conf=0.25, verbose=False)[0]
    detections = sv.Detections.from_ultralytics(results)

    # COCO class 0 = person
    detections = detections[detections.class_id == 0]

    tracked_detections = tracker.update_with_detections(detections)

    track_ids = tracked_detections.tracker_id

    if track_ids is not None:
        print("Detected people:", len(tracked_detections))
        print("Track IDs:", track_ids)

        if session_id is not None:
            for box, tracker_id in zip(
                tracked_detections.xyxy,
                tracked_detections.tracker_id
            ):
                x1, y1, x2, y2 = box

                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                save_tracking_point(session_id, tracker_id, center_x, center_y)

    total_visitors = count_visitors(track_ids)
    active_people = len(tracked_detections)

    last_active_people = active_people
    last_total_visitors = total_visitors

    if active_people >= 4:
        save_alert(
            "crowd_congestion",
            f"Crowd congestion detected: {active_people} people active in frame",
            "high"
        )

    events = generate_events(active_people, total_visitors)
    print("Events:", events)

    for event in events:
        event_key = (
            event.get("event_type"),
            event.get("zone"),
            event.get("severity"),
            session_id
        )

        if event_key not in saved_event_keys:
            if session_id is not None:
                save_event(event, session_id)
                print("✅ Event saved to DB:", event)
            else:
                print("⚠️ No session_id provided, event not saved to DB")

            saved_event_keys.add(event_key)

cap.release()

print("✅ Processing completed")
print("Final active people:", last_active_people)
print("Final unique visitors:", last_total_visitors)