from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(str, Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    EMAIL = "email"
    ACCOUNT = "account"
    OTHER = "other"


class TicketBase(BaseModel):
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class Ticket(TicketBase):
    id: str
    status: TicketStatus
    created_by: str
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    attachments: List[str] = []

    class Config:
        from_attributes = True


class TicketComment(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    comment: str
    is_internal: bool = False
    created_at: datetime


class TicketHistory(BaseModel):
    id: str
    ticket_id: str
    changed_by: str
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime

