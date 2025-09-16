"""
Host adapter factory for creating appropriate adapters based on host type.
"""

import logging
from typing import Any, Dict, Optional

from mcp.server import Server
from .base import HostAdapter
from .claude_desktop import ClaudeDesktopAdapter
from .generic import GenericAdapter
from .google_gemini import GoogleGeminiAdapter

logger = logging.getLogger(__name__)


class AdapterFactory:
    """Factory for creating host adapters."""
    
    _adapters = {
        "claude-desktop": ClaudeDesktopAdapter,
        "generic": GenericAdapter,
        "google-gemini-cli": GoogleGeminiAdapter,
    }
    
    @classmethod
    def create_adapter(
        cls, 
        host_type: str, 
        server: Server, 
        config: Optional[Dict[str, Any]] = None
    ) -> HostAdapter:
        """
        Create a host adapter for the specified type.
        
        Args:
            host_type: The type of host adapter to create
            server: The MCP server instance
            config: Host-specific configuration
            
        Returns:
            HostAdapter instance for the specified type
            
        Raises:
            ValueError: If host_type is not supported
        """
        if config is None:
            config = {}
            
        if host_type not in cls._adapters:
            available = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"Unsupported host type: {host_type}. "
                f"Available types: {available}"
            )
        
        adapter_class = cls._adapters[host_type]
        logger.info(f"Creating {host_type} adapter")
        return adapter_class(server, config)
    
    @classmethod
    def get_available_types(cls) -> list[str]:
        """Return list of available host types."""
        return list(cls._adapters.keys())
    
    @classmethod
    def get_default_type(cls) -> str:
        """Return the default host type (for backward compatibility)."""
        return "claude-desktop"