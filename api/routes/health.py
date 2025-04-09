"""
Health check routes for API monitoring.
"""

from fastapi import APIRouter
import os

router = APIRouter(tags=["health"])

@router.get("/health", summary="Health Check", description="Verifies if the API is up and running")
async def health_check():
    """
    Health check endpoint that verifies if the server is operational.
    
    Returns:
        dict: Status information including version and service health
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "glpi_url": os.getenv("GLPI_URL", "Not configured"),
        "environment": "development" if os.getenv("MCP_DEBUG", "True").lower() == "true" else "production"
    } 