"""
API routes initialization.
"""

from fastapi import APIRouter
from .tickets import router as tickets_router
from .categories import router as categories_router
from .solutions import router as solutions_router
from .health import router as health_router

# Create main router
router = APIRouter()

# Include all route modules
router.include_router(health_router)
router.include_router(tickets_router)
router.include_router(categories_router)
router.include_router(solutions_router) 