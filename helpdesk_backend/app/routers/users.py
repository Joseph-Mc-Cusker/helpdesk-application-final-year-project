from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user, require_role
from app.database import get_db
from app.models.user import User, UserRole, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[User])
async def list_users(current_user: dict = Depends(require_role([UserRole.ADMINISTRATOR]))):
  db = get_db()
  cursor = db.users.find({})
  docs = await cursor.to_list(length=200)
  users = []
  for u in docs:
    u["id"] = str(u["_id"])
    u.pop("_id", None)
    u.pop("hashed_password", None)
    users.append(u)
  return users


@router.get("/support-staff", response_model=List[User])
async def list_support_staff(current_user: dict = Depends(get_current_active_user)):
  db = get_db()
  cursor = db.users.find(
    {
      "role": {"$in": [UserRole.SUPPORT_STAFF.value, UserRole.ADMINISTRATOR.value]},
      "is_active": True,
    },
  )
  docs = await cursor.to_list(length=200)
  users = []
  for u in docs:
    u["id"] = str(u["_id"])
    u.pop("_id", None)
    u.pop("hashed_password", None)
    users.append(u)
  return users


@router.patch("/{user_id}", response_model=User)
async def update_user(
  user_id: str,
  user_update: UserUpdate,
  current_user: dict = Depends(require_role([UserRole.ADMINISTRATOR])),
):
  db = get_db()
  if not ObjectId.is_valid(user_id):
    raise HTTPException(status_code=404, detail="User not found")

  existing = await db.users.find_one({"_id": ObjectId(user_id)})
  if not existing:
    raise HTTPException(status_code=404, detail="User not found")

  updates = user_update.dict(exclude_unset=True)
  updates["updated_at"] = datetime.utcnow()
  await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})

  updated = await db.users.find_one({"_id": ObjectId(user_id)})
  updated["id"] = str(updated["_id"])
  updated.pop("_id", None)
  updated.pop("hashed_password", None)
  return updated

