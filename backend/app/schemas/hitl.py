from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class ApprovalTicketBase(BaseModel):
    trace_id: str
    node_name: str
    state_snapshot: Optional[Dict[str, Any]] = None

class ApprovalTicketCreate(ApprovalTicketBase):
    pass

class ApprovalTicketResponse(ApprovalTicketBase):
    id: str
    tenant_id: str
    status: str
    requested_at: datetime
    resolved_at: Optional[datetime] = None
    resolver_id: Optional[str] = None
    resolution_payload: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class ApprovalResolveRequest(BaseModel):
    decision: str # "approved" or "rejected"
    state_overrides: Optional[Dict[str, Any]] = None
