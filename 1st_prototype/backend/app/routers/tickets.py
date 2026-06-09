from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.ticket import TicketCreate, TicketUpdate, Ticket, TicketStatus, TicketHistory
from app.core.security import get_current_active_user, require_role
from app.core.email import (
    send_ticket_created_email,
    send_ticket_assigned_email,
    send_ticket_status_update_email
)
from app.database import get_database
from bson import ObjectId
from datetime import datetime
from app.models.user import UserRole

router = APIRouter()


def ticket_from_dict(ticket_dict: dict) -> dict:
    """Convert MongoDB document to ticket dict"""
    ticket_dict["id"] = str(ticket_dict["_id"])
    ticket_dict.pop("_id", None)
    return ticket_dict


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new ticket"""
    db = get_database()
    
    ticket_dict = {
        **ticket_data.dict(),
        "status": TicketStatus.OPEN.value,
        "created_by": current_user["id"],
        "assigned_to": None,
        "resolution_notes": None,
        "attachments": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.tickets.insert_one(ticket_dict)
    ticket_dict["id"] = str(result.inserted_id)
    
    # Create audit log entry
    await db.ticket_history.insert_one({
        "ticket_id": ticket_dict["id"],
        "changed_by": current_user["id"],
        "field_changed": "status",
        "old_value": None,
        "new_value": TicketStatus.OPEN.value,
        "created_at": datetime.utcnow()
    })
    
    # Send email notification to user
    await send_ticket_created_email(
        current_user["email"],
        current_user["full_name"],
        ticket_dict["id"],
        ticket_dict["title"]
    )
    
    # Find support staff to notify (first available or admin)
    support_staff = await db.users.find_one({
        "role": {"$in": [UserRole.SUPPORT_STAFF.value, UserRole.ADMINISTRATOR.value]},
        "is_active": True
    })
    
    if support_staff:
        await send_ticket_assigned_email(
            support_staff["email"],
            support_staff["full_name"],
            ticket_dict["id"],
            ticket_dict["title"],
            current_user["full_name"]
        )
    
    return ticket_dict


@router.get("/", response_model=List[Ticket])
async def get_tickets(
    status_filter: Optional[TicketStatus] = None,
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get tickets with optional filters"""
    db = get_database()
    query = {}
    
    # End users can only see their own tickets
    if current_user["role"] == UserRole.END_USER.value:
        query["created_by"] = current_user["id"]
    elif assigned_to:
        query["assigned_to"] = assigned_to
    elif created_by:
        query["created_by"] = created_by
    
    if status_filter:
        query["status"] = status_filter.value
    
    cursor = db.tickets.find(query).sort("created_at", -1)
    tickets = await cursor.to_list(length=100)
    
    return [ticket_from_dict(ticket) for ticket in tickets]


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific ticket"""
    db = get_database()
    
    if not ObjectId.is_valid(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permissions
    if (current_user["role"] == UserRole.END_USER.value and 
        ticket["created_by"] != current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
    
    return ticket_from_dict(ticket)


@router.patch("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: str,
    ticket_update: TicketUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update a ticket"""
    db = get_database()
    
    if not ObjectId.is_valid(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permissions
    if current_user["role"] == UserRole.END_USER.value:
        raise HTTPException(status_code=403, detail="End users cannot update tickets")
    
    # Track changes for audit log
    update_dict = ticket_update.dict(exclude_unset=True)
    old_status = ticket.get("status")
    
    # Update ticket
    update_dict["updated_at"] = datetime.utcnow()
    await db.tickets.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": update_dict}
    )
    
    # Create audit log entries
    for field, new_value in update_dict.items():
        if field != "updated_at":
            old_value = ticket.get(field)
            if old_value != new_value:
                await db.ticket_history.insert_one({
                    "ticket_id": ticket_id,
                    "changed_by": current_user["id"],
                    "field_changed": field,
                    "old_value": str(old_value) if old_value else None,
                    "new_value": str(new_value) if new_value else None,
                    "created_at": datetime.utcnow()
                })
    
    # Send email notifications
    updated_ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
    
    # Notify user if status changed
    if "status" in update_dict and update_dict["status"] != old_status:
        creator = await db.users.find_one({"_id": ObjectId(updated_ticket["created_by"])})
        if creator:
            await send_ticket_status_update_email(
                creator["email"],
                creator["full_name"],
                ticket_id,
                updated_ticket["title"],
                TicketStatus(update_dict["status"]),
                update_dict.get("resolution_notes")
            )
    
    # Notify assigned staff if ticket was assigned
    if "assigned_to" in update_dict and update_dict["assigned_to"]:
        assigned_user = await db.users.find_one({"_id": ObjectId(update_dict["assigned_to"])})
        if assigned_user:
            creator = await db.users.find_one({"_id": ObjectId(updated_ticket["created_by"])})
            await send_ticket_assigned_email(
                assigned_user["email"],
                assigned_user["full_name"],
                ticket_id,
                updated_ticket["title"],
                creator["full_name"] if creator else "Unknown"
            )
    
    return ticket_from_dict(updated_ticket)


@router.get("/{ticket_id}/history", response_model=List[TicketHistory])
async def get_ticket_history(
    ticket_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get ticket history/audit trail"""
    db = get_database()
    
    if not ObjectId.is_valid(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permissions
    if (current_user["role"] == UserRole.END_USER.value and 
        ticket["created_by"] != current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cursor = db.ticket_history.find({"ticket_id": ticket_id}).sort("created_at", 1)
    history = await cursor.to_list(length=100)
    
    return [
        {
            **item,
            "id": str(item["_id"])
        }
        for item in history
    ]

