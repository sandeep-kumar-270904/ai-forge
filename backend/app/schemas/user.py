from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    role: str = "user"
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    tenant_id: str | None = None

class UserUpdate(UserBase):
    password: str | None = None

class UserInDBBase(UserBase):
    id: str
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class User(UserInDBBase):
    pass
