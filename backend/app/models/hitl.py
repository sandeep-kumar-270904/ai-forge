import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class ApprovalTicket(Base):
    __tablename__ = "approval_tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    trace_id = Column(String, ForeignKey("agent_runs.id"), nullable=False, index=True)
    node_name = Column(String, nullable=False)
    status = Column(String, default="pending", index=True) # pending, approved, rejected, expired
    requested_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolver_id = Column(String, ForeignKey("users.id"), nullable=True)
    state_snapshot = Column(JSONB, nullable=True)
    resolution_payload = Column(JSONB, nullable=True)

    run = relationship("AgentRun")
    resolver = relationship("User")
