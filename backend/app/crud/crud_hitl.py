from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.hitl import ApprovalTicket
from ..schemas.hitl import ApprovalTicketCreate
from .base import CRUDBase

class CRUDApprovalTicket(CRUDBase[ApprovalTicket, ApprovalTicketCreate, ApprovalTicketCreate]):
    async def create_ticket(self, db: AsyncSession, *, obj_in: ApprovalTicketCreate, tenant_id: str) -> ApprovalTicket:
        db_obj = ApprovalTicket(
            tenant_id=tenant_id,
            trace_id=obj_in.trace_id,
            node_name=obj_in.node_name,
            state_snapshot=obj_in.state_snapshot
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
        
    async def get_pending_by_tenant(self, db: AsyncSession, *, tenant_id: str) -> List[ApprovalTicket]:
        result = await db.execute(
            select(ApprovalTicket)
            .filter(ApprovalTicket.tenant_id == tenant_id, ApprovalTicket.status == "pending")
            .order_by(ApprovalTicket.requested_at.desc())
        )
        return list(result.scalars().all())

approval_ticket = CRUDApprovalTicket(ApprovalTicket)
