from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class DocumentRead(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    file_type: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    metadata_filter: Optional[dict[str, Any]] = None

class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    content: str
    metadata: Optional[dict[str, Any]]
    similarity_score: float
