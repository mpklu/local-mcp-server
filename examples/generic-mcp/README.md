# Generic MCP Client Configuration

This example shows how to configure Local MCP Server with any MCP-compatible client using the generic host adapter.

## Quick Setup

1. **Prepare tools and configuration:**
   ```bash
   cd /absolute/path/to/local-mcp-server/server
   python discover_tools.py     # Auto-discover tools
   python build_tools.py        # Compile configuration
   ```

2. **Start server in generic mode:**
   ```bash
   ./start_server.sh --host generic
   ```

3. **Connect your MCP client to the stdio interface**

## Host Adapter Features

The generic adapter provides:
- ✅ Standard MCP protocol compliance
- ✅ Tool discovery and registration  
- ✅ Parameter validation and type conversion
- ✅ JSON-RPC message handling
- ✅ Basic error reporting and recovery
- ⚠️ Minimal host-specific optimizations

## Configuration Options

### Command Line Interface
```bash
# Basic usage
./start_server.sh --host generic

# With additional options (if supported by adapter)
./start_server.sh --host generic --debug --timeout 60
```

### Programmatic Usage
```python
import subprocess
import json

# Start server process  
process = subprocess.Popen([
    "/path/to/local-mcp-server/server/start_server.sh", 
    "--host", "generic"
], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

# Send MCP initialization request
init_request = {
    "jsonrpc": "2.0",
    "id": 1, 
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "my-client", "version": "1.0"}
    }
}

process.stdin.write(json.dumps(init_request) + "\n")
process.stdin.flush()

# Read response
response_line = process.stdout.readline()
response = json.loads(response_line)
print("Server capabilities:", response["result"]["capabilities"])
```

## Available Tools

After discovery, these tools are available via MCP protocol:

| Tool Name | Description | Entry Point |
|-----------|-------------|-------------|
| `system-info` | System information and metrics | `tools/system-info/run.py` |
| `file-ops` | File operation utilities | `tools/file-ops/run.py` |
| `http-client` | HTTP request and API tools | `tools/http-client/run.py` |
| `text-utils` | Text processing utilities | `tools/text-utils/run.py` |
| `demo-features` | Feature demonstration | `tools/demo-features/run.py` |

## Integration Examples

### Python MCP Client
```python
import asyncio
import json
from mcp import ClientSession

async def use_tools():
    # Connect to server
    session = ClientSession()
    await session.initialize()
    
    # List available tools
    tools = await session.list_tools()
    print(f"Available tools: {[t.name for t in tools]}")
    
    # Call a tool
    result = await session.call_tool("system-info", {"action": "get_info"})
    print(f"System info: {result}")
```

### Shell Script Integration  
```bash
#!/bin/bash
# example-client.sh

SERVER_PROCESS=$(./start_server.sh --host generic &)
SERVER_PID=$!

# Send MCP requests via named pipes or files
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
    socat - EXEC:"/path/to/start_server.sh --host generic"

# Cleanup
kill $SERVER_PID
```
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