from fastapi import APIRouter, Depends

from app.core.security import get_current_active_user
from app.database import get_db
from app.models.ticket import TicketStatus
from app.models.user import UserRole

router = APIRouter()


@router.get("/stats")
async def stats(current_user: dict = Depends(get_current_active_user)):
  """Basic ticket statistics for the current user."""
  db = get_db()

  query: dict = {}
  if current_user["role"] == UserRole.END_USER.value:
    query["created_by"] = current_user["id"]
  elif current_user["role"] == UserRole.SUPPORT_STAFF.value:
    query["assigned_to"] = current_user["id"]

  return {
    "total": await db.tickets.count_documents(query),
    "open": await db.tickets.count_documents({**query, "status": TicketStatus.OPEN.value}),
    "in_progress": await db.tickets.count_documents({**query, "status": TicketStatus.IN_PROGRESS.value}),
    "resolved": await db.tickets.count_documents({**query, "status": TicketStatus.RESOLVED.value}),
    "closed": await db.tickets.count_documents({**query, "status": TicketStatus.CLOSED.value}),
  }

