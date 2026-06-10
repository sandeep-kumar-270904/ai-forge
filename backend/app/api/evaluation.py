from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .deps import get_db, get_current_active_user
from ..models.user import User
from ..schemas.evaluation import DatasetCreate, DatasetResponse, EvaluationRunCreate, EvaluationRunResponse
from ..crud.crud_evaluation import dataset, evaluation_run
from ..ai.evaluation.worker import EvaluationWorker

router = APIRouter()

@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    obj_in: DatasetCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await dataset.create_with_rows(db, obj_in=obj_in, tenant_id=current_user.tenant_id)

@router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await dataset.get_by_tenant(db, tenant_id=current_user.tenant_id)

@router.post("/runs", response_model=EvaluationRunResponse)
async def start_evaluation_run(
    obj_in: EvaluationRunCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    ds = await dataset.get(db, id=obj_in.dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    run = await evaluation_run.create(db, obj_in=obj_in)
    
    background_tasks.add_task(EvaluationWorker.run_evaluation_batch, db, run.id)
    
    return run

@router.get("/runs/{run_id}", response_model=EvaluationRunResponse)
async def get_evaluation_run(
    run_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    run = await evaluation_run.get_with_results(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
