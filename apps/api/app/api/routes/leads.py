from fastapi import APIRouter, Depends

from app.api.deps import get_lead_service
from app.schemas.common import LeadCapturePayload
from app.services.lead_service import LeadService

router = APIRouter()


@router.post("/")
async def create_lead(
    payload: LeadCapturePayload,
    lead_service: LeadService = Depends(get_lead_service),
) -> dict:
    return await lead_service.capture_lead(payload)
