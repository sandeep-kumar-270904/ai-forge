import logging
from typing import Dict, Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from ...crud.crud_hitl import approval_ticket
from ...schemas.hitl import ApprovalTicketCreate
from langchain_core.runnables.config import RunnableConfig

logger = logging.getLogger(__name__)

class HITLInterceptor:
    @staticmethod
    async def request_approval(
        db: AsyncSession, 
        tenant_id: str, 
        trace_id: str, 
        node_name: str, 
        state: Dict[str, Any]
    ):
        """
        Called when a LangGraph node marked with interrupt_before is reached.
        Suspends the graph (via LangGraph native Checkpointer) and creates an ApprovalTicket.
        """
        ticket_create = ApprovalTicketCreate(
            trace_id=trace_id,
            node_name=node_name,
            state_snapshot=state
        )
        
        ticket = await approval_ticket.create_ticket(db, obj_in=ticket_create, tenant_id=tenant_id)
        logger.info(f"Created Approval Ticket {ticket.id} for Trace {trace_id} at Node {node_name}")
        return ticket
