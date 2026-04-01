from fastapi import APIRouter, Depends

from app.api.deps import get_livekit_service
from app.schemas.common import VoiceTokenRequest, VoiceTokenResponse
from app.services.livekit_service import LiveKitService

router = APIRouter()


@router.post("/token", response_model=VoiceTokenResponse)
async def create_voice_token(
    payload: VoiceTokenRequest,
    livekit_service: LiveKitService = Depends(get_livekit_service),
) -> VoiceTokenResponse:
    result = livekit_service.build_connection_response(
        identity=payload.identity,
        room_name=payload.room_name,
        can_publish=payload.can_publish,
        can_subscribe=payload.can_subscribe,
    )
    return VoiceTokenResponse(**result)
