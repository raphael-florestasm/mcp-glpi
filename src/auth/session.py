"""
GLPI session management module.
Handles authentication and session token management with GLPI.
"""

import time
from typing import Optional, Dict
import requests
from loguru import logger
from cachetools import TTLCache

from config.settings import settings

class GLPISession:
    """
    Manages GLPI session authentication and token handling.
    Implements caching and automatic token renewal.
    """
    
    def __init__(self):
        """Initialize GLPI session manager."""
        self.url = settings.GLPI_URL
        self.app_token = settings.GLI_APP_TOKEN
        self.user_token = settings.GLPI_USER_TOKEN
        self.session_token: Optional[str] = None
        self.session_expiry: float = 0
        self.cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)
        
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for GLPI API requests.
        
        Returns:
            Dict[str, str]: Headers for API requests
        """
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token
        }
        
        if self.session_token:
            headers["Session-Token"] = self.session_token
        else:
            headers["Authorization"] = f"user_token {self.user_token}"
            
        return headers
    
    def init_session(self) -> str:
        """
        Initialize a new GLPI session.
        
        Returns:
            str: Session token
            
        Raises:
            Exception: If session initialization fails
        """
        try:
            endpoint = f"{self.url}/apirest.php/initSession"
            headers = self._get_headers()
            
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data.get("session_token")
            self.session_expiry = time.time() + 3600  # 1 hour expiry
            
            logger.info("GLPI session initialized successfully")
            return self.session_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initialize GLPI session: {str(e)}")
            raise Exception(f"Failed to initialize GLPI session: {str(e)}")
    
    def ensure_session(self) -> str:
        """
        Ensure a valid GLPI session exists.
        Initializes a new session if needed.
        
        Returns:
            str: Valid session token
        """
        if not self.session_token or time.time() >= self.session_expiry:
            return self.init_session()
        return self.session_token
    
    def kill_session(self) -> bool:
        """
        Terminate the current GLPI session.
        
        Returns:
            bool: True if session was terminated successfully
        """
        if not self.session_token:
            return True
            
        try:
            endpoint = f"{self.url}/apirest.php/killSession"
            headers = self._get_headers()
            
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            
            self.session_token = None
            self.session_expiry = 0
            self.cache.clear()
            
            logger.info("GLPI session terminated successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to terminate GLPI session: {str(e)}")
            return False
    
    def __del__(self):
        """Cleanup on object destruction."""
        try:
            self.kill_session()
        except:
            pass 