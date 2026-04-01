from fastapi import APIRouter

from app.prompts.do_agent_blueprint import build_agent_blueprint
from app.schemas.common import AgentBlueprintResponse

router = APIRouter()


@router.get("/blueprint", response_model=AgentBlueprintResponse)
async def get_agent_blueprint() -> AgentBlueprintResponse:
    return build_agent_blueprint()