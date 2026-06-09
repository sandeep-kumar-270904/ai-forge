from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.tenant import Tenant
from .base import CRUDBase
from pydantic import BaseModel

class TenantCreate(BaseModel):
    name: str

class CRUDTenant(CRUDBase[Tenant, TenantCreate, BaseModel]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Tenant]:
        result = await db.execute(select(Tenant).filter(Tenant.name == name))
        return result.scalars().first()

tenant = CRUDTenant(Tenant)
