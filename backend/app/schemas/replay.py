from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class ReplaySessionBase(BaseModel):
    mock_tools: bool = True

class ReplaySessionCreate(ReplaySessionBase):
    original_trace_id: str
    user_id: str

class ReplaySessionResponse(ReplaySessionBase):
    id: str
    original_trace_id: str
    user_id: str
    current_step: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReplayStartRequest(BaseModel):
    trace_id: str
    mock_tools: bool = True

class ReplayStepRequest(BaseModel):
    node_name: str

class ReplayOverrideRequest(BaseModel):
    state_updates: Dict[str, Any]
