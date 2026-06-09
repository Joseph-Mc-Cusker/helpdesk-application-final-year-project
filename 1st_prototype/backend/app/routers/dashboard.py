from fastapi import APIRouter, Depends
from typing import Dict
from app.core.security import get_current_active_user, require_role
from app.models.user import UserRole
from app.database import get_database
from app.models.ticket import TicketStatus

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_active_user)
):
    """Get dashboard statistics"""
    db = get_database()
    
    # Build query based on user role
    query = {}
    if current_user["role"] == UserRole.END_USER.value:
        query["created_by"] = current_user["id"]
    elif current_user["role"] == UserRole.SUPPORT_STAFF.value:
        query["assigned_to"] = current_user["id"]
    
    # Count tickets by status
    stats = {
        "total": await db.tickets.count_documents(query),
        "open": await db.tickets.count_documents({**query, "status": TicketStatus.OPEN.value}),
        "in_progress": await db.tickets.count_documents({**query, "status": TicketStatus.IN_PROGRESS.value}),
        "resolved": await db.tickets.count_documents({**query, "status": TicketStatus.RESOLVED.value}),
        "closed": await db.tickets.count_documents({**query, "status": TicketStatus.CLOSED.value}),
    }
    
    return stats


@router.get("/kanban")
async def get_kanban_tickets(
    current_user: dict = Depends(require_role([UserRole.SUPPORT_STAFF, UserRole.ADMINISTRATOR]))
):
    """Get tickets organized for Kanban view"""
    db = get_database()
    
    query = {}
    if current_user["role"] == UserRole.SUPPORT_STAFF.value:
        query["assigned_to"] = current_user["id"]
    
    kanban_data = {
        "open": [],
        "in_progress": [],
        "resolved": [],
        "closed": []
    }
    
    for status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED]:
        cursor = db.tickets.find({**query, "status": status.value}).sort("created_at", -1)
        tickets = await cursor.to_list(length=50)
        status_key = status.value.replace("_", "")
        kanban_data[status_key] = [
            {
                **ticket,
                "id": str(ticket["_id"])
            }
            for ticket in tickets
        ]
    
    return kanban_data

