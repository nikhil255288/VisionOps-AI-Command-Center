from datetime import datetime


def generate_events(active_people, total_visitors):
    events = []

    if active_people >= 1:
        events.append({
            "event_type": "person_detected",
            "zone": "store_front",
            "severity": "low",
            "message": f"{active_people} active person detected",
            "timestamp": datetime.now().isoformat()
        })

    if active_people >= 2:
        events.append({
            "event_type": "crowd_alert",
            "zone": "store_front",
            "severity": "medium",
            "message": f"Crowd activity detected: {active_people} active people",
            "timestamp": datetime.now().isoformat()
        })

    if total_visitors >= 1:
        events.append({
            "event_type": "footfall_spike",
            "zone": "store",
            "severity": "medium",
            "message": f"Visitor count crossed {total_visitors}",
            "timestamp": datetime.now().isoformat()
        })

    return events