from fastapi import FastAPI

from backend.app.routes.analytics import router as analytics_router
from backend.app.routes.events import router as events_router
from backend.app.routes.alerts import router as alerts_router
from backend.app.routes.stores import router as stores_router

app = FastAPI(
    title="VisionOps AI",
    version="1.0.0"
)

app.include_router(analytics_router)
app.include_router(events_router)
app.include_router(alerts_router)
app.include_router(stores_router)

@app.get("/")
def root():
    return {
        "project": "VisionOps AI",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }