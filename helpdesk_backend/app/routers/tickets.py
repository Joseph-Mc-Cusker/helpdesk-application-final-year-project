from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.email import send_ticket_created_email, send_ticket_status_email
from app.core.security import get_current_active_user
from app.database import get_db
from app.models.ticket import Ticket, TicketCreate, TicketHistory, TicketStatus, TicketUpdate
from app.models.user import UserRole

router = APIRouter()


def _ticket_from_doc(doc: dict) -> dict:
  doc["id"] = str(doc["_id"])
  doc.pop("_id", None)
  return doc


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket_in: TicketCreate, current_user: dict = Depends(get_current_active_user)):
  db = get_db()
  now = datetime.utcnow()
  doc = {
    **ticket_in.dict(),
    "status": TicketStatus.OPEN.value,
    "created_by": current_user["id"],
    "assigned_to": None,
    "resolution_notes": None,
    "attachments": [],
    "created_at": now,
    "updated_at": now,
  }
  result = await db.tickets.insert_one(doc)
  doc["id"] = str(result.inserted_id)

  await db.ticket_history.insert_one(
    {
      "ticket_id": doc["id"],
      "changed_by": current_user["id"],
      "field_changed": "status",
      "old_value": None,
      "new_value": TicketStatus.OPEN.value,
      "created_at": now,
    },
  )

  await send_ticket_created_email(
    current_user["email"],
    current_user["full_name"],
    doc["id"],
    doc["title"],
  )
  return doc


@router.get("/", response_model=List[Ticket])
async def list_tickets(
  status_filter: Optional[TicketStatus] = None,
  current_user: dict = Depends(get_current_active_user),
):
  db = get_db()
  query: dict = {}

  # End users only see their own tickets
  if current_user["role"] == UserRole.END_USER.value:
    query["created_by"] = current_user["id"]

  if status_filter:
    query["status"] = status_filter.value

  cursor = db.tickets.find(query).sort("created_at", -1)
  docs = await cursor.to_list(length=100)
  return [_ticket_from_doc(d) for d in docs]


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str, current_user: dict = Depends(get_current_active_user)):
  db = get_db()
  if not ObjectId.is_valid(ticket_id):
    raise HTTPException(status_code=404, detail="Ticket not found")

  doc = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
  if not doc:
    raise HTTPException(status_code=404, detail="Ticket not found")

  # End users can't see others' tickets
  if current_user["role"] == UserRole.END_USER.value and doc["created_by"] != current_user["id"]:
    raise HTTPException(status_code=403, detail="Not authorised")

  return _ticket_from_doc(doc)


@router.patch("/{ticket_id}", response_model=Ticket)
async def update_ticket(
  ticket_id: str,
  ticket_update: TicketUpdate,
  current_user: dict = Depends(get_current_active_user),
):
  db = get_db()
  if not ObjectId.is_valid(ticket_id):
    raise HTTPException(status_code=404, detail="Ticket not found")

  doc = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
  if not doc:
    raise HTTPException(status_code=404, detail="Ticket not found")

  # Only administrators can update tickets (e.g. mark complete); end users and support staff cannot
  if current_user["role"] != UserRole.ADMINISTRATOR.value:
    raise HTTPException(status_code=403, detail="Only administrators can update ticket status")

  updates = ticket_update.dict(exclude_unset=True)
  old_status = doc.get("status")
  now = datetime.utcnow()

  updates["updated_at"] = now
  await db.tickets.update_one({"_id": ObjectId(ticket_id)}, {"$set": updates})

  # History
  for field, new_val in updates.items():
    if field == "updated_at":
      continue
    old_val = doc.get(field)
    if old_val != new_val:
      await db.ticket_history.insert_one(
        {
          "ticket_id": ticket_id,
          "changed_by": current_user["id"],
          "field_changed": field,
          "old_value": str(old_val) if old_val is not None else None,
          "new_value": str(new_val) if new_val is not None else None,
          "created_at": now,
        },
      )

  new_doc = await db.tickets.find_one({"_id": ObjectId(ticket_id)})

  # Notify creator on status change (email + in-app notification when resolved)
  if "status" in updates and updates["status"] != old_status:
    creator_id = new_doc.get("created_by")
    if creator_id:
      creator = await db.users.find_one({"_id": ObjectId(creator_id)})
      if creator:
        await send_ticket_status_email(
          creator["email"],
          creator["full_name"],
          ticket_id,
          new_doc["title"],
          TicketStatus(updates["status"]),
          updates.get("resolution_notes"),
        )
      # In-app notification: when resolved, end user sees it after they log in
      if updates["status"] == "resolved":
        await db.notifications.insert_one({
          "user_id": creator_id if isinstance(creator_id, str) else str(creator_id),
          "ticket_id": ticket_id,
          "ticket_title": new_doc["title"],
          "message": "Your ticket has been resolved.",
          "created_at": now,
          "read": False,
        })

  return _ticket_from_doc(new_doc)


@router.get("/{ticket_id}/history", response_model=List[TicketHistory])
async def ticket_history(ticket_id: str, current_user: dict = Depends(get_current_active_user)):
  db = get_db()
  if not ObjectId.is_valid(ticket_id):
    raise HTTPException(status_code=404, detail="Ticket not found")

  ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
  if not ticket:
    raise HTTPException(status_code=404, detail="Ticket not found")

  if current_user["role"] == UserRole.END_USER.value and ticket["created_by"] != current_user["id"]:
    raise HTTPException(status_code=403, detail="Not authorised")

  cursor = db.ticket_history.find({"ticket_id": ticket_id}).sort("created_at", 1)
  docs = await cursor.to_list(length=100)
  for d in docs:
    d["id"] = str(d["_id"])
    d.pop("_id", None)
  return docs

