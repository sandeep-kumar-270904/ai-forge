from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, ValidationError
from jose import jwt

from ..core import security
from ..core.config import settings
from .deps import get_db
from ..models.user import User
from ..schemas.token import Token
from ..schemas.user import UserCreate, User as UserSchema
from ..crud import user as crud_user
from ..crud import tenant as crud_tenant
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
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    tenant_id = user_in.tenant_id
    if not tenant_id:
        default_tenant = await crud_tenant.get_by_name(db, name="Default Tenant")
        if not default_tenant:
            raise HTTPException(status_code=500, detail="Default tenant not found.")
        tenant_id = default_tenant.id

    user = await crud_user.create(db, obj_in=UserCreate(email=user_in.email, password=user_in.password, tenant_id=tenant_id))
    return user

@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud_user.get_by_email(db, email=form_data.username)
    if user is None or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=7)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        ),
        "token_type": "bearer",
    }

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> Any:
    try:
        payload = jwt.decode(
            request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
        token_type = payload.get("type")
        
        if token_data is None or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
            
        user = await crud_user.get(db, id=token_data)
        
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=7)
        
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "refresh_token": security.create_refresh_token(
                user.id, expires_delta=refresh_token_expires
            ),
            "token_type": "bearer",
        }
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
