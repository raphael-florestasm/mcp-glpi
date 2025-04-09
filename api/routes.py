"""
API routes module.
Defines the REST API endpoints for the MCP server.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import os
import platform
from datetime import datetime

from src.auth.session import GLPISession
from src.glpi.client import GLPIClient
from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager
from src.agent.decision import MCPDecisionMaker
from src.agent.thinking import MCPThinker
from src.agent.searching import MCPSearcher
from api.sse import sse_router, send_ticket_event

# Create router
router = APIRouter()

# Include SSE routes
router.include_router(sse_router, prefix="/sse", tags=["sse"])

# Initialize services
session = GLPISession()
client = GLPIClient(session)
ticket_manager = GLPITicketManager(client)
category_manager = GLPICategoryManager(client)
decision_maker = MCPDecisionMaker(ticket_manager, category_manager)
thinker = MCPThinker(ticket_manager, category_manager)
searcher = MCPSearcher(ticket_manager, category_manager)

# Request/Response Models
class TicketCreate(BaseModel):
    """Model for ticket creation request."""
    name: str
    content: str
    itilcategories_id: int
    type: int = 1
    urgency: int = 3
    impact: int = 3
    priority: int = 3
    entities_id: Optional[int] = None
    requesttypes_id: Optional[int] = None

class TicketUpdate(BaseModel):
    """Model for ticket update request."""
    name: Optional[str] = None
    content: Optional[str] = None
    itilcategories_id: Optional[int] = None
    type: Optional[int] = None
    urgency: Optional[int] = None
    impact: Optional[int] = None
    priority: Optional[int] = None
    status: Optional[int] = None

class FollowupCreate(BaseModel):
    """Model for follow-up creation request."""
    content: str
    is_private: bool = False

class SolutionCreate(BaseModel):
    """Model for solution creation request."""
    content: str
    status: int = 5

class SearchRequest(BaseModel):
    """Model for search request."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10

# Ticket Routes
@router.post("/tickets", response_model=Dict[str, Any])
async def create_ticket(ticket: TicketCreate):
    """Create a new ticket."""
    try:
        result = ticket_manager.create_ticket(**ticket.dict())
        
        # Send SSE event
        await send_ticket_event(
            ticket_id=result["id"],
            event_type="ticket_created",
            data=result
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/tickets/{ticket_id}", response_model=Dict[str, Any])
async def get_ticket(ticket_id: int):
    """Get ticket details."""
    try:
        result = ticket_manager.get_ticket(ticket_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/tickets/{ticket_id}", response_model=Dict[str, Any])
async def update_ticket(ticket_id: int, ticket: TicketUpdate):
    """Update a ticket."""
    try:
        result = ticket_manager.update_ticket(ticket_id, **ticket.dict(exclude_unset=True))
        
        # Send SSE event
        await send_ticket_event(
            ticket_id=ticket_id,
            event_type="ticket_updated",
            data=result
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/tickets/{ticket_id}/followups", response_model=Dict[str, Any])
async def add_followup(ticket_id: int, followup: FollowupCreate):
    """Add a follow-up to a ticket."""
    try:
        result = ticket_manager.add_followup(ticket_id, **followup.dict())
        
        # Send SSE event
        await send_ticket_event(
            ticket_id=ticket_id,
            event_type="followup_added",
            data=result
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/tickets/{ticket_id}/solutions", response_model=Dict[str, Any])
async def add_solution(ticket_id: int, solution: SolutionCreate):
    """Add a solution to a ticket."""
    try:
        result = ticket_manager.add_solution(ticket_id, **solution.dict())
        
        # Send SSE event
        await send_ticket_event(
            ticket_id=ticket_id,
            event_type="solution_added",
            data=result
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Category Routes
@router.get("/categories", response_model=Dict[str, Any])
async def get_categories():
    """Get all categories."""
    try:
        result = category_manager.get_categories()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/categories/{category_id}", response_model=Dict[str, Any])
async def get_category(category_id: int):
    """Get category details."""
    try:
        result = category_manager.get_category(category_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Search Routes
@router.post("/search/tickets", response_model=Dict[str, Any])
async def search_tickets(request: SearchRequest):
    """Search for tickets."""
    try:
        result = searcher.search_tickets(
            request.query,
            request.filters,
            request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/search/tickets/{ticket_id}/similar", response_model=Dict[str, Any])
async def search_similar_tickets(ticket_id: int, limit: int = 5):
    """Search for similar tickets."""
    try:
        result = searcher.search_similar_tickets(ticket_id, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/search/solutions", response_model=Dict[str, Any])
async def search_solutions(query: str, category_id: Optional[int] = None, limit: int = 5):
    """Search for solutions."""
    try:
        result = searcher.search_solutions(query, category_id, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Agent Routes
@router.post("/agent/analyze", response_model=Dict[str, Any])
async def analyze_demand(content: str, title: str):
    """Analyze demand content."""
    try:
        result = thinker.analyze_content(content, title)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/agent/suggest-category", response_model=Dict[str, Any])
async def suggest_category(content: str, title: str):
    """Suggest category for demand."""
    try:
        result = thinker.suggest_category(content, title)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/agent/evaluate-priority", response_model=Dict[str, int])
async def evaluate_priority(content: str, title: str):
    """Evaluate demand priority."""
    try:
        result = thinker.evaluate_priority(content, title)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/agent/determine-action", response_model=Dict[str, Any])
async def determine_action(ticket_id: Optional[int], content: str, title: str):
    """Determine action for demand."""
    try:
        result = decision_maker.determine_action(ticket_id, content, title)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/agent/execute-action", response_model=Dict[str, Any])
async def execute_action(action: Dict[str, Any]):
    """Execute determined action."""
    try:
        result = decision_maker.execute_action(action)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Health and Monitoring Routes
@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Check system health."""
    try:
        # Verificar conexão com GLPI (simulação)
        # Em produção, seria uma verificação real
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "MCP GLPI Server"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível"
        )

@router.get("/version", response_model=Dict[str, Any])
async def get_version():
    """Get system version info."""
    return {
        "version": "1.0.0",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "hostname": platform.node()
    } 