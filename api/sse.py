"""
Server-Sent Events (SSE) module for MCP GLPI Server.
Provides real-time updates for ticket changes and events.
"""

import asyncio
import json
from datetime import datetime
from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional

# Create SSE router
sse_router = APIRouter()

# Store active connections
active_connections = {}

# Store ticket events
ticket_events = []

# Store ticket watchers by user
ticket_watchers = {}

async def send_event(user_id: str, event_type: str, data: Dict[str, Any]):
    """
    Send event to a specific user connection.
    
    Args:
        user_id: User identifier
        event_type: Type of event (ticket_update, category_change, etc)
        data: Event data
    """
    if user_id in active_connections:
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await active_connections[user_id].put(event)

async def send_ticket_event(ticket_id: int, event_type: str, data: Dict[str, Any]):
    """
    Send event to all users watching a specific ticket.
    
    Args:
        ticket_id: Ticket ID
        event_type: Type of event
        data: Event data
    """
    # Store event for history
    ticket_events.append({
        "ticket_id": ticket_id,
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })
    
    # Send to all watchers of this ticket
    watchers = [
        user_id for user_id, tickets in ticket_watchers.items() 
        if ticket_id in tickets
    ]
    
    for user_id in watchers:
        await send_event(user_id, event_type, data)

@sse_router.get("/stream")
async def stream(user_id: str):
    """
    SSE endpoint for streaming events.
    
    Args:
        user_id: User identifier
        
    Returns:
        EventSourceResponse: SSE response
    """
    if user_id in active_connections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection already exists for this user"
        )
    
    # Create queue for this connection
    queue = asyncio.Queue()
    active_connections[user_id] = queue
    
    # Function to listen for events
    async def event_generator():
        try:
            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "message": "Connected to MCP GLPI event stream",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                })
            }
            
            # Listen for events
            while True:
                event = await queue.get()
                yield {
                    "event": event["type"],
                    "data": json.dumps(event["data"])
                }
                
        except asyncio.CancelledError:
            # Remove connection when client disconnects
            if user_id in active_connections:
                del active_connections[user_id]
                # Clear ticket watchers for this user
                if user_id in ticket_watchers:
                    del ticket_watchers[user_id]
    
    return EventSourceResponse(event_generator())

@sse_router.post("/watch/{ticket_id}")
async def watch_ticket(ticket_id: int, user_id: str):
    """
    Add a ticket to user's watch list.
    
    Args:
        ticket_id: Ticket ID
        user_id: User identifier
        
    Returns:
        Dict: Status message
    """
    if user_id not in ticket_watchers:
        ticket_watchers[user_id] = set()
    
    ticket_watchers[user_id].add(ticket_id)
    
    return {
        "status": "success",
        "message": f"Now watching ticket {ticket_id}",
        "ticket_id": ticket_id
    }

@sse_router.delete("/watch/{ticket_id}")
async def unwatch_ticket(ticket_id: int, user_id: str):
    """
    Remove a ticket from user's watch list.
    
    Args:
        ticket_id: Ticket ID
        user_id: User identifier
        
    Returns:
        Dict: Status message
    """
    if user_id in ticket_watchers and ticket_id in ticket_watchers[user_id]:
        ticket_watchers[user_id].remove(ticket_id)
        
        return {
            "status": "success",
            "message": f"No longer watching ticket {ticket_id}",
            "ticket_id": ticket_id
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ticket {ticket_id} not found in watch list"
    ) 