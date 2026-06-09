"""In-app notifications for users (e.g. when their ticket is resolved)."""
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_active_user
from app.database import get_db

router = APIRouter()


def _notification_from_doc(doc: dict) -> dict:
    out = dict(doc)
    out["id"] = str(doc["_id"])
    out.pop("_id", None)
    return out


@router.get("", response_model=List[dict])
async def list_my_notifications(current_user: dict = Depends(get_current_active_user)):
    """Return notifications for the current user (newest first)."""
    db = get_db()
    cursor = db.notifications.find({"user_id": current_user["id"]}).sort("created_at", -1)
    docs = await cursor.to_list(length=50)
    return [_notification_from_doc(d) for d in docs]


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    """Mark a notification as read. Only the owner can mark it."""
    db = get_db()
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")
    result = await db.notifications.update_one(
        {"_id": ObjectId(notification_id), "user_id": current_user["id"]},
        {"$set": {"read": True}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"ok": True}
