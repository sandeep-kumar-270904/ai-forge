import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ...crud.crud_hitl import approval_ticket
from ...schemas.hitl import ApprovalResolveRequest

class HITLService:
    @staticmethod
    async def resolve_ticket(db: AsyncSession, ticket_id: str, user_id: str, request: ApprovalResolveRequest):
        """
        Resolves a pending approval ticket, applying any state overrides, and resumes the LangGraph thread.
        """
        ticket = await approval_ticket.get(db, id=ticket_id)
        if not ticket:
             raise HTTPException(status_code=404, detail="Approval ticket not found")
             
        if ticket.status != "pending":
             raise HTTPException(status_code=400, detail=f"Ticket already resolved with status: {ticket.status}")

        ticket.status = request.decision
        ticket.resolved_at = datetime.utcnow()
        ticket.resolver_id = user_id
        ticket.resolution_payload = request.state_overrides
        
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        
        return ticket
