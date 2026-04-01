from fastapi import APIRouter

router = APIRouter()


@router.post("/livekit")
async def livekit_webhook(event: dict) -> dict:
    return {"received": True, "event_type": event.get("type")}
