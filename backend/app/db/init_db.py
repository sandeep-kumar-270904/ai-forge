import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..core.security import get_password_hash
from ..models.tenant import Tenant
from ..models.user import User
from ..models.workspace import Workspace

logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession) -> None:
    result = await db.execute(select(Tenant).filter(Tenant.name == "Default Tenant"))
    tenant = result.scalars().first()
    if not tenant:
        tenant = Tenant(name="Default Tenant")
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        logger.info("Created Default Tenant")

    result = await db.execute(select(User).filter(User.email == "admin@aiforge.com"))
    user = result.scalars().first()
    if not user:
        user = User(
            email="admin@aiforge.com",
            hashed_password=get_password_hash("admin"),
            role="admin",
            tenant_id=tenant.id
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("Created Admin User")

    result = await db.execute(select(Workspace).filter(Workspace.name == "Default Workspace"))
    workspace = result.scalars().first()
    if not workspace:
        workspace = Workspace(
            name="Default Workspace",
            description="Initial Workspace",
            tenant_id=tenant.id
        )
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)
        logger.info("Created Default Workspace")
