from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .deps import get_db, get_current_active_user
from ..models.user import User
from ..schemas.observability import AgentRunResponse, AgentRunTimelineResponse, AgentSpanTreeNode
from ..crud.crud_observability import agent_run

router = APIRouter()

@router.get("/runs", response_model=List[AgentRunResponse])
async def list_runs(
    x_workspace_id: str = Header(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    runs = await agent_run.get_by_workspace(db, workspace_id=x_workspace_id)
    return runs

@router.get("/runs/{run_id}/timeline", response_model=AgentRunTimelineResponse)
async def get_run_timeline(
    run_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    run = await agent_run.get_with_spans(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    duration = None
    if run.completed_at and run.started_at:
        duration = int((run.completed_at - run.started_at).total_seconds() * 1000)
        
    span_dict = {}
    root_spans = []
    
    for span in run.spans:
        s_node = AgentSpanTreeNode.model_validate(span)
        span_dict[span.id] = s_node
        
    for span in run.spans:
        s_node = span_dict[span.id]
        if span.parent_span_id and span.parent_span_id in span_dict:
            span_dict[span.parent_span_id].children.append(s_node)
        else:
            root_spans.append(s_node)
            
    response = AgentRunTimelineResponse.model_validate(run)
    response.total_duration_ms = duration
    response.spans = root_spans
    
    return response
