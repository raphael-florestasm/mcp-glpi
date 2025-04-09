"""
Ticket management routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Models
class TicketBase(BaseModel):
    title: str
    description: str
    category_id: Optional[int] = None
    requester_id: Optional[int] = None
    priority: Optional[int] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[int] = None

class TicketResponse(TicketBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[TicketResponse], summary="List Tickets")
async def get_tickets(
    status: Optional[str] = None, 
    category_id: Optional[int] = None,
    requester_id: Optional[int] = None
):
    """
    Retrieve a list of tickets with optional filtering.
    
    Parameters:
        status: Filter tickets by status
        category_id: Filter tickets by category
        requester_id: Filter tickets by requester
        
    Returns:
        List of tickets matching the query parameters
    """
    # This is a sample implementation
    # In a real implementation, this would query the GLPI API
    return [
        {
            "id": 1,
            "title": "Sample Ticket",
            "description": "This is a sample ticket for demonstration",
            "status": "open",
            "category_id": 1,
            "requester_id": 1,
            "priority": 3,
            "created_at": datetime.now(),
            "updated_at": None
        }
    ]

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED, summary="Create Ticket")
async def create_ticket(ticket: TicketCreate):
    """
    Create a new ticket in GLPI.
    
    Parameters:
        ticket: Ticket information
        
    Returns:
        Created ticket information
    """
    # This is a sample implementation
    # In a real implementation, this would create a ticket in GLPI
    return {
        "id": 2,
        "title": ticket.title,
        "description": ticket.description,
        "status": "new",
        "category_id": ticket.category_id,
        "requester_id": ticket.requester_id,
        "priority": ticket.priority or 3,
        "created_at": datetime.now(),
        "updated_at": None
    }

@router.get("/{ticket_id}", response_model=TicketResponse, summary="Get Ticket")
async def get_ticket(ticket_id: int):
    """
    Retrieve a specific ticket by ID.
    
    Parameters:
        ticket_id: ID of the ticket to retrieve
        
    Returns:
        Ticket information
    """
    # This is a sample implementation
    # In a real implementation, this would get a ticket from GLPI
    if ticket_id != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )
        
    return {
        "id": ticket_id,
        "title": "Sample Ticket",
        "description": "This is a sample ticket for demonstration",
        "status": "open",
        "category_id": 1,
        "requester_id": 1,
        "priority": 3,
        "created_at": datetime.now(),
        "updated_at": None
    }

@router.put("/{ticket_id}", response_model=TicketResponse, summary="Update Ticket")
async def update_ticket(ticket_id: int, ticket: TicketUpdate):
    """
    Update an existing ticket.
    
    Parameters:
        ticket_id: ID of the ticket to update
        ticket: Updated ticket information
        
    Returns:
        Updated ticket information
    """
    # This is a sample implementation
    # In a real implementation, this would update a ticket in GLPI
    if ticket_id != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )
        
    return {
        "id": ticket_id,
        "title": ticket.title or "Sample Ticket",
        "description": ticket.description or "This is a sample ticket for demonstration",
        "status": ticket.status or "open",
        "category_id": ticket.category_id or 1,
        "requester_id": 1,
        "priority": ticket.priority or 3,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    } 