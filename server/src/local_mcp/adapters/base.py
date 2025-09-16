"""
Base interface for MCP host adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from mcp.server import Server


class HostAdapter(ABC):
    """
    Abstract base class for MCP host adapters.
    
    Each adapter handles communication with a specific MCP host type,
    allowing the server to support multiple host protocols.
    """
    
    def __init__(self, server: Server, config: Dict[str, Any]):
        """
        Initialize the host adapter.
        
        Args:
            server: The MCP server instance
            config: Host-specific configuration
        """
        self.server = server
        self.config = config
    
    @property
    @abstractmethod
    def host_type(self) -> str:
        """Return the host type identifier (e.g., 'claude-desktop', 'generic')."""
        pass
    
    @abstractmethod
    async def run(self) -> None:
        """
        Start the MCP server with the host-specific communication protocol.
        
        This method should handle the complete server lifecycle for the
        specific host type.
        """
        pass
    
    @abstractmethod
    def get_configuration_template(self) -> Dict[str, Any]:
        """
        Return a configuration template for this host type.
        
        Returns:
            Dictionary containing the configuration template
        """
        pass
    
    @abstractmethod
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate that the environment is suitable for this host type.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        pass
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Return information about the server configuration for this host.
        
        Returns:
            Dictionary with server information
        """
        return {
            "host_type": self.host_type,
            "server_name": self.server.name,
            "config": self.config
        }