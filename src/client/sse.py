"""
Server-Sent Events (SSE) client for MCP GLPI Server.
Allows receiving real-time updates for ticket changes and events.
"""

import json
import time
import threading
import requests
import sseclient
from typing import Callable, Dict, Any, Optional, List

class MCPSSEClient:
    """
    Client for receiving events from MCP GLPI Server via SSE.
    Provides event-based updates for ticket changes and notifications.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Initialize the SSE client.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.user_id = f"user_{int(time.time())}"
        self.running = False
        self.sse_thread = None
        self.event_handlers = {}
        
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Event type to handle
            handler: Function to call when event is received
        """
        self.event_handlers[event_type] = handler
        
    def watch_ticket(self, ticket_id: int) -> bool:
        """
        Start watching a ticket for updates.
        
        Args:
            ticket_id: Ticket ID to watch
            
        Returns:
            bool: Success status
        """
        try:
            response = self.session.post(
                f"{self.base_url}/sse/watch/{ticket_id}",
                params={"user_id": self.user_id}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error watching ticket {ticket_id}: {str(e)}")
            return False
            
    def unwatch_ticket(self, ticket_id: int) -> bool:
        """
        Stop watching a ticket for updates.
        
        Args:
            ticket_id: Ticket ID to unwatch
            
        Returns:
            bool: Success status
        """
        try:
            response = self.session.delete(
                f"{self.base_url}/sse/watch/{ticket_id}",
                params={"user_id": self.user_id}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error unwatching ticket {ticket_id}: {str(e)}")
            return False
    
    def _event_listener(self):
        """
        Internal thread function for listening to SSE events.
        """
        try:
            # Connect to SSE endpoint
            url = f"{self.base_url}/sse/stream?user_id={self.user_id}"
            response = self.session.get(url, stream=True)
            client = sseclient.SSEClient(response)
            
            # Process events
            for event in client.events():
                if not self.running:
                    break
                    
                # Process different event types
                try:
                    event_type = event.event
                    event_data = json.loads(event.data)
                    
                    # Call the appropriate handler
                    if event_type in self.event_handlers:
                        self.event_handlers[event_type](event_data)
                    elif '*' in self.event_handlers:
                        # Generic handler for all events
                        self.event_handlers['*'](event_data)
                        
                except json.JSONDecodeError:
                    print(f"Error decoding event data: {event.data}")
                except Exception as e:
                    print(f"Error processing event: {str(e)}")
                    
        except Exception as e:
            if self.running:
                print(f"SSE connection error: {str(e)}")
                # Try to reconnect after delay
                time.sleep(5)
                if self.running:
                    self._start_listener()
    
    def _start_listener(self):
        """
        Start the event listener thread.
        """
        self.sse_thread = threading.Thread(target=self._event_listener)
        self.sse_thread.daemon = True
        self.sse_thread.start()
    
    def start(self):
        """
        Start the SSE client.
        """
        if self.running:
            return
            
        self.running = True
        self._start_listener()
        
    def stop(self):
        """
        Stop the SSE client.
        """
        self.running = False
        if self.sse_thread and self.sse_thread.is_alive():
            self.sse_thread.join(timeout=2)
            
    def __del__(self):
        """
        Clean up resources on object destruction.
        """
        self.stop() 