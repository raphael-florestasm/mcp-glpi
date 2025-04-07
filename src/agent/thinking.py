"""
Reasoning module for the MCP agent.
Handles complex decision-making and analysis.
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from src.glpi.tickets import GLPITicketManager
from src.glpi.categories import GLPICategoryManager

class MCPThinker:
    """
    Handles complex reasoning and analysis for the MCP agent.
    Provides methods for analyzing ticket content and making decisions.
    """
    
    def __init__(
        self,
        ticket_manager: GLPITicketManager,
        category_manager: GLPICategoryManager
    ):
        """
        Initialize thinker.
        
        Args:
            ticket_manager: GLPITicketManager instance
            category_manager: GLPICategoryManager instance
        """
        self.ticket_manager = ticket_manager
        self.category_manager = category_manager
        
    def analyze_content(
        self,
        content: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Analyze ticket content to extract key information.
        
        Args:
            content: Ticket content
            title: Ticket title
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # TODO: Implement more sophisticated content analysis
            # For now, using a simple keyword-based approach
            
            analysis = {
                "keywords": [],
                "sentiment": "neutral",
                "urgency_level": "medium",
                "complexity": "medium",
                "related_tickets": []
            }
            
            # Extract keywords
            words = content.lower().split()
            analysis["keywords"] = list(set(words))
            
            # Simple sentiment analysis
            positive_words = ["good", "great", "excellent", "thanks", "thank"]
            negative_words = ["bad", "poor", "terrible", "urgent", "critical"]
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            if positive_count > negative_count:
                analysis["sentiment"] = "positive"
            elif negative_count > positive_count:
                analysis["sentiment"] = "negative"
            
            # Urgency analysis
            urgent_words = ["urgent", "critical", "emergency", "immediate"]
            if any(word in content.lower() for word in urgent_words):
                analysis["urgency_level"] = "high"
            
            # Complexity analysis
            complex_words = ["complex", "difficult", "challenging", "complicated"]
            if any(word in content.lower() for word in complex_words):
                analysis["complexity"] = "high"
            
            # Find related tickets
            related_tickets = self._find_related_tickets(content, title)
            analysis["related_tickets"] = related_tickets
            
            logger.info(f"Content analysis completed: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze content: {str(e)}")
            raise
    
    def _find_related_tickets(
        self,
        content: str,
        title: str
    ) -> List[Dict[str, Any]]:
        """
        Find tickets related to the current content.
        
        Args:
            content: Ticket content
            title: Ticket title
            
        Returns:
            List[Dict[str, Any]]: Related tickets
        """
        try:
            # Extract key terms for search
            terms = content.lower().split() + title.lower().split()
            terms = list(set(terms))  # Remove duplicates
            
            related_tickets = []
            
            # Search for each term
            for term in terms:
                if len(term) < 3:  # Skip short terms
                    continue
                    
                criteria = [{
                    "field": "content",
                    "searchtype": "contains",
                    "value": term
                }]
                
                try:
                    results = self.ticket_manager.search_tickets(criteria)
                    related_tickets.extend(results.get("data", []))
                except:
                    continue
            
            # Remove duplicates
            seen_ids = set()
            unique_tickets = []
            for ticket in related_tickets:
                if ticket["id"] not in seen_ids:
                    seen_ids.add(ticket["id"])
                    unique_tickets.append(ticket)
            
            return unique_tickets[:5]  # Return top 5 related tickets
            
        except Exception as e:
            logger.error(f"Failed to find related tickets: {str(e)}")
            return []
    
    def suggest_category(
        self,
        content: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Suggest appropriate category based on content analysis.
        
        Args:
            content: Ticket content
            title: Ticket title
            
        Returns:
            Dict[str, Any]: Category suggestion
        """
        try:
            # Get all categories
            categories = self.category_manager.get_categories()
            
            # TODO: Implement more sophisticated category matching
            # For now, using a simple keyword-based approach
            
            # Default category
            suggestion = {
                "category_id": 1,
                "confidence": 0.5,
                "alternatives": []
            }
            
            # Simple keyword matching
            content_lower = content.lower()
            title_lower = title.lower()
            
            for category in categories.get("data", []):
                category_name = category.get("name", "").lower()
                
                # Check if category name appears in content or title
                if (category_name in content_lower or
                    category_name in title_lower):
                    suggestion["category_id"] = category["id"]
                    suggestion["confidence"] = 0.8
                    break
            
            logger.info(f"Category suggestion: {suggestion}")
            return suggestion
            
        except Exception as e:
            logger.error(f"Failed to suggest category: {str(e)}")
            raise
    
    def evaluate_priority(
        self,
        content: str,
        title: str,
        analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        Evaluate ticket priority based on content analysis.
        
        Args:
            content: Ticket content
            title: Ticket title
            analysis: Optional pre-computed content analysis
            
        Returns:
            Dict[str, int]: Priority levels
        """
        try:
            if analysis is None:
                analysis = self.analyze_content(content, title)
            
            # Default priority levels
            priority = {
                "priority": 3,  # Medium
                "urgency": 3,   # Medium
                "impact": 3     # Medium
            }
            
            # Adjust based on analysis
            if analysis["urgency_level"] == "high":
                priority["priority"] = 1
                priority["urgency"] = 1
                priority["impact"] = 1
            elif analysis["urgency_level"] == "low":
                priority["priority"] = 5
                priority["urgency"] = 5
                priority["impact"] = 5
            
            # Adjust based on complexity
            if analysis["complexity"] == "high":
                priority["impact"] = min(priority["impact"] - 1, 1)
            
            logger.info(f"Priority evaluation: {priority}")
            return priority
            
        except Exception as e:
            logger.error(f"Failed to evaluate priority: {str(e)}")
            raise 