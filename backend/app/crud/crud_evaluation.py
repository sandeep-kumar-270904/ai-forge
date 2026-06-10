from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models.evaluation import Dataset, DatasetRow, EvaluationRun, EvaluationResult
from ..schemas.evaluation import DatasetCreate, EvaluationRunCreate
from .base import CRUDBase

class CRUDDataset(CRUDBase[Dataset, DatasetCreate, DatasetCreate]):
    async def create_with_rows(self, db: AsyncSession, *, obj_in: DatasetCreate, tenant_id: str) -> Dataset:
        db_obj = Dataset(
            tenant_id=tenant_id,
            name=obj_in.name,
            description=obj_in.description
        )
        db.add(db_obj)
        await db.flush()
        
        for r in obj_in.rows:
            db_row = DatasetRow(
                dataset_id=db_obj.id,
                input_data=r.input_data,
                expected_output=r.expected_output
            )
            db.add(db_row)
            
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
        
    async def get_by_tenant(self, db: AsyncSession, *, tenant_id: str) -> List[Dataset]:
        result = await db.execute(
            select(Dataset)
            .filter(Dataset.tenant_id == tenant_id)
            .order_by(Dataset.created_at.desc())
        )
        return list(result.scalars().all())

class CRUDEvaluationRun(CRUDBase[EvaluationRun, EvaluationRunCreate, EvaluationRunCreate]):
    async def get_with_results(self, db: AsyncSession, *, id: str) -> Optional[EvaluationRun]:
        result = await db.execute(
            select(EvaluationRun)
            .filter(EvaluationRun.id == id)
            .options(selectinload(EvaluationRun.results))
        )
        return result.scalars().first()

dataset = CRUDDataset(Dataset)
dataset_row = CRUDBase[DatasetRow, DatasetRow, DatasetRow](DatasetRow)
evaluation_run = CRUDEvaluationRun(EvaluationRun)
evaluation_result = CRUDBase[EvaluationResult, EvaluationResult, EvaluationResult](EvaluationResult)
