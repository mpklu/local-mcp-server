"""
Local MCP Server - A Model Context Protocol server for local script execution.
"""

__version__ = "0.1.0"
__author__ = "kunlu"
__description__ = "Local MCP server for executing scripts in tools directory"

from .server import LocalMCPServer

__all__ = ["LocalMCPServer"]
