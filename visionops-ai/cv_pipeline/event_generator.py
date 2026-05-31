from datetime import datetime

def generate_events(active_people, total_visitors):
    events = []

    if active_people >= 5:
        events.append({
            "event_type": "crowd_alert",
            "zone": "store_front",
            "severity": "medium",
            "message": f"High crowd detected: {active_people} active people",
            "timestamp": datetime.now().isoformat()
        })

    if active_people >= 8:
        events.append({
            "event_type": "queue_alert",
            "zone": "billing_counter",
            "severity": "high",
            "message": f"Possible queue formation detected with {active_people} people",
            "timestamp": datetime.now().isoformat()
        })

    if total_visitors >= 20:
        events.append({
            "event_type": "footfall_spike",
            "zone": "store",
            "severity": "medium",
            "message": f"Visitor count crossed {total_visitors}",
            "timestamp": datetime.now().isoformat()
        })

    return events