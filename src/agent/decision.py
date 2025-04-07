"""
Decision-making module for the MCP agent.
Handles ticket classification and action determination.
"""

from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager

class MCPDecisionMaker:
    """
    Makes decisions about ticket management based on content analysis.
    Determines appropriate categories, priorities, and actions.
    """
    
    def __init__(
        self,
        ticket_manager: GLPITicketManager,
        category_manager: GLPICategoryManager
    ):
        """
        Initialize decision maker.
        
        Args:
            ticket_manager: GLPITicketManager instance
            category_manager: GLPICategoryManager instance
        """
        self.ticket_manager = ticket_manager
        self.category_manager = category_manager
        self.category_cache = {}
        
    def _get_category_cache(self) -> Dict[int, Dict[str, Any]]:
        """
        Get or update category cache.
        
        Returns:
            Dict[int, Dict[str, Any]]: Category cache
        """
        if not self.category_cache:
            categories = self.category_manager.get_categories()
            self.category_cache = {
                cat["id"]: cat for cat in categories.get("data", [])
            }
        return self.category_cache
    
    def analyze_demand(
        self,
        content: str,
        title: str
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Analyze a demand to determine appropriate category and priority.
        
        Args:
            content: Demand content
            title: Demand title
            
        Returns:
            Tuple[int, Dict[str, Any]]: (category_id, priority_info)
        """
        try:
            # Get category cache
            categories = self._get_category_cache()
            
            # TODO: Implement more sophisticated analysis
            # For now, using a simple keyword-based approach
            
            # Default values
            category_id = 1  # Default category
            priority = 3  # Medium priority
            urgency = 3  # Medium urgency
            impact = 3  # Medium impact
            
            # Simple keyword analysis
            content_lower = content.lower()
            title_lower = title.lower()
            
            # Check for high priority keywords
            high_priority_keywords = ["urgent", "critical", "emergency", "down"]
            if any(keyword in content_lower or keyword in title_lower
                  for keyword in high_priority_keywords):
                priority = 1
                urgency = 1
                impact = 1
            
            # Check for low priority keywords
            low_priority_keywords = ["question", "information", "general"]
            if any(keyword in content_lower or keyword in title_lower
                  for keyword in low_priority_keywords):
                priority = 5
                urgency = 5
                impact = 5
            
            # Build priority info
            priority_info = {
                "priority": priority,
                "urgency": urgency,
                "impact": impact
            }
            
            logger.info(f"Analyzed demand: category={category_id}, priority={priority}")
            return category_id, priority_info
            
        except Exception as e:
            logger.error(f"Failed to analyze demand: {str(e)}")
            raise
    
    def determine_action(
        self,
        ticket_id: Optional[int],
        content: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Determine appropriate action for a ticket.
        
        Args:
            ticket_id: Existing ticket ID (if any)
            content: Ticket content
            title: Ticket title
            
        Returns:
            Dict[str, Any]: Action to take
        """
        try:
            # Analyze the demand
            category_id, priority_info = self.analyze_demand(content, title)
            
            if ticket_id:
                # Existing ticket - determine update action
                ticket = self.ticket_manager.get_ticket(ticket_id)
                current_status = ticket.get("status")
                
                # Check if ticket should be closed
                if "resolved" in content.lower() or "fixed" in content.lower():
                    return {
                        "action": "close",
                        "ticket_id": ticket_id,
                        "category_id": category_id,
                        **priority_info
                    }
                
                # Otherwise, add follow-up
                return {
                    "action": "followup",
                    "ticket_id": ticket_id,
                    "category_id": category_id,
                    **priority_info
                }
            else:
                # New ticket
                return {
                    "action": "create",
                    "category_id": category_id,
                    **priority_info
                }
                
        except Exception as e:
            logger.error(f"Failed to determine action: {str(e)}")
            raise
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the determined action.
        
        Args:
            action: Action to execute
            
        Returns:
            Dict[str, Any]: Action result
        """
        try:
            action_type = action.get("action")
            
            if action_type == "create":
                # Create new ticket
                result = self.ticket_manager.create_ticket(
                    name=action.get("title", "New Ticket"),
                    content=action.get("content", ""),
                    itilcategories_id=action["category_id"],
                    priority=action["priority"],
                    urgency=action["urgency"],
                    impact=action["impact"]
                )
                
            elif action_type == "followup":
                # Add follow-up to existing ticket
                result = self.ticket_manager.add_followup(
                    ticket_id=action["ticket_id"],
                    content=action.get("content", ""),
                    is_private=action.get("is_private", False)
                )
                
            elif action_type == "close":
                # Add solution and close ticket
                result = self.ticket_manager.add_solution(
                    ticket_id=action["ticket_id"],
                    content=action.get("content", "Ticket resolved"),
                    status=5  # Closed
                )
                
            else:
                raise ValueError(f"Unknown action type: {action_type}")
            
            logger.info(f"Executed action {action_type}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute action: {str(e)}")
            raise 