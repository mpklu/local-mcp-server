"""
Claude Desktop MCP host adapter.

This adapter handles stdio-based communication for Claude Desktop,
which is the original and default behavior.
"""

import logging
from typing import Any, Dict, List, Tuple

from mcp.server.stdio import stdio_server

from .base import HostAdapter

logger = logging.getLogger(__name__)


class ClaudeDesktopAdapter(HostAdapter):
    """
    Adapter for Claude Desktop stdio-based MCP communication.
    
    This is the original implementation that communicates via stdin/stdout
    with Claude Desktop application.
    """
    
    @property
    def host_type(self) -> str:
        """Return the host type identifier."""
        return "claude-desktop"
    
    async def run(self) -> None:
        """
        Run the MCP server using stdio communication for Claude Desktop.
        
        This maintains the original behavior for backward compatibility.
        """
        logger.info(f"Starting {self.host_type} MCP server via stdio...")
        
        # Use the existing stdio server implementation
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    def get_configuration_template(self) -> Dict[str, Any]:
        """
        Return Claude Desktop configuration template.
        
        Returns the configuration format used by Claude Desktop.
        """
        return {
            "mcpServers": {
                "local-tools": {
                    "command": "/absolute/path/to/local-mcp-server/server/start_server.sh",
                    "cwd": "/absolute/path/to/local-mcp-server/server",
                    "env": {}
                }
            }
        }
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate Claude Desktop environment.
        
        For Claude Desktop, we mainly need to ensure stdio communication works.
        """
        issues = []
        
        # Check if we're in a stdio environment (basic check)
        import sys
        if not hasattr(sys.stdin, 'buffer'):
            issues.append("stdin buffer not available - may not work with Claude Desktop")
        
        if not hasattr(sys.stdout, 'buffer'):
            issues.append("stdout buffer not available - may not work with Claude Desktop")
        
        return len(issues) == 0, issues