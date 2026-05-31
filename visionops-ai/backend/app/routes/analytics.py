from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def analytics_summary():
    return {
        "store_id": 1,
        "current_visitors": 24,
        "total_visitors_today": 186,
        "average_dwell_time_minutes": 12.4,
        "queue_alerts": 3,
        "anomaly_alerts": 2,
        "peak_hour": "6 PM - 7 PM",
        "recommendation": "Open one additional billing counter during evening peak hours."
    }