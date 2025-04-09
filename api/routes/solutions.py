"""
Solution management routes.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/solutions", tags=["solutions"])

# Models
class SolutionBase(BaseModel):
    content: str
    ticket_id: int
    status: Optional[str] = "pending"

class SolutionCreate(SolutionBase):
    pass

class SolutionUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None

class SolutionResponse(SolutionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[SolutionResponse], summary="List Solutions")
async def get_solutions(ticket_id: Optional[int] = None, status: Optional[str] = None):
    """
    Retrieve a list of solutions with optional filtering.
    
    Parameters:
        ticket_id: Filter solutions by ticket ID
        status: Filter solutions by status
        
    Returns:
        List of solutions matching the query parameters
    """
    # This is a sample implementation
    # In a real implementation, this would query the GLPI API
    solutions = [
        {
            "id": 1,
            "content": "Restart the computer and try again",
            "ticket_id": 1,
            "status": "approved",
            "created_at": datetime.now(),
            "updated_at": None
        },
        {
            "id": 2,
            "content": "Install the latest drivers from the manufacturer's website",
            "ticket_id": 2,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": None
        }
    ]
    
    result = solutions
    if ticket_id is not None:
        result = [sol for sol in result if sol["ticket_id"] == ticket_id]
    if status is not None:
        result = [sol for sol in result if sol["status"] == status]
        
    return result

@router.post("/", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED, summary="Create Solution")
async def create_solution(solution: SolutionCreate):
    """
    Create a new solution for a ticket in GLPI.
    
    Parameters:
        solution: Solution information
        
    Returns:
        Created solution information
    """
    # This is a sample implementation
    # In a real implementation, this would create a solution in GLPI
    return {
        "id": 3,
        "content": solution.content,
        "ticket_id": solution.ticket_id,
        "status": solution.status,
        "created_at": datetime.now(),
        "updated_at": None
    }

@router.get("/{solution_id}", response_model=SolutionResponse, summary="Get Solution")
async def get_solution(solution_id: int):
    """
    Retrieve a specific solution by ID.
    
    Parameters:
        solution_id: ID of the solution to retrieve
        
    Returns:
        Solution information
    """
    # This is a sample implementation
    # In a real implementation, this would get a solution from GLPI
    solutions = {
        1: {
            "id": 1,
            "content": "Restart the computer and try again",
            "ticket_id": 1,
            "status": "approved",
            "created_at": datetime.now(),
            "updated_at": None
        },
        2: {
            "id": 2,
            "content": "Install the latest drivers from the manufacturer's website",
            "ticket_id": 2,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": None
        }
    }
    
    if solution_id not in solutions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution with ID {solution_id} not found"
        )
        
    return solutions[solution_id]

@router.put("/{solution_id}", response_model=SolutionResponse, summary="Update Solution")
async def update_solution(solution_id: int, solution: SolutionUpdate):
    """
    Update an existing solution.
    
    Parameters:
        solution_id: ID of the solution to update
        solution: Updated solution information
        
    Returns:
        Updated solution information
    """
    # This is a sample implementation
    # In a real implementation, this would update a solution in GLPI
    solutions = {
        1: {
            "id": 1,
            "content": "Restart the computer and try again",
            "ticket_id": 1,
            "status": "approved",
            "created_at": datetime.now(),
            "updated_at": None
        },
        2: {
            "id": 2,
            "content": "Install the latest drivers from the manufacturer's website",
            "ticket_id": 2,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": None
        }
    }
    
    if solution_id not in solutions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution with ID {solution_id} not found"
        )
    
    existing = solutions[solution_id]
    updated = {
        "id": solution_id,
        "content": solution.content if solution.content is not None else existing["content"],
        "ticket_id": existing["ticket_id"],
        "status": solution.status if solution.status is not None else existing["status"],
        "created_at": existing["created_at"],
        "updated_at": datetime.now()
    }
        
    return updated 