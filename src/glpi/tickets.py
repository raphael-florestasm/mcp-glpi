"""
GLPI ticket management module.
Handles ticket-related operations with the GLPI API.
"""

from typing import Any, Dict, List, Optional, Union
from loguru import logger

from src.glpi.client import GLPIClient

class GLPITicketManager:
    """
    Manages ticket operations in GLPI.
    Provides methods for creating, updating, and managing tickets.
    """
    
    def __init__(self, client: GLPIClient):
        """
        Initialize ticket manager.
        
        Args:
            client: GLPIClient instance
        """
        self.client = client
        
    def create_ticket(
        self,
        name: str,
        content: str,
        itilcategories_id: int,
        type: int = 1,  # 1 = Incident, 2 = Request
        urgency: int = 3,  # 1 = Very high, 5 = Very low
        impact: int = 3,  # 1 = Very high, 5 = Very low
        priority: int = 3,  # 1 = Very high, 5 = Very low
        entities_id: Optional[int] = None,
        requesttypes_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new ticket in GLPI.
        
        Args:
            name: Ticket name/title
            content: Ticket description
            itilcategories_id: Category ID
            type: Ticket type (1=Incident, 2=Request)
            urgency: Urgency level (1-5)
            impact: Impact level (1-5)
            priority: Priority level (1-5)
            entities_id: Entity ID
            requesttypes_id: Request type ID
            **kwargs: Additional ticket fields
            
        Returns:
            Dict[str, Any]: Created ticket data
        """
        try:
            ticket_data = {
                "name": name,
                "content": content,
                "itilcategories_id": itilcategories_id,
                "type": type,
                "urgency": urgency,
                "impact": impact,
                "priority": priority,
                **kwargs
            }
            
            if entities_id:
                ticket_data["entities_id"] = entities_id
                
            if requesttypes_id:
                ticket_data["requesttypes_id"] = requesttypes_id
                
            result = self.client.create_item("Ticket", ticket_data)
            logger.info(f"Created ticket {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create ticket: {str(e)}")
            raise
    
    def get_ticket(
        self,
        ticket_id: Union[int, str],
        expand_dropdowns: bool = True,
        with_logs: bool = True
    ) -> Dict[str, Any]:
        """
        Get ticket details from GLPI.
        
        Args:
            ticket_id: Ticket ID
            expand_dropdowns: Whether to expand dropdown fields
            with_logs: Whether to include ticket logs
            
        Returns:
            Dict[str, Any]: Ticket data
        """
        try:
            params = {
                "expand_dropdowns": expand_dropdowns,
                "with_logs": with_logs
            }
            
            result = self.client.get_item("Ticket", ticket_id, params=params)
            logger.info(f"Retrieved ticket {ticket_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get ticket {ticket_id}: {str(e)}")
            raise
    
    def update_ticket(
        self,
        ticket_id: Union[int, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing ticket in GLPI.
        
        Args:
            ticket_id: Ticket ID
            **kwargs: Fields to update
            
        Returns:
            Dict[str, Any]: Updated ticket data
        """
        try:
            result = self.client.update_item("Ticket", ticket_id, kwargs)
            logger.info(f"Updated ticket {ticket_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update ticket {ticket_id}: {str(e)}")
            raise
    
    def add_followup(
        self,
        ticket_id: Union[int, str],
        content: str,
        is_private: bool = False
    ) -> Dict[str, Any]:
        """
        Add a follow-up to a ticket.
        
        Args:
            ticket_id: Ticket ID
            content: Follow-up content
            is_private: Whether the follow-up is private
            
        Returns:
            Dict[str, Any]: Created follow-up data
        """
        try:
            followup_data = {
                "items_id": ticket_id,
                "itemtype": "Ticket",
                "content": content,
                "is_private": 1 if is_private else 0
            }
            
            result = self.client.post(
                f"Ticket/{ticket_id}/ITILFollowup",
                json=followup_data
            )
            logger.info(f"Added follow-up to ticket {ticket_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add follow-up to ticket {ticket_id}: {str(e)}")
            raise
    
    def add_solution(
        self,
        ticket_id: Union[int, str],
        content: str,
        status: int = 5  # 5 = Closed
    ) -> Dict[str, Any]:
        """
        Add a solution to a ticket.
        
        Args:
            ticket_id: Ticket ID
            content: Solution content
            status: Ticket status after solution (5=Closed)
            
        Returns:
            Dict[str, Any]: Created solution data
        """
        try:
            solution_data = {
                "itemtype": "Ticket",
                "items_id": ticket_id,
                "content": content,
                "status": status
            }
            
            result = self.client.post(
                f"Ticket/{ticket_id}/ITILSolution",
                json=solution_data
            )
            logger.info(f"Added solution to ticket {ticket_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add solution to ticket {ticket_id}: {str(e)}")
            raise
    
    def search_tickets(
        self,
        criteria: List[Dict[str, Any]],
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for tickets in GLPI.
        
        Args:
            criteria: Search criteria
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            result = self.client.search("Ticket", criteria, range)
            logger.info(f"Found {len(result.get('data', []))} tickets")
            return result
            
        except Exception as e:
            logger.error(f"Failed to search tickets: {str(e)}")
            raise
    
    def get_tickets_by_status(
        self,
        status: int,
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get tickets by status.
        
        Args:
            status: Ticket status
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Ticket data
        """
        criteria = [{
            "field": "status",
            "searchtype": "equals",
            "value": status
        }]
        
        return self.search_tickets(criteria, range)
    
    def get_tickets_by_requester(
        self,
        requester_id: int,
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get tickets by requester.
        
        Args:
            requester_id: Requester user ID
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Ticket data
        """
        criteria = [{
            "field": "users_id_recipient",
            "searchtype": "equals",
            "value": requester_id
        }]
        
        return self.search_tickets(criteria, range)
    
    def get_tickets_by_category(
        self,
        category_id: int,
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get tickets by category.
        
        Args:
            category_id: Category ID
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Ticket data
        """
        criteria = [{
            "field": "itilcategories_id",
            "searchtype": "equals",
            "value": category_id
        }]
        
        return self.search_tickets(criteria, range) 