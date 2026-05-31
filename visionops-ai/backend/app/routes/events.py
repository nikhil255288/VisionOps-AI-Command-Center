from fastapi import APIRouter

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

@router.get("/")
def get_events():
    return [
        {
            "event_id": 1,
            "event_type": "queue_alert",
            "zone": "billing_counter",
            "severity": "high",
            "timestamp": "2026-05-30T18:15:00"
        },
        {
            "event_id": 2,
            "event_type": "loitering_detected",
            "zone": "cosmetics_section",
            "severity": "medium",
            "timestamp": "2026-05-30T18:22:00"
        }
    ]