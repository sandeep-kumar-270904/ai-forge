import uuid
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ...crud.crud_replay import replay_session
from ...crud.crud_observability import agent_run
from ...schemas.replay import ReplaySessionCreate, ReplayStartRequest, ReplayStepRequest, ReplayOverrideRequest

class ReplayService:
    @staticmethod
    async def start_replay(db: AsyncSession, user_id: str, request: ReplayStartRequest):
        run = await agent_run.get(db, id=request.trace_id)
        if not run:
             raise HTTPException(status_code=404, detail="Trace not found")
             
        session_create = ReplaySessionCreate(
            original_trace_id=request.trace_id,
            user_id=user_id,
            mock_tools=request.mock_tools
        )
        session = await replay_session.create_session(db, obj_in=session_create)
        return session

    @staticmethod
    async def step_forward(db: AsyncSession, session_id: str, request: ReplayStepRequest):
        session = await replay_session.get(db, id=session_id)
        if not session:
             raise HTTPException(status_code=404, detail="Replay session not found")
             
        session.current_step += 1
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return {"status": "stepped", "current_step": session.current_step, "node_executed": request.node_name}

    @staticmethod
    async def override_state(db: AsyncSession, session_id: str, request: ReplayOverrideRequest):
        session = await replay_session.get(db, id=session_id)
        if not session:
             raise HTTPException(status_code=404, detail="Replay session not found")
             
        return {"status": "state_overridden", "updates": request.state_updates}
