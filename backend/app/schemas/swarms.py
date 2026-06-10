from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SwarmAgentPersonaBase(BaseModel):
    name: str
    role_description: str
    system_prompt_id: Optional[str] = None
    tools: Optional[List[str]] = []

class SwarmAgentPersonaCreate(SwarmAgentPersonaBase):
    pass

class SwarmAgentPersonaResponse(SwarmAgentPersonaBase):
    id: str
    tenant_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SwarmBase(BaseModel):
    name: str
    description: Optional[str] = None
    supervisor_prompt_id: Optional[str] = None
    max_loops: int = 15

class SwarmCreate(SwarmBase):
    agent_ids: List[str] = []

class SwarmResponse(SwarmBase):
    id: str
    tenant_id: str
    created_at: datetime
    agents: List[SwarmAgentPersonaResponse] = []
    
    class Config:
        from_attributes = True
        
class SwarmInvokeRequest(BaseModel):
    input_message: str
