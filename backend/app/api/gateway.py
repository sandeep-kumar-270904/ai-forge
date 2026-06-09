from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from .deps import get_db, get_current_active_user
from ..models.user import User
from ..schemas.gateway import ChatCompletionRequest, ChatCompletionResponse
from ..ai.gateway.service import GatewayService
from fastapi_limiter.depends import RateLimiter

router = APIRouter()

@router.post("/chat/completions", response_model=ChatCompletionResponse, dependencies=[Depends(RateLimiter(times=100, seconds=60))])
async def create_chat_completion(
    request: ChatCompletionRequest,
    x_workspace_id: str = Header(..., description="The ID of the workspace for billing and access control"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        response = await GatewayService.process_chat(
            request=request, 
            db=db, 
            tenant_id=current_user.tenant_id, 
            workspace_id=x_workspace_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
