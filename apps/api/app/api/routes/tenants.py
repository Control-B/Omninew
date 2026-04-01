from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_tenants() -> dict[str, list[dict[str, str]]]:
    return {"items": []}
