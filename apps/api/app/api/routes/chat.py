from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_conversation_service
from app.schemas.common import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    try:
        result = await conversation_service.handle_chat(payload)
    except ValueError as error:
        status_code = 402 if "Plan limit reached" in str(error) else 400
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    return ChatResponse(**result)
