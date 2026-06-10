from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentSpanBase(BaseModel):
    name: str
    span_type: str
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

class AgentSpanCreate(AgentSpanBase):
    id: str
    trace_id: str
    parent_span_id: Optional[str] = None

class AgentSpanResponse(AgentSpanBase):
    id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class AgentSpanTreeNode(AgentSpanResponse):
    children: List['AgentSpanTreeNode'] = []

class AgentRunBase(BaseModel):
    workspace_id: str
    workflow_id: str
    status: str

class AgentRunCreate(AgentRunBase):
    id: str

class AgentRunResponse(AgentRunBase):
    id: str
    tenant_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AgentRunTimelineResponse(AgentRunResponse):
    total_duration_ms: Optional[int] = None
    spans: List[AgentSpanTreeNode] = []
