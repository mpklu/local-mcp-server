"""
Generic MCP host adapter.

This adapter provides a generic HTTP/WebSocket-based MCP server
that can work with any MCP-compatible client.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Tuple
from pathlib import Path

from .base import HostAdapter

logger = logging.getLogger(__name__)


class GenericAdapter(HostAdapter):
    """
    Generic MCP adapter for HTTP/WebSocket communication.
    
    This adapter provides a more universal MCP server that can be
    accessed via HTTP endpoints or WebSocket connections.
    """
    
    @property
    def host_type(self) -> str:
        """Return the host type identifier."""
        return "generic"
    
    async def run(self) -> None:
        """
        Run the MCP server using HTTP/WebSocket for generic clients.
        
        This creates a server that listens on a configurable port
        and can accept connections from any MCP-compatible client.
        """
        port = self.config.get("port", 3001)
        host = self.config.get("host", "localhost")
        
        logger.info(f"Starting {self.host_type} MCP server on {host}:{port}")
        
        # For now, we'll use stdio as fallback but log the intent
        # In a full implementation, this would set up HTTP/WebSocket server
        logger.warning("Generic MCP server not fully implemented yet - using stdio fallback")
        logger.info(f"Would start HTTP server on http://{host}:{port}")
        logger.info("This is a placeholder for future HTTP/WebSocket implementation")
        
        # Import here to avoid issues if mcp package isn't available
        try:
            from mcp.server.stdio import stdio_server
            
            # Temporary stdio fallback with warning
            logger.warning("Using stdio fallback - connect via stdio interface")
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except ImportError:
            logger.error("MCP package not available - cannot run server")
            raise
    
    def get_configuration_template(self) -> Dict[str, Any]:
        """
        Return generic MCP configuration template.
        
        Returns a configuration that can be used with any MCP client.
        """
        return {
            "mcp_server": {
                "type": "http",
                "host": "localhost",
                "port": 3001,
                "endpoints": {
                    "tools": "/api/v1/tools",
                    "execute": "/api/v1/execute",
                    "health": "/api/v1/health"
                }
            },
            "fallback": {
                "type": "stdio",
                "command": "/absolute/path/to/local-mcp-server/server/start_server.sh",
                "args": ["--host=generic"],
                "cwd": "/absolute/path/to/local-mcp-server/server"
            }
        }
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate generic MCP environment.
        
        Check if we can bind to the configured port and host.
        """
        issues = []
        
        port = self.config.get("port", 3001)
        host = self.config.get("host", "localhost")
        
        # Basic port validation
        if not isinstance(port, int) or port < 1 or port > 65535:
            issues.append(f"Invalid port number: {port}")
        
        # Check if port is available (basic check)
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
        except OSError as e:
            issues.append(f"Cannot bind to {host}:{port} - {e}")
        
        return len(issues) == 0, issues