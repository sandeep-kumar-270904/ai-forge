from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .deps import get_db, get_current_active_user
from ..models.user import User
from ..schemas.replay import ReplaySessionResponse, ReplayStartRequest, ReplayStepRequest, ReplayOverrideRequest
from ..ai.replay.service import ReplayService
from ..crud.crud_replay import replay_session

router = APIRouter()

@router.get("/sessions", response_model=List[ReplaySessionResponse])
async def list_replay_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    sessions = await replay_session.get_by_user(db, user_id=current_user.id)
    return sessions

@router.post("/start", response_model=ReplaySessionResponse)
async def start_replay(
    request: ReplayStartRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await ReplayService.start_replay(db, user_id=current_user.id, request=request)

@router.post("/{session_id}/step")
async def step_replay(
    session_id: str,
    request: ReplayStepRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await ReplayService.step_forward(db, session_id=session_id, request=request)

@router.post("/{session_id}/override")
async def override_replay_state(
    session_id: str,
    request: ReplayOverrideRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await ReplayService.override_state(db, session_id=session_id, request=request)
