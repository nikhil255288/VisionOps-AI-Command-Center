from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/")
def get_alerts():
    return [
        {
            "alert_id": 1,
            "type": "long_queue",
            "severity": "high",
            "message": "Billing counter queue exceeded threshold",
            "status": "active"
        }
    ]