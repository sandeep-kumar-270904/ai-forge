from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PromptVariableSchema(BaseModel):
    name: str
    type: str = "string"
    description: Optional[str] = None
    required: bool = True

class PromptVersionBase(BaseModel):
    content: str
    variables: List[PromptVariableSchema] = []

class PromptVersionCreate(PromptVersionBase):
    pass

class PromptVersionResponse(PromptVersionBase):
    id: str
    prompt_id: str
    version_number: int
    status: str
    author_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PromptBase(BaseModel):
    name: str
    description: Optional[str] = None

class PromptCreate(PromptBase):
    initial_content: str
    variables: List[PromptVariableSchema] = []

class PromptResponse(PromptBase):
    id: str
    tenant_id: str
    created_at: datetime
    versions: Optional[List[PromptVersionResponse]] = None
    
    class Config:
        from_attributes = True

class PromptDeploymentResponse(BaseModel):
    id: str
    prompt_id: str
    version_id: str
    environment: str
    deployed_by: str
    deployed_at: datetime
    
    class Config:
        from_attributes = True

class PromptExecuteRequest(BaseModel):
    environment: str = "production"
    variables: Dict[str, Any] = {}
