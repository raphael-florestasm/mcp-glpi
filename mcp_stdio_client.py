#!/usr/bin/env python3
"""
MCP GLPI Stdio Client
Command line utility to interact with MCP GLPI Server via stdin/stdout.
"""

import click
import os
import sys
from src.client.stdio import MCPStdioClient

@click.group()
@click.option('--url', default=None, help='MCP GLPI Server URL')
@click.pass_context
def cli(ctx, url):
    """
    Command line client for MCP GLPI Server.
    Uses stdin/stdout for communication.
    """
    # Use environment variable or default
    if not url:
        url = os.environ.get('MCP_URL', 'http://localhost:8000/api/v1')
    
    # Store client in context
    ctx.obj = {'url': url}

@cli.command()
@click.pass_context
def run(ctx):
    """Run the Stdio client."""
    url = ctx.obj['url']
    client = MCPStdioClient(base_url=url)
    click.echo(f"Connecting to MCP GLPI Server at {url}...", err=True)
    client.run()

@cli.command()
@click.pass_context
def example(ctx):
    """Print example commands."""
    examples = [
        {
            "command": "ping"
        },
        {
            "command": "get_categories"
        },
        {
            "command": "create_ticket",
            "ticket": {
                "name": "Impressora não imprime",
                "content": "A impressora do departamento financeiro não está funcionando",
                "itilcategories_id": 1,
                "urgency": 3,
                "impact": 3
            }
        },
        {
            "command": "get_ticket",
            "ticket_id": 123
        },
        {
            "command": "analyze_demand",
            "content": "Meu computador não liga, já verifiquei a tomada",
            "title": "Problema com computador"
        }
    ]
    
    import json
    for ex in examples:
        click.echo(json.dumps(ex, indent=2))
        click.echo()

if __name__ == '__main__':
    cli(obj={}) 