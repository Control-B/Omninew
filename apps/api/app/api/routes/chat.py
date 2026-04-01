from fastapi import APIRouter, Depends

from app.api.deps import get_conversation_service
from app.schemas.common import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    result = await conversation_service.handle_chat(payload)
    return ChatResponse(**result)
