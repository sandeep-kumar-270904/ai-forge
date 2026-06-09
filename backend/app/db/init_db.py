import logging
from sqlalchemy.orm import Session
from ..core.security import get_password_hash
from ..models.tenant import Tenant
from ..models.user import User
from ..models.workspace import Workspace

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    tenant = db.query(Tenant).filter(Tenant.name == "Default Tenant").first()
    if not tenant:
        tenant = Tenant(name="Default Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        logger.info("Created Default Tenant")

    user = db.query(User).filter(User.email == "admin@aiforge.com").first()
    if not user:
        user = User(
            email="admin@aiforge.com",
            hashed_password=get_password_hash("admin"),
            role="admin",
            tenant_id=tenant.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created Admin User")

    workspace = db.query(Workspace).filter(Workspace.name == "Default Workspace").first()
    if not workspace:
        workspace = Workspace(
            name="Default Workspace",
            description="Initial Workspace",
            tenant_id=tenant.id
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        logger.info("Created Default Workspace")
