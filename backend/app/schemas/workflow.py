from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class WorkflowNodeBase(BaseModel):
    id: str
    node_type: str
    config: Optional[Dict[str, Any]] = None

class WorkflowEdgeBase(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    condition_type: Optional[str] = "always"
    condition_config: Optional[Dict[str, Any]] = None

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNodeBase]
    edges: List[WorkflowEdgeBase]

class WorkflowNodeRead(WorkflowNodeBase):
    workflow_id: UUID
    model_config = ConfigDict(from_attributes=True)

class WorkflowEdgeRead(WorkflowEdgeBase):
    workflow_id: UUID
    model_config = ConfigDict(from_attributes=True)

class WorkflowRead(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    nodes: List[WorkflowNodeRead]
    edges: List[WorkflowEdgeRead]
    
    model_config = ConfigDict(from_attributes=True)

class WorkflowInvokeRequest(BaseModel):
    input_state: Dict[str, Any]
    thread_id: Optional[str] = None
