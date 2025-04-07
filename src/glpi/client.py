"""
Base GLPI client module.
Provides core functionality for interacting with the GLPI API.
"""

from typing import Any, Dict, List, Optional, Union
import requests
from loguru import logger

from src.auth.session import GLPISession

class GLPIClient:
    """
    Base client for interacting with GLPI API.
    Handles common operations and error handling.
    """
    
    def __init__(self, session: GLPISession):
        """
        Initialize GLPI client.
        
        Args:
            session: GLPISession instance for authentication
        """
        self.session = session
        self.url = session.url
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the GLPI API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json: JSON data
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            Exception: If request fails
        """
        try:
            # Ensure valid session
            self.session.ensure_session()
            
            # Prepare request
            url = f"{self.url}/apirest.php/{endpoint}"
            headers = self.session._get_headers()
            
            # Make request
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers
            )
            
            # Handle response
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GLPI API request failed: {str(e)}")
            raise Exception(f"GLPI API request failed: {str(e)}")
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the GLPI API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Dict[str, Any]: Response data
        """
        return self._make_request("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the GLPI API.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            
        Returns:
            Dict[str, Any]: Response data
        """
        return self._make_request("POST", endpoint, data=data, json=json)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a PUT request to the GLPI API.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            
        Returns:
            Dict[str, Any]: Response data
        """
        return self._make_request("PUT", endpoint, data=data, json=json)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request to the GLPI API.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Dict[str, Any]: Response data
        """
        return self._make_request("DELETE", endpoint)
    
    def search(
        self,
        itemtype: str,
        criteria: List[Dict[str, Any]],
        range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for items in GLPI.
        
        Args:
            itemtype: Type of item to search for
            criteria: Search criteria
            range: Range of results to return
            
        Returns:
            Dict[str, Any]: Search results
        """
        params = {"criteria": criteria}
        if range:
            params["range"] = range
            
        return self.get(f"search/{itemtype}", params=params)
    
    def get_item(
        self,
        itemtype: str,
        id: Union[int, str],
        expand_dropdowns: bool = True
    ) -> Dict[str, Any]:
        """
        Get a specific item from GLPI.
        
        Args:
            itemtype: Type of item
            id: Item ID
            expand_dropdowns: Whether to expand dropdown fields
            
        Returns:
            Dict[str, Any]: Item data
        """
        params = {"expand_dropdowns": expand_dropdowns}
        return self.get(f"{itemtype}/{id}", params=params)
    
    def create_item(
        self,
        itemtype: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new item in GLPI.
        
        Args:
            itemtype: Type of item to create
            data: Item data
            
        Returns:
            Dict[str, Any]: Created item data
        """
        return self.post(itemtype, json=data)
    
    def update_item(
        self,
        itemtype: str,
        id: Union[int, str],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing item in GLPI.
        
        Args:
            itemtype: Type of item
            id: Item ID
            data: Updated item data
            
        Returns:
            Dict[str, Any]: Updated item data
        """
        return self.put(f"{itemtype}/{id}", json=data)
    
    def delete_item(
        self,
        itemtype: str,
        id: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Delete an item from GLPI.
        
        Args:
            itemtype: Type of item
            id: Item ID
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        return self.delete(f"{itemtype}/{id}") 