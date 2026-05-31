import supervision as sv

tracker = sv.ByteTrack()

def update_tracks(detections):
    return tracker.update_with_detections(detections)