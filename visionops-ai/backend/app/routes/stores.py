from fastapi import APIRouter

router = APIRouter(prefix="/stores", tags=["Stores"])

@router.get("/")
def get_stores():
    return [
        {
            "store_id": 1,
            "name": "Purplle Smart Store",
            "location": "Hyderabad",
            "status": "active"
        }
    ]