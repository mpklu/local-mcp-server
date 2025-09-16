"""
Host adapters for different MCP communication protocols.
"""

from .base import HostAdapter
from .claude_desktop import ClaudeDesktopAdapter
from .generic import GenericAdapter
from .google_gemini import GoogleGeminiAdapter
from .factory import AdapterFactory

__all__ = [
    "HostAdapter",
    "ClaudeDesktopAdapter", 
    "GenericAdapter",
    "GoogleGeminiAdapter",
    "AdapterFactory"
]