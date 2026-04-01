from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_livekit_service, get_tenant_service
from app.schemas.common import VoiceTokenRequest, VoiceTokenResponse
from app.services.livekit_service import LiveKitService
from app.services.tenant_service import TenantService

router = APIRouter()


@router.post("/token", response_model=VoiceTokenResponse)
async def create_voice_token(
    payload: VoiceTokenRequest,
    livekit_service: LiveKitService = Depends(get_livekit_service),
    tenant_service: TenantService = Depends(get_tenant_service),
) -> VoiceTokenResponse:
    try:
        runtime_context = await tenant_service.resolve_runtime_context(
            widget_key=payload.widget_key,
            tenant_id=payload.tenant_id,
            store_id=payload.store_id,
            metadata={},
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not runtime_context.voice_enabled:
        raise HTTPException(status_code=403, detail="Voice mode is disabled for this assistant.")

    session_id = payload.session_id or uuid4()
    room_name = payload.room_name or (
        f"tenant-{runtime_context.tenant_id}-store-{runtime_context.store_id or 'na'}-session-{session_id}"
    )

    await tenant_service.create_voice_session(
        tenant_id=runtime_context.tenant_id,
        store_id=runtime_context.store_id,
        room_name=room_name,
        identity=payload.identity,
        session_id=session_id,
    )

    result = livekit_service.build_connection_response(
        identity=payload.identity,
        room_name=room_name,
        can_publish=payload.can_publish,
        can_subscribe=payload.can_subscribe,
    )
    return VoiceTokenResponse(**result)
