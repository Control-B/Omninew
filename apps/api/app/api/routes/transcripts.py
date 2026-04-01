from fastapi import APIRouter, Depends

from app.api.deps import get_transcript_service
from app.schemas.common import TranscriptRecord
from app.services.transcript_service import TranscriptService

router = APIRouter()


@router.post("/")
async def create_transcript(
    payload: TranscriptRecord,
    transcript_service: TranscriptService = Depends(get_transcript_service),
) -> dict:
    return await transcript_service.store_transcript(payload)
