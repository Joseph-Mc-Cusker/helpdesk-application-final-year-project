from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (
  ACCESS_TOKEN_EXPIRE_MINUTES,
  create_access_token,
  get_current_active_user,
  get_password_hash,
  verify_password,
)
from app.database import get_db
from app.models.user import Token, User, UserCreate

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
  """Register a new user."""
  db = get_db()
  existing = await db.users.find_one({"email": user_in.email})
  if existing:
    raise HTTPException(status_code=400, detail="Email already registered")

  now = datetime.utcnow()
  doc = {
    "email": user_in.email,
    "full_name": user_in.full_name,
    "role": user_in.role.value,
    "hashed_password": get_password_hash(user_in.password),
    "is_active": True,
    "created_at": now,
    "updated_at": now,
  }
  result = await db.users.insert_one(doc)
  doc["id"] = str(result.inserted_id)
  doc.pop("hashed_password", None)
  return doc


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  """Issue JWT for valid credentials."""
  db = get_db()
  user = await db.users.find_one({"email": form_data.username})
  if not user or not verify_password(form_data.password, user.get("hashed_password", "")):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect email or password",
    )
  if not user.get("is_active", True):
    raise HTTPException(status_code=400, detail="Inactive user")

  expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  token = create_access_token(data={"sub": user["email"]}, expires_delta=expires)
  return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_me(current_user: dict = Depends(get_current_active_user)):
  """Return current logged-in user."""
  current_user.pop("hashed_password", None)
  return current_user

