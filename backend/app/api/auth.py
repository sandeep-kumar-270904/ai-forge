from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core import security
from ..core.config import settings
from .deps import get_db
from ..models.user import User
from ..schemas.token import Token
from ..schemas.user import UserCreate, User as UserSchema
from fastapi_limiter.depends import RateLimiter

router = APIRouter()

@router.post("/register", response_model=UserSchema, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def register_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    tenant_id = user_in.tenant_id
    if not tenant_id:
        from ..models.tenant import Tenant
        tenant_result = await db.execute(select(Tenant).filter(Tenant.name == "Default Tenant"))
        default_tenant = tenant_result.scalars().first()
        if not default_tenant:
            raise HTTPException(status_code=500, detail="Default tenant not found.")
        tenant_id = default_tenant.id

    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        tenant_id=tenant_id,
        role="user"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    if user is None or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
