# Local MCP Server

A Model Context Protocol server that exposes local scripts in the tools directory for execution through various MCP hosts.

## Features

- Multi-host support (Claude Desktop, Generic MCP, Google Gemini CLI)
- Automatic script discovery and configuration
- Web-based tool management interface
- Individual virtual environments for tool dependencies
- Comprehensive tool validation and testing

## Installation

```bash
# Install with uv
uv sync

# Or install with pip
pip install -e .
```

## Usage

```bash
# Run with default settings (Claude Desktop)
python -m local_mcp.server

# Run with specific host type
python -m local_mcp.server --host=claude-desktop
python -m local_mcp.server --host=generic
python -m local_mcp.server --host=google-gemini-cli

# Enable discovery
python -m local_mcp.server --discover

# Debug mode
python -m local_mcp.server --debug
```

## Host Types

- **claude-desktop**: Default stdio-based communication for Claude Desktop
- **generic**: Generic MCP server for any MCP-compatible client  
- **google-gemini-cli**: Optimized for Google's Gemini CLI tool

## Configuration

The server uses configuration files in the `config/` directory:
- `config.json`: Global server settings
- `tools.json`: Compiled tool configurations
- `tools/`: Individual tool configurations

## Development

```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest

# Format code
black src/
ruff check src/
```