# Generic MCP Configuration

This directory contains configuration examples for using the Local MCP Server with generic MCP clients.

## Configuration File

Use the `mcp-config.json` as a template for connecting generic MCP clients to the Local MCP Server.

## Setup Instructions

1. **Update Paths**: Replace `/absolute/path/to/local-mcp-server` with your actual installation path
2. **Configure Client**: Use the configuration with your MCP-compatible client
3. **Test Connection**: Verify the server responds to MCP protocol requests

## Usage

```bash
# Start the server in generic mode
cd /path/to/local-mcp-server/server
./start_server.sh --host=generic

# The server will be available via stdio interface
# Connect your MCP client to the running process
```

## Client Integration

The generic configuration supports:
- Standard MCP protocol over stdio
- Tool discovery and execution
- JSON-RPC communication
- Error handling and timeouts

## Environment Variables

Optional environment variables for configuration:
- `PYTHONPATH`: Ensure Python can find the server modules
- `MCP_TIMEOUT`: Override default timeout settings
- `MCP_DEBUG`: Enable debug logging

## Troubleshooting

Common issues:
1. **Path Issues**: Ensure all paths in configuration are absolute
2. **Permissions**: Make sure start_server.sh is executable
3. **Python Environment**: Verify uv and dependencies are installed