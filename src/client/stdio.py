"""
Standard IO client for MCP GLPI Server.
Allows interaction with the server via stdin/stdout.
"""

import sys
import json
import time
import threading
import requests
from typing import Dict, Any, List, Optional, Callable

class MCPStdioClient:
    """
    Client for interacting with MCP GLPI Server via stdin/stdout.
    Provides a JSON-based protocol for command/response interaction.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Initialize the stdio client.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.continue_reading = True
        self.command_handlers = {
            "ping": self.handle_ping,
            "create_ticket": self.handle_create_ticket,
            "get_ticket": self.handle_get_ticket,
            "update_ticket": self.handle_update_ticket,
            "add_followup": self.handle_add_followup,
            "add_solution": self.handle_add_solution,
            "get_categories": self.handle_get_categories,
            "search_tickets": self.handle_search_tickets,
            "analyze_demand": self.handle_analyze_demand,
            "suggest_category": self.handle_suggest_category,
            "evaluate_priority": self.handle_evaluate_priority,
            "exit": self.handle_exit
        }
    
    def send_response(self, response: Dict[str, Any]):
        """
        Send a response to stdout.
        
        Args:
            response: Response data
        """
        # Add timestamp
        response["timestamp"] = time.time()
        
        # Write to stdout as JSON
        json_response = json.dumps(response)
        sys.stdout.write(json_response + "\n")
        sys.stdout.flush()
    
    def send_error(self, error_message: str, command: Optional[str] = None):
        """
        Send an error response to stdout.
        
        Args:
            error_message: Error message
            command: Original command (if applicable)
        """
        response = {
            "status": "error",
            "error": error_message
        }
        
        if command:
            response["command"] = command
            
        self.send_response(response)
    
    def handle_ping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ping command.
        
        Args:
            data: Command data
            
        Returns:
            Dict[str, Any]: Response data
        """
        return {
            "status": "success",
            "message": "pong",
            "server_time": time.time()
        }
    
    def handle_create_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle create_ticket command.
        
        Args:
            data: Command data with ticket details
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            response = self.session.post(
                f"{self.base_url}/tickets",
                json=data.get("ticket", {})
            )
            response.raise_for_status()
            return {
                "status": "success",
                "ticket": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_get_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_ticket command.
        
        Args:
            data: Command data with ticket_id
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            ticket_id = data.get("ticket_id")
            if not ticket_id:
                return {
                    "status": "error",
                    "error": "Missing ticket_id"
                }
                
            response = self.session.get(f"{self.base_url}/tickets/{ticket_id}")
            response.raise_for_status()
            return {
                "status": "success",
                "ticket": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_update_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle update_ticket command.
        
        Args:
            data: Command data with ticket_id and update details
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            ticket_id = data.get("ticket_id")
            if not ticket_id:
                return {
                    "status": "error",
                    "error": "Missing ticket_id"
                }
                
            response = self.session.put(
                f"{self.base_url}/tickets/{ticket_id}",
                json=data.get("ticket", {})
            )
            response.raise_for_status()
            return {
                "status": "success",
                "ticket": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_add_followup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle add_followup command.
        
        Args:
            data: Command data with ticket_id and followup details
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            ticket_id = data.get("ticket_id")
            if not ticket_id:
                return {
                    "status": "error",
                    "error": "Missing ticket_id"
                }
                
            response = self.session.post(
                f"{self.base_url}/tickets/{ticket_id}/followups",
                json=data.get("followup", {})
            )
            response.raise_for_status()
            return {
                "status": "success",
                "followup": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_add_solution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle add_solution command.
        
        Args:
            data: Command data with ticket_id and solution details
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            ticket_id = data.get("ticket_id")
            if not ticket_id:
                return {
                    "status": "error",
                    "error": "Missing ticket_id"
                }
                
            response = self.session.post(
                f"{self.base_url}/tickets/{ticket_id}/solutions",
                json=data.get("solution", {})
            )
            response.raise_for_status()
            return {
                "status": "success",
                "solution": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_get_categories(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_categories command.
        
        Args:
            data: Command data (not used)
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            response = self.session.get(f"{self.base_url}/categories")
            response.raise_for_status()
            return {
                "status": "success",
                "categories": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_search_tickets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle search_tickets command.
        
        Args:
            data: Command data with search parameters
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            response = self.session.post(
                f"{self.base_url}/search/tickets",
                json=data.get("search", {})
            )
            response.raise_for_status()
            return {
                "status": "success",
                "results": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_analyze_demand(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle analyze_demand command.
        
        Args:
            data: Command data with content and title
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            response = self.session.post(
                f"{self.base_url}/agent/analyze",
                json={
                    "content": data.get("content", ""),
                    "title": data.get("title", "")
                }
            )
            response.raise_for_status()
            return {
                "status": "success",
                "analysis": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_suggest_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle suggest_category command.
        
        Args:
            data: Command data with content and title
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            response = self.session.post(
                f"{self.base_url}/agent/suggest-category",
                json={
                    "content": data.get("content", ""),
                    "title": data.get("title", "")
                }
            )
            response.raise_for_status()
            return {
                "status": "success",
                "suggestion": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_evaluate_priority(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle evaluate_priority command.
        
        Args:
            data: Command data with content and title
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            response = self.session.post(
                f"{self.base_url}/agent/evaluate-priority",
                json={
                    "content": data.get("content", ""),
                    "title": data.get("title", "")
                }
            )
            response.raise_for_status()
            return {
                "status": "success",
                "priority": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_exit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle exit command.
        
        Args:
            data: Command data (not used)
            
        Returns:
            Dict[str, Any]: Response data
        """
        self.continue_reading = False
        return {
            "status": "success",
            "message": "Exiting"
        }
    
    def process_command(self, line: str):
        """
        Process a command from stdin.
        
        Args:
            line: Command line as JSON string
        """
        try:
            # Parse JSON command
            command_data = json.loads(line)
            
            # Get command type
            command = command_data.get("command")
            if not command:
                self.send_error("Missing 'command' field")
                return
            
            # Call appropriate handler
            handler = self.command_handlers.get(command)
            if not handler:
                self.send_error(f"Unknown command: {command}", command)
                return
                
            # Process command and send response
            response = handler(command_data)
            response["command"] = command
            self.send_response(response)
            
        except json.JSONDecodeError:
            self.send_error("Invalid JSON")
        except Exception as e:
            self.send_error(f"Error processing command: {str(e)}")
    
    def run(self):
        """
        Run the client, reading commands from stdin.
        """
        try:
            # Check server health
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            
            # Send ready message
            self.send_response({
                "status": "ready",
                "message": "MCP GLPI Stdio Client ready",
                "server_status": response.json()
            })
            
            # Process commands
            while self.continue_reading:
                line = sys.stdin.readline().strip()
                if not line:
                    continue
                    
                self.process_command(line)
                
        except Exception as e:
            self.send_error(f"Fatal error: {str(e)}") 