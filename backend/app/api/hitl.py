from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .deps import get_db, get_current_active_user
from ..models.user import User
from ..schemas.hitl import ApprovalTicketResponse, ApprovalResolveRequest
from ..ai.hitl.service import HITLService
from ..crud.crud_hitl import approval_ticket

router = APIRouter()

@router.get("/tickets", response_model=List[ApprovalTicketResponse])
async def list_pending_tickets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    tickets = await approval_ticket.get_pending_by_tenant(db, tenant_id=current_user.tenant_id)
    return tickets

@router.post("/tickets/{ticket_id}/resolve", response_model=ApprovalTicketResponse)
async def resolve_ticket(
    ticket_id: str,
    request: ApprovalResolveRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if request.decision not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")
        
    return await HITLService.resolve_ticket(db, ticket_id=ticket_id, user_id=current_user.id, request=request)
