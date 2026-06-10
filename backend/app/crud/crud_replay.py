from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.replay import ReplaySession
from ..schemas.replay import ReplaySessionCreate
from .base import CRUDBase

class CRUDReplaySession(CRUDBase[ReplaySession, ReplaySessionCreate, ReplaySessionCreate]):
    async def create_session(self, db: AsyncSession, *, obj_in: ReplaySessionCreate) -> ReplaySession:
        db_obj = ReplaySession(
            original_trace_id=obj_in.original_trace_id,
            user_id=obj_in.user_id,
            mock_tools=obj_in.mock_tools
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
        
    async def get_by_user(self, db: AsyncSession, *, user_id: str) -> List[ReplaySession]:
        result = await db.execute(
            select(ReplaySession)
            .filter(ReplaySession.user_id == user_id)
            .order_by(ReplaySession.updated_at.desc())
        )
        return list(result.scalars().all())

replay_session = CRUDReplaySession(ReplaySession)
