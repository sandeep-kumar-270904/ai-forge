from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from .base import CRUDBase
from ..core.security import get_password_hash

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            tenant_id=obj_in.tenant_id,
            role="user"
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

user = CRUDUser(User)
