from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models.observability import AgentRun, AgentSpan
from ..schemas.observability import AgentRunCreate, AgentSpanCreate
from .base import CRUDBase

class CRUDAgentRun(CRUDBase[AgentRun, AgentRunCreate, AgentRunCreate]):
    async def get_with_spans(self, db: AsyncSession, *, id: str) -> Optional[AgentRun]:
        result = await db.execute(
            select(AgentRun)
            .filter(AgentRun.id == id)
            .options(selectinload(AgentRun.spans))
        )
        return result.scalars().first()
        
    async def get_by_workspace(self, db: AsyncSession, *, workspace_id: str) -> List[AgentRun]:
        result = await db.execute(
            select(AgentRun)
            .filter(AgentRun.workspace_id == workspace_id)
            .order_by(AgentRun.started_at.desc())
        )
        return list(result.scalars().all())

class CRUDAgentSpan(CRUDBase[AgentSpan, AgentSpanCreate, AgentSpanCreate]):
    async def create_span(self, db: AsyncSession, *, obj_in: AgentSpanCreate) -> AgentSpan:
        db_obj = AgentSpan(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

run = CRUDAgentRun(AgentRun)
span = CRUDAgentSpan(AgentSpan)
