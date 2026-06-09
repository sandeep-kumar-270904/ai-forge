from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.workspace import Workspace
from .base import CRUDBase
from pydantic import BaseModel

class WorkspaceCreate(BaseModel):
    name: str
    tenant_id: str

class CRUDWorkspace(CRUDBase[Workspace, WorkspaceCreate, BaseModel]):
    async def get_by_id_and_tenant(
        self, db: AsyncSession, *, workspace_id: str, tenant_id: str
    ) -> Optional[Workspace]:
        result = await db.execute(
            select(Workspace).filter(Workspace.id == workspace_id, Workspace.tenant_id == tenant_id)
        )
        return result.scalars().first()

workspace = CRUDWorkspace(Workspace)
