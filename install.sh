#!/bin/bash

# Create directory structure
mkdir -p ~/mcp-glpi/src/auth ~/mcp-glpi/src/glpi ~/mcp-glpi/src/agent ~/mcp-glpi/api ~/mcp-glpi/config ~/mcp-glpi/logs

# Create main.py
cat > ~/mcp-glpi/main.py << 'EOL'
"""
Main application module.
Initializes and runs the FastAPI application.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes import router as api_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="MCP GLPI Server",
    description="API Server for MCP GLPI Integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", 8000)),
        reload=os.getenv("MCP_DEBUG", "True").lower() == "true"
    )
EOL

# Create .env
cat > ~/mcp-glpi/.env << 'EOL'
# GLPI Configuration
GLPI_URL=http://your-glpi-instance.com
GLPI_APP_TOKEN=your_app_token
GLPI_USER_TOKEN=your_user_token
GLPI_DEFAULT_ENTITY_ID=0

# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_DEBUG=True

# Security
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cache Configuration
CACHE_TTL=300  # 5 minutes in seconds

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mcp-server.log
EOL

# Create api/routes.py
mkdir -p ~/mcp-glpi/api
cat > ~/mcp-glpi/api/routes.py << 'EOL'
"""
API routes module.
Defines the REST API endpoints for the MCP server.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.auth.session import GLPISession
from src.glpi.client import GLPIClient
from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager
from src.agent.decision import MCPDecisionMaker
from src.agent.thinking import MCPThinker
from src.agent.searching import MCPSearcher

# Create router
router = APIRouter()

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
EOL

# Create src/auth/session.py
mkdir -p ~/mcp-glpi/src/auth
cat > ~/mcp-glpi/src/auth/session.py << 'EOL'
"""
Session management module.
Handles authentication and session management with GLPI.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from cachetools import TTLCache
from loguru import logger

# Load environment variables
load_dotenv()

class GLPISession:
    """GLPI session management class."""
    
    def __init__(self):
        """Initialize session with environment variables."""
        self.url = os.getenv("GLPI_URL")
        self.app_token = os.getenv("GLPI_APP_TOKEN")
        self.user_token = os.getenv("GLPI_USER_TOKEN")
        self.session_token = None
        self.session_cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour cache
        
        if not all([self.url, self.app_token, self.user_token]):
            raise ValueError("Missing required GLPI configuration")
            
        logger.info("GLPI Session initialized")
        
    def get_session_token(self) -> str:
        """Get or create session token."""
        if self.session_token:
            return self.session_token
            
        # TODO: Implement session token retrieval from GLPI
        self.session_token = "dummy_token"
        return self.session_token
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "App-Token": self.app_token,
            "Session-Token": self.get_session_token(),
            "Content-Type": "application/json"
        }
        
    def clear_cache(self):
        """Clear session cache."""
        self.session_cache.clear()
        logger.info("Session cache cleared")
EOL

# Create src/glpi/client.py
mkdir -p ~/mcp-glpi/src/glpi
cat > ~/mcp-glpi/src/glpi/client.py << 'EOL'
"""
GLPI API client module.
Handles communication with the GLPI API.
"""

import requests
from typing import Any, Dict, Optional
from loguru import logger

from src.auth.session import GLPISession

class GLPIClient:
    """GLPI API client class."""
    
    def __init__(self, session: GLPISession):
        """Initialize client with session."""
        self.session = session
        self.base_url = session.url.rstrip("/")
        logger.info("GLPI Client initialized")
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to GLPI API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.session.get_headers()
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
            
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params)
        
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data)
        
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, data=data)
        
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint)
EOL

# Create src/glpi/tickets.py
cat > ~/mcp-glpi/src/glpi/tickets.py << 'EOL'
"""
Ticket management module.
Handles ticket operations with GLPI.
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from src.glpi.client import GLPIClient

class GLPITicketManager:
    """GLPI ticket management class."""
    
    def __init__(self, client: GLPIClient):
        """Initialize ticket manager with client."""
        self.client = client
        logger.info("GLPI Ticket Manager initialized")
        
    def create_ticket(self, **kwargs) -> Dict[str, Any]:
        """Create a new ticket."""
        try:
            result = self.client.post("Ticket", kwargs)
            logger.info(f"Ticket created: {result.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Failed to create ticket: {str(e)}")
            raise
            
    def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """Get ticket details."""
        try:
            result = self.client.get(f"Ticket/{ticket_id}")
            logger.info(f"Retrieved ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get ticket: {str(e)}")
            raise
            
    def update_ticket(self, ticket_id: int, **kwargs) -> Dict[str, Any]:
        """Update a ticket."""
        try:
            result = self.client.put(f"Ticket/{ticket_id}", kwargs)
            logger.info(f"Ticket updated: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update ticket: {str(e)}")
            raise
            
    def add_followup(self, ticket_id: int, content: str, is_private: bool = False) -> Dict[str, Any]:
        """Add a follow-up to a ticket."""
        try:
            data = {
                "tickets_id": ticket_id,
                "content": content,
                "is_private": is_private
            }
            result = self.client.post("TicketFollowup", data)
            logger.info(f"Followup added to ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to add followup: {str(e)}")
            raise
            
    def add_solution(self, ticket_id: int, content: str, status: int = 5) -> Dict[str, Any]:
        """Add a solution to a ticket."""
        try:
            data = {
                "tickets_id": ticket_id,
                "content": content,
                "status": status
            }
            result = self.client.post("TicketSolution", data)
            logger.info(f"Solution added to ticket: {ticket_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to add solution: {str(e)}")
            raise
EOL

# Create src/glpi/categories.py
cat > ~/mcp-glpi/src/glpi/categories.py << 'EOL'
"""
Category management module.
Handles category operations with GLPI.
"""

from typing import Dict, List, Optional
from loguru import logger

from src.glpi.client import GLPIClient

class GLPICategoryManager:
    """GLPI category management class."""
    
    def __init__(self, client: GLPIClient):
        """Initialize category manager with client."""
        self.client = client
        self._cache = {}
        logger.info("GLPI Category Manager initialized")
        
    def get_categories(self) -> Dict[str, Any]:
        """Get all categories."""
        try:
            result = self.client.get("ITILCategory")
            logger.info(f"Retrieved {len(result)} categories")
            return result
        except Exception as e:
            logger.error(f"Failed to get categories: {str(e)}")
            raise
            
    def get_category(self, category_id: int) -> Dict[str, Any]:
        """Get category details."""
        try:
            result = self.client.get(f"ITILCategory/{category_id}")
            logger.info(f"Retrieved category: {category_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get category: {str(e)}")
            raise
EOL

# Create src/agent/decision.py
mkdir -p ~/mcp-glpi/src/agent
cat > ~/mcp-glpi/src/agent/decision.py << 'EOL'
"""
Decision making module.
Handles ticket classification and action determination.
"""

from typing import Dict, Optional, Any
from loguru import logger

from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager

class MCPDecisionMaker:
    """MCP decision making class."""
    
    def __init__(self, ticket_manager: GLPITicketManager, category_manager: GLPICategoryManager):
        """Initialize decision maker with managers."""
        self.ticket_manager = ticket_manager
        self.category_manager = category_manager
        logger.info("MCP Decision Maker initialized")
        
    def _get_category_cache(self) -> Dict[str, Any]:
        """Get or update category cache."""
        try:
            categories = self.category_manager.get_categories()
            return {cat["id"]: cat for cat in categories}
        except Exception as e:
            logger.error(f"Failed to get category cache: {str(e)}")
            return {}
            
    def analyze_demand(self, content: str, title: str) -> Dict[str, Any]:
        """Analyze demand content and title."""
        # TODO: Implement content analysis
        return {
            "category": 1,
            "priority": 3
        }
        
    def determine_action(self, ticket_id: Optional[int], content: str, title: str) -> Dict[str, Any]:
        """Determine action for demand."""
        try:
            analysis = self.analyze_demand(content, title)
            
            if ticket_id:
                # Existing ticket
                return {
                    "action": "add_followup",
                    "ticket_id": ticket_id,
                    "content": content,
                    "is_private": False
                }
            else:
                # New ticket
                return {
                    "action": "create_ticket",
                    "name": title,
                    "content": content,
                    "itilcategories_id": analysis["category"],
                    "priority": analysis["priority"]
                }
        except Exception as e:
            logger.error(f"Failed to determine action: {str(e)}")
            raise
            
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute determined action."""
        try:
            action_type = action.get("action")
            
            if action_type == "create_ticket":
                return self.ticket_manager.create_ticket(**action)
            elif action_type == "add_followup":
                return self.ticket_manager.add_followup(**action)
            elif action_type == "close_ticket":
                return self.ticket_manager.update_ticket(action["ticket_id"], status=6)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
        except Exception as e:
            logger.error(f"Failed to execute action: {str(e)}")
            raise
EOL

# Create src/agent/thinking.py
cat > ~/mcp-glpi/src/agent/thinking.py << 'EOL'
"""
Thinking module.
Handles complex decision making and analysis.
"""

from typing import Dict, List, Optional
from loguru import logger

from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager

class MCPThinker:
    """MCP thinking class."""
    
    def __init__(self, ticket_manager: GLPITicketManager, category_manager: GLPICategoryManager):
        """Initialize thinker with managers."""
        self.ticket_manager = ticket_manager
        self.category_manager = category_manager
        logger.info("MCP Thinker initialized")
        
    def analyze_content(self, content: str, title: str) -> Dict[str, Any]:
        """Analyze content and title."""
        try:
            # Simple keyword-based analysis
            keywords = self._extract_keywords(content + " " + title)
            sentiment = self._analyze_sentiment(content)
            urgency = self._evaluate_urgency(keywords)
            complexity = self._evaluate_complexity(content)
            
            return {
                "keywords": keywords,
                "sentiment": sentiment,
                "urgency": urgency,
                "complexity": complexity,
                "related_tickets": self._find_related_tickets(keywords)
            }
        except Exception as e:
            logger.error(f"Failed to analyze content: {str(e)}")
            raise
            
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # TODO: Implement keyword extraction
        return ["keyword1", "keyword2"]
        
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze text sentiment."""
        # TODO: Implement sentiment analysis
        return "neutral"
        
    def _evaluate_urgency(self, keywords: List[str]) -> int:
        """Evaluate urgency level."""
        # TODO: Implement urgency evaluation
        return 3
        
    def _evaluate_complexity(self, text: str) -> int:
        """Evaluate complexity level."""
        # TODO: Implement complexity evaluation
        return 2
        
    def _find_related_tickets(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find related tickets."""
        try:
            # TODO: Implement related tickets search
            return []
        except Exception as e:
            logger.error(f"Failed to find related tickets: {str(e)}")
            return []
            
    def suggest_category(self, content: str, title: str) -> Dict[str, Any]:
        """Suggest category based on content."""
        try:
            analysis = self.analyze_content(content, title)
            categories = self.category_manager.get_categories()
            
            # TODO: Implement category suggestion
            return {
                "suggested_category": 1,
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"Failed to suggest category: {str(e)}")
            raise
            
    def evaluate_priority(self, content: str, title: str) -> Dict[str, int]:
        """Evaluate priority based on content."""
        try:
            analysis = self.analyze_content(content, title)
            
            # TODO: Implement priority evaluation
            return {
                "priority": 3,
                "urgency": analysis["urgency"],
                "impact": 3
            }
        except Exception as e:
            logger.error(f"Failed to evaluate priority: {str(e)}")
            raise
EOL

# Create src/agent/searching.py
cat > ~/mcp-glpi/src/agent/searching.py << 'EOL'
"""
Searching module.
Handles ticket and knowledge base searches.
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager

class MCPSearcher:
    """MCP searching class."""
    
    def __init__(self, ticket_manager: GLPITicketManager, category_manager: GLPICategoryManager):
        """Initialize searcher with managers."""
        self.ticket_manager = ticket_manager
        self.category_manager = category_manager
        logger.info("MCP Searcher initialized")
        
    def search_tickets(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10) -> Dict[str, Any]:
        """Search for tickets."""
        try:
            # Build search criteria
            criteria = {
                "searchText": query,
                "limit": limit
            }
            if filters:
                criteria.update(filters)
                
            # TODO: Implement ticket search
            return {
                "total": 0,
                "tickets": []
            }
        except Exception as e:
            logger.error(f"Failed to search tickets: {str(e)}")
            raise
            
    def search_similar_tickets(self, ticket_id: int, limit: int = 5) -> Dict[str, Any]:
        """Search for similar tickets."""
        try:
            # Get reference ticket
            ticket = self.ticket_manager.get_ticket(ticket_id)
            
            # TODO: Implement similar tickets search
            return {
                "total": 0,
                "tickets": []
            }
        except Exception as e:
            logger.error(f"Failed to search similar tickets: {str(e)}")
            raise
            
    def search_by_requester(self, requester_id: int, status: Optional[int] = None, limit: int = 10) -> Dict[str, Any]:
        """Search tickets by requester."""
        try:
            # Build search criteria
            criteria = {
                "requester_id": requester_id,
                "limit": limit
            }
            if status is not None:
                criteria["status"] = status
                
            # TODO: Implement requester search
            return {
                "total": 0,
                "tickets": []
            }
        except Exception as e:
            logger.error(f"Failed to search by requester: {str(e)}")
            raise
            
    def search_by_category(self, category_id: int, status: Optional[int] = None, limit: int = 10) -> Dict[str, Any]:
        """Search tickets by category."""
        try:
            # Build search criteria
            criteria = {
                "itilcategories_id": category_id,
                "limit": limit
            }
            if status is not None:
                criteria["status"] = status
                
            # TODO: Implement category search
            return {
                "total": 0,
                "tickets": []
            }
        except Exception as e:
            logger.error(f"Failed to search by category: {str(e)}")
            raise
            
    def search_solutions(self, query: str, category_id: Optional[int] = None, limit: int = 5) -> Dict[str, Any]:
        """Search for solutions."""
        try:
            # Build search criteria
            criteria = {
                "searchText": query,
                "status": 5,  # Closed tickets
                "limit": limit
            }
            if category_id:
                criteria["itilcategories_id"] = category_id
                
            # TODO: Implement solution search
            return {
                "total": 0,
                "solutions": []
            }
        except Exception as e:
            logger.error(f"Failed to search solutions: {str(e)}")
            raise
EOL

# Install Python and dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install fastapi==0.104.1 uvicorn==0.24.0 python-dotenv==1.0.0 requests==2.31.0 pydantic==2.4.2 python-jose==3.3.0 passlib==1.7.4 python-multipart==0.0.6 cachetools==5.3.1 loguru==0.7.2 pytest==7.4.3 httpx==0.25.1

# Set permissions
chmod -R 755 ~/mcp-glpi
chmod +x ~/mcp-glpi/main.py

echo "Installation completed successfully!"
echo "To start the server, run:"
echo "cd ~/mcp-glpi"
echo "source venv/bin/activate"
echo "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
EOL

# Make the script executable
chmod +x install.sh

# Run the installation script
./install.sh 