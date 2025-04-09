#!/usr/bin/env python3
"""
MCP GLPI SSE Client Example
Shows how to use Server-Sent Events to receive real-time updates.
"""

import click
import json
import os
import sys
import time
from src.client.sse import MCPSSEClient

@click.group()
@click.option('--url', default=None, help='MCP GLPI Server URL')
@click.pass_context
def cli(ctx, url):
    """
    Example client for MCP GLPI Server using SSE.
    Demonstrates receiving real-time updates for ticket events.
    """
    # Use environment variable or default
    if not url:
        url = os.environ.get('MCP_URL', 'http://localhost:8000/api/v1')
    
    # Store in context
    ctx.obj = {'url': url}

@cli.command()
@click.argument('ticket_id', type=int)
@click.option('--timeout', default=0, help='Timeout in seconds (0 for no timeout)')
@click.pass_context
def watch(ctx, ticket_id, timeout):
    """Watch a ticket for updates."""
    url = ctx.obj['url']
    
    # Create and configure SSE client
    client = MCPSSEClient(base_url=url)
    
    # Register event handlers
    def on_ticket_updated(data):
        click.echo(f"Ticket {ticket_id} updated:")
        click.echo(json.dumps(data, indent=2))
        click.echo()
    
    def on_followup_added(data):
        click.echo(f"New follow-up added to ticket {ticket_id}:")
        click.echo(json.dumps(data, indent=2))
        click.echo()
    
    def on_solution_added(data):
        click.echo(f"Solution added to ticket {ticket_id}:")
        click.echo(json.dumps(data, indent=2))
        click.echo()
    
    def on_connected(data):
        click.echo(f"Connected to SSE stream: {data['message']}")
        click.echo(f"User ID: {data['user_id']}")
        click.echo()
        
    # Register event handlers
    client.register_handler('connected', on_connected)
    client.register_handler('ticket_updated', on_ticket_updated)
    client.register_handler('followup_added', on_followup_added)
    client.register_handler('solution_added', on_solution_added)
    
    # Start client and watch the ticket
    try:
        client.start()
        if client.watch_ticket(ticket_id):
            click.echo(f"Watching ticket {ticket_id} for updates...")
            click.echo("Press Ctrl+C to stop")
            
            if timeout > 0:
                time.sleep(timeout)
            else:
                # Keep script running until manually stopped
                while True:
                    time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nStopping...")
    finally:
        client.stop()

@cli.command()
@click.pass_context
def monitor(ctx):
    """Monitor all ticket events."""
    url = ctx.obj['url']
    
    # Create and configure SSE client
    client = MCPSSEClient(base_url=url)
    
    # Generic handler for all events
    def on_any_event(data):
        event_type = data.get('event_type', 'unknown')
        ticket_id = data.get('ticket_id', 'N/A')
        timestamp = data.get('timestamp', 'N/A')
        
        click.echo(f"[{timestamp}] Event: {event_type} - Ticket: {ticket_id}")
        click.echo(json.dumps(data, indent=2))
        click.echo()
    
    # Register a catch-all handler
    client.register_handler('*', on_any_event)
    
    # Start client
    try:
        client.start()
        click.echo("Monitoring all ticket events...")
        click.echo("Press Ctrl+C to stop")
        
        # Keep script running until manually stopped
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nStopping...")
    finally:
        client.stop()

if __name__ == '__main__':
    cli(obj={}) 