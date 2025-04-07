"""
Search module for the MCP agent.
Handles ticket and knowledge base searches.
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager

class MCPSearcher:
    """
    Handles search operations for the MCP agent.
    Provides methods for searching tickets and knowledge base.
    """
    
    def __init__(
        self,
        ticket_manager: GLPITicketManager,
        category_manager: GLPICategoryManager
    ):
        """
        Initialize searcher.
        
        Args:
            ticket_manager: GLPITicketManager instance
            category_manager: GLPICategoryManager instance
        """
        self.ticket_manager = ticket_manager
        self.category_manager = category_manager
        
    def search_tickets(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for tickets matching the query.
        
        Args:
            query: Search query
            filters: Additional search filters
            limit: Maximum number of results
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            # Build search criteria
            criteria = []
            
            # Add content search
            if query:
                criteria.append({
                    "field": "content",
                    "searchtype": "contains",
                    "value": query
                })
            
            # Add filters
            if filters:
                for field, value in filters.items():
                    criteria.append({
                        "field": field,
                        "searchtype": "equals",
                        "value": value
                    })
            
            # Execute search
            range = f"0-{limit}"
            results = self.ticket_manager.search_tickets(criteria, range)
            
            logger.info(f"Found {len(results.get('data', []))} tickets matching query")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search tickets: {str(e)}")
            raise
    
    def search_similar_tickets(
        self,
        ticket_id: int,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search for tickets similar to the given ticket.
        
        Args:
            ticket_id: Reference ticket ID
            limit: Maximum number of results
            
        Returns:
            Dict[str, Any]: Similar tickets
        """
        try:
            # Get reference ticket
            ticket = self.ticket_manager.get_ticket(ticket_id)
            
            # Extract search terms
            content = ticket.get("content", "")
            title = ticket.get("name", "")
            category_id = ticket.get("itilcategories_id")
            
            # Build search criteria
            criteria = []
            
            # Search by category
            if category_id:
                criteria.append({
                    "field": "itilcategories_id",
                    "searchtype": "equals",
                    "value": category_id
                })
            
            # Search by content keywords
            words = content.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    criteria.append({
                        "field": "content",
                        "searchtype": "contains",
                        "value": word
                    })
            
            # Execute search
            range = f"0-{limit}"
            results = self.ticket_manager.search_tickets(criteria, range)
            
            # Filter out the reference ticket
            filtered_results = [
                t for t in results.get("data", [])
                if t["id"] != ticket_id
            ]
            
            logger.info(f"Found {len(filtered_results)} similar tickets")
            return {"data": filtered_results}
            
        except Exception as e:
            logger.error(f"Failed to search similar tickets: {str(e)}")
            raise
    
    def search_by_requester(
        self,
        requester_id: int,
        status: Optional[int] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for tickets by requester.
        
        Args:
            requester_id: Requester user ID
            status: Optional ticket status filter
            limit: Maximum number of results
            
        Returns:
            Dict[str, Any]: Requester's tickets
        """
        try:
            # Build search criteria
            criteria = [{
                "field": "users_id_recipient",
                "searchtype": "equals",
                "value": requester_id
            }]
            
            # Add status filter
            if status is not None:
                criteria.append({
                    "field": "status",
                    "searchtype": "equals",
                    "value": status
                })
            
            # Execute search
            range = f"0-{limit}"
            results = self.ticket_manager.search_tickets(criteria, range)
            
            logger.info(f"Found {len(results.get('data', []))} tickets for requester")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search by requester: {str(e)}")
            raise
    
    def search_by_category(
        self,
        category_id: int,
        status: Optional[int] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for tickets by category.
        
        Args:
            category_id: Category ID
            status: Optional ticket status filter
            limit: Maximum number of results
            
        Returns:
            Dict[str, Any]: Category tickets
        """
        try:
            # Build search criteria
            criteria = [{
                "field": "itilcategories_id",
                "searchtype": "equals",
                "value": category_id
            }]
            
            # Add status filter
            if status is not None:
                criteria.append({
                    "field": "status",
                    "searchtype": "equals",
                    "value": status
                })
            
            # Execute search
            range = f"0-{limit}"
            results = self.ticket_manager.search_tickets(criteria, range)
            
            logger.info(f"Found {len(results.get('data', []))} tickets in category")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search by category: {str(e)}")
            raise
    
    def search_solutions(
        self,
        query: str,
        category_id: Optional[int] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search for solutions in closed tickets.
        
        Args:
            query: Search query
            category_id: Optional category filter
            limit: Maximum number of results
            
        Returns:
            Dict[str, Any]: Solution search results
        """
        try:
            # Build search criteria
            criteria = [
                {
                    "field": "status",
                    "searchtype": "equals",
                    "value": 5  # Closed
                },
                {
                    "field": "content",
                    "searchtype": "contains",
                    "value": query
                }
            ]
            
            # Add category filter
            if category_id:
                criteria.append({
                    "field": "itilcategories_id",
                    "searchtype": "equals",
                    "value": category_id
                })
            
            # Execute search
            range = f"0-{limit}"
            results = self.ticket_manager.search_tickets(criteria, range)
            
            # Extract solutions
            solutions = []
            for ticket in results.get("data", []):
                ticket_id = ticket["id"]
                try:
                    ticket_details = self.ticket_manager.get_ticket(ticket_id)
                    if "solutions" in ticket_details:
                        solutions.extend(ticket_details["solutions"])
                except:
                    continue
            
            logger.info(f"Found {len(solutions)} solutions")
            return {"data": solutions}
            
        except Exception as e:
            logger.error(f"Failed to search solutions: {str(e)}")
            raise 