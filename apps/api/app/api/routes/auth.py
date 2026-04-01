from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def auth_status() -> dict[str, str]:
    return {"status": "pending", "message": "MVP uses manual token input. OAuth arrives later."}
