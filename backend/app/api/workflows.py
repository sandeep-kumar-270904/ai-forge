from uuid import UUID
from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.workflow import WorkflowCreate, WorkflowRead, WorkflowInvokeRequest
from app.crud.crud_workflow import crud_workflow
from app.ai.workflow_engine import DynamicWorkflowEngine
from fastapi_limiter.depends import RateLimiter

router = APIRouter()

@router.post("/", response_model=WorkflowRead)
async def create_workflow(
    payload: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = await crud_workflow.create_workflow(db, current_user.tenant_id, payload)
    return workflow

@router.get("/", response_model=List[WorkflowRead])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflows = await crud_workflow.get_all_workflows(db, current_user.tenant_id)
    # Note: For full nodes/edges listing, this would need selectinload in the CRUD function
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = await crud_workflow.get_workflow_with_graph(db, workflow_id, current_user.tenant_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.post("/{workflow_id}/invoke", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def invoke_workflow(
    workflow_id: UUID,
    payload: WorkflowInvokeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = await crud_workflow.get_workflow_with_graph(db, workflow_id, current_user.tenant_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    engine = DynamicWorkflowEngine(workflow)
    try:
        result = await engine.invoke(payload.input_state)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
