from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class DatasetRowBase(BaseModel):
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]] = None

class DatasetRowCreate(DatasetRowBase):
    pass

class DatasetRowResponse(DatasetRowBase):
    id: str
    dataset_id: str
    
    class Config:
        from_attributes = True

class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    rows: List[DatasetRowCreate] = []

class DatasetResponse(DatasetBase):
    id: str
    tenant_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class EvaluationRunBase(BaseModel):
    dataset_id: str
    target_prompt_id: Optional[str] = None

class EvaluationRunCreate(EvaluationRunBase):
    pass

class EvaluationRunResponse(EvaluationRunBase):
    id: str
    status: str
    overall_score: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EvaluationResultResponse(BaseModel):
    id: str
    run_id: str
    row_id: str
    actual_output: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    reasoning: Optional[str] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    
    class Config:
        from_attributes = True
