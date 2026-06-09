from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
  END_USER = "end_user"
  SUPPORT_STAFF = "support_staff"
  ADMINISTRATOR = "administrator"


class UserBase(BaseModel):
  email: EmailStr
  full_name: str
  role: UserRole = UserRole.END_USER


class UserCreate(UserBase):
  password: str


class UserUpdate(BaseModel):
  full_name: Optional[str] = None
  role: Optional[UserRole] = None
  is_active: Optional[bool] = None


class User(UserBase):
  id: str
  is_active: bool
  created_at: datetime
  updated_at: datetime


class Token(BaseModel):
  access_token: str
  token_type: str


class TokenData(BaseModel):
  email: Optional[str] = None

