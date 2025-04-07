"""
GLPI category management module.
Handles category-related operations with the GLPI API.
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from src.glpi.client import GLPIClient

class GLPICategoryManager:
    """
    Manages category operations in GLPI.
    Provides methods for retrieving and managing categories.
    """
    
    def __init__(self, client: GLPIClient):
        """
        Initialize category manager.
        
        Args:
            client: GLPIClient instance
        """
        self.client = client
        
    def get_categories(
        self,
        expand_dropdowns: bool = True,
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all ITIL categories from GLPI.
        
        Args:
            expand_dropdowns: Whether to expand dropdown fields
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Category data
        """
        try:
            params = {"expand_dropdowns": expand_dropdowns}
            if range:
                params["range"] = range
                
            result = self.client.get("ITILCategory", params=params)
            logger.info(f"Retrieved {len(result.get('data', []))} categories")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get categories: {str(e)}")
            raise
    
    def get_category(
        self,
        category_id: int,
        expand_dropdowns: bool = True
    ) -> Dict[str, Any]:
        """
        Get a specific category from GLPI.
        
        Args:
            category_id: Category ID
            expand_dropdowns: Whether to expand dropdown fields
            
        Returns:
            Dict[str, Any]: Category data
        """
        try:
            params = {"expand_dropdowns": expand_dropdowns}
            result = self.client.get_item("ITILCategory", category_id, params=params)
            logger.info(f"Retrieved category {category_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get category {category_id}: {str(e)}")
            raise
    
    def search_categories(
        self,
        criteria: List[Dict[str, Any]],
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for categories in GLPI.
        
        Args:
            criteria: Search criteria
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            result = self.client.search("ITILCategory", criteria, range)
            logger.info(f"Found {len(result.get('data', []))} categories")
            return result
            
        except Exception as e:
            logger.error(f"Failed to search categories: {str(e)}")
            raise
    
    def get_categories_by_name(
        self,
        name: str,
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get categories by name.
        
        Args:
            name: Category name
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Category data
        """
        criteria = [{
            "field": "name",
            "searchtype": "contains",
            "value": name
        }]
        
        return self.search_categories(criteria, range)
    
    def get_categories_by_parent(
        self,
        parent_id: int,
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get categories by parent ID.
        
        Args:
            parent_id: Parent category ID
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Category data
        """
        criteria = [{
            "field": "itilcategories_id",
            "searchtype": "equals",
            "value": parent_id
        }]
        
        return self.search_categories(criteria, range)
    
    def get_category_tree(
        self,
        parent_id: Optional[int] = None,
        expand_dropdowns: bool = True
    ) -> Dict[str, Any]:
        """
        Get category tree structure.
        
        Args:
            parent_id: Parent category ID (None for root)
            expand_dropdowns: Whether to expand dropdown fields
            
        Returns:
            Dict[str, Any]: Category tree data
        """
        try:
            # Get all categories
            categories = self.get_categories(expand_dropdowns)
            
            # Build tree structure
            tree = {}
            for category in categories.get("data", []):
                cat_id = category.get("id")
                parent = category.get("itilcategories_id")
                
                if parent == parent_id:
                    tree[cat_id] = {
                        "data": category,
                        "children": self.get_category_tree(cat_id, expand_dropdowns)
                    }
            
            return tree
            
        except Exception as e:
            logger.error(f"Failed to build category tree: {str(e)}")
            raise
    
    def get_category_path(
        self,
        category_id: int,
        expand_dropdowns: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get the path from root to a specific category.
        
        Args:
            category_id: Category ID
            expand_dropdowns: Whether to expand dropdown fields
            
        Returns:
            List[Dict[str, Any]]: Category path
        """
        try:
            path = []
            current_id = category_id
            
            while current_id:
                category = self.get_category(current_id, expand_dropdowns)
                path.insert(0, category)
                current_id = category.get("itilcategories_id")
                
            return path
            
        except Exception as e:
            logger.error(f"Failed to get category path for {category_id}: {str(e)}")
            raise 