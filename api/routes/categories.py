"""
Category management routes.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["categories"])

# Models
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

# Routes
@router.get("/", response_model=List[CategoryResponse], summary="List Categories")
async def get_categories(parent_id: Optional[int] = None):
    """
    Retrieve a list of ticket categories with optional filtering.
    
    Parameters:
        parent_id: Filter categories by parent category
        
    Returns:
        List of categories matching the query parameters
    """
    # This is a sample implementation
    # In a real implementation, this would query the GLPI API
    categories = [
        {
            "id": 1,
            "name": "Hardware",
            "description": "Hardware related issues",
            "parent_id": None
        },
        {
            "id": 2,
            "name": "Software",
            "description": "Software related issues",
            "parent_id": None
        },
        {
            "id": 3,
            "name": "Network",
            "description": "Network related issues",
            "parent_id": None
        },
        {
            "id": 4,
            "name": "Printers",
            "description": "Printer related issues",
            "parent_id": 1
        }
    ]
    
    if parent_id is not None:
        return [cat for cat in categories if cat["parent_id"] == parent_id]
    return categories

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Create Category")
async def create_category(category: CategoryCreate):
    """
    Create a new ticket category in GLPI.
    
    Parameters:
        category: Category information
        
    Returns:
        Created category information
    """
    # This is a sample implementation
    # In a real implementation, this would create a category in GLPI
    return {
        "id": 5,
        "name": category.name,
        "description": category.description,
        "parent_id": category.parent_id
    }

@router.get("/{category_id}", response_model=CategoryResponse, summary="Get Category")
async def get_category(category_id: int):
    """
    Retrieve a specific category by ID.
    
    Parameters:
        category_id: ID of the category to retrieve
        
    Returns:
        Category information
    """
    # This is a sample implementation
    # In a real implementation, this would get a category from GLPI
    categories = {
        1: {"id": 1, "name": "Hardware", "description": "Hardware related issues", "parent_id": None},
        2: {"id": 2, "name": "Software", "description": "Software related issues", "parent_id": None},
        3: {"id": 3, "name": "Network", "description": "Network related issues", "parent_id": None},
        4: {"id": 4, "name": "Printers", "description": "Printer related issues", "parent_id": 1}
    }
    
    if category_id not in categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
        
    return categories[category_id]

@router.put("/{category_id}", response_model=CategoryResponse, summary="Update Category")
async def update_category(category_id: int, category: CategoryUpdate):
    """
    Update an existing category.
    
    Parameters:
        category_id: ID of the category to update
        category: Updated category information
        
    Returns:
        Updated category information
    """
    # This is a sample implementation
    # In a real implementation, this would update a category in GLPI
    categories = {
        1: {"id": 1, "name": "Hardware", "description": "Hardware related issues", "parent_id": None},
        2: {"id": 2, "name": "Software", "description": "Software related issues", "parent_id": None},
        3: {"id": 3, "name": "Network", "description": "Network related issues", "parent_id": None},
        4: {"id": 4, "name": "Printers", "description": "Printer related issues", "parent_id": 1}
    }
    
    if category_id not in categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    existing = categories[category_id]
    updated = {
        "id": category_id,
        "name": category.name if category.name is not None else existing["name"],
        "description": category.description if category.description is not None else existing["description"],
        "parent_id": category.parent_id if category.parent_id is not None else existing["parent_id"]
    }
        
    return updated 