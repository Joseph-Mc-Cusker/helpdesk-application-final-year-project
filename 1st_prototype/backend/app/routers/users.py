from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import User, UserUpdate, UserRole
from app.core.security import get_current_active_user, require_role
from app.database import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    current_user: dict = Depends(require_role([UserRole.ADMINISTRATOR]))
):
    """Get all users (admin only)"""
    db = get_database()
    cursor = db.users.find({})
    users = await cursor.to_list(length=100)
    
    result = []
    for user in users:
        user_dict = {
            **user,
            "id": str(user["_id"])
        }
        user_dict.pop("hashed_password", None)  # Remove password from response
        result.append(user_dict)
    return result


@router.get("/support-staff", response_model=List[User])
async def get_support_staff(
    current_user: dict = Depends(get_current_active_user)
):
    """Get all support staff and administrators"""
    db = get_database()
    cursor = db.users.find({
        "role": {"$in": [UserRole.SUPPORT_STAFF.value, UserRole.ADMINISTRATOR.value]},
        "is_active": True
    })
    staff = await cursor.to_list(length=100)
    
    result = []
    for user in staff:
        user_dict = {
            **user,
            "id": str(user["_id"])
        }
        user_dict.pop("hashed_password", None)  # Remove password from response
        result.append(user_dict)
    return result


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(require_role([UserRole.ADMINISTRATOR]))
):
    """Update a user (admin only)"""
    db = get_database()
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_dict = user_update.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_dict}
    )
    
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user["_id"])
    updated_user.pop("hashed_password", None)
    
    return updated_user

