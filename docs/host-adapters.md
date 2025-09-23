# Host Adapter System

The Local MCP Server features a pluggable host adapter architecture that enables seamless integration with different MCP clients and communication protocols. This system provides universal compatibility while maintaining optimal behavior for each specific host type.

## Architecture Overview

### Host Adapter Pattern
```
MCP Client  →  Host Adapter  →  Local MCP Server
(Claude)       (Translator)     (Core Logic)
```

Each adapter:
- **Translates** between host-specific protocols and the core MCP server
- **Optimizes** communication patterns for specific client requirements  
- **Handles** host-specific configuration and startup procedures
- **Provides** error handling and recovery appropriate for each host type

### Supported Host Types

| Host Type | Status | Protocol | Use Case |
|-----------|--------|----------|----------|
| `claude-desktop` | ✅ Production | stdio | Claude Desktop application (default) |
| `generic` | ✅ Production | stdio | Any MCP-compatible client |  
| `google-gemini-cli` | ⚠️ Experimental | stdio | Google Gemini CLI integration |

## Quick Start

### Command Line Usage

```bash
cd server/

# Claude Desktop (default)
./start_server.sh --host claude-desktop

# Generic MCP client  
./start_server.sh --host generic

# Google Gemini CLI
./start_server.sh --host google-gemini-cli

# Show all options
./start_server.sh --help
```

### Python API Usage

```python
from local_mcp.adapters.factory import AdapterFactory
from mcp.server import Server

# Create server instance
server = Server("local-mcp-server")

# Create adapter for specific host type  
adapter = AdapterFactory.create_adapter("claude-desktop", server)

# Run with adapter
await adapter.run()
```

## Host-Specific Configuration

### Claude Desktop

**Configuration File**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "local-tools": {
      "command": "/absolute/path/to/local-mcp-server/server/start_server.sh",
      "args": ["--host", "claude-desktop"],
      "cwd": "/absolute/path/to/local-mcp-server/server"
    }
  }
}
```

**Features**:
- ✅ Tool discovery and listing
- ✅ Parameter validation and type conversion
- ✅ Structured result handling
- ✅ Error reporting with context
- ✅ Resource cleanup and timeout management

**Best Practices**:
- Use absolute paths for `command` and `cwd`
- Ensure `start_server.sh` is executable (`chmod +x`)
- Test configuration with `./start_server.sh --host claude-desktop`

### Generic MCP Client

**Usage**: For any MCP-compatible client that supports stdio communication.

```bash
# Direct execution
./start_server.sh --host generic

# Via Python
uv run python -m local_mcp.server --host generic
**Protocol**: Standard MCP over stdio with minimal host-specific optimizations.

**Features**:
- ✅ Core MCP protocol compliance
- ✅ Standard tool registration and execution
- ✅ JSON-RPC message handling
- ✅ Basic error reporting
- ⚠️ Limited host-specific optimizations

**Integration Example**:
```python
import subprocess
import json

# Start server process
process = subprocess.Popen([
    "/path/to/start_server.sh", 
    "--host", "generic"
], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# Send MCP requests via stdin/stdout
request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
process.stdin.write(json.dumps(request) + "\n")
response = json.loads(process.stdout.readline())
```

### Google Gemini CLI

**Configuration**: Integration with Google's Gemini CLI tool.

```bash
# Start server for Gemini CLI
./start_server.sh --host google-gemini-cli
```

**Status**: ⚠️ Experimental - based on expected Gemini CLI MCP protocol support.

**Features** (Planned):
- 🔄 Gemini CLI protocol compatibility
- 🔄 Authentication integration
- 🔄 Optimized result formatting for Gemini
- 🔄 Context-aware error handling

**Note**: This adapter is prepared for future Gemini CLI MCP support. Current implementation provides stdio compatibility with planned Gemini-specific optimizations.

## Custom Host Adapters

### Creating a New Adapter

1. **Extend Base Adapter**:
```python
from .base import HostAdapter
from typing import Optional, Dict, Any

class MyCustomAdapter(HostAdapter):
    def __init__(self, server, config: Optional[Dict[str, Any]] = None):
        super().__init__(server, config)
        # Custom initialization
    
    async def run(self) -> None:
        # Implement host-specific startup logic
        pass
    
    def get_startup_message(self) -> str:
        return "Custom MCP Server ready for MyHost"
```

2. **Register with Factory**:
```python
# In adapters/factory.py
from .my_custom import MyCustomAdapter

class AdapterFactory:
    _adapters = {
        "claude-desktop": ClaudeDesktopAdapter,
        "generic": GenericAdapter,
        "google-gemini-cli": GoogleGeminiAdapter,
        "my-custom": MyCustomAdapter,  # Add your adapter
    }
```

3. **Add Configuration Template**:
```bash
# Create server/config_templates/my-custom.json
{
  "host_type": "my-custom",
  "description": "Configuration for MyCustom MCP client",
  "server_command": "./start_server.sh --host my-custom",
  "notes": "Specific setup instructions for MyCustom"
}
```

### Adapter Interface

All adapters implement the `HostAdapter` base class:

```python
class HostAdapter:
    def __init__(self, server: Server, config: Optional[Dict[str, Any]] = None)
    async def run(self) -> None
    def get_startup_message(self) -> str
```

**Required Methods**:
- `run()`: Main execution loop for the adapter
- `get_startup_message()`: Host-specific startup confirmation message

## Troubleshooting

### Configuration Issues

**Problem**: Claude Desktop doesn't detect server
```bash
# Verify server starts correctly
./start_server.sh --host claude-desktop

# Check configuration syntax
cat ~/.config/claude/claude_desktop_config.json | python -m json.tool

# Test with absolute paths
{
  "command": "/Users/yourname/local-mcp-server/server/start_server.sh"
}
```

**Problem**: Generic client connection fails
```bash
# Test stdio communication
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | ./start_server.sh --host generic

# Verify MCP protocol compatibility
./start_server.sh --host generic --debug
```

### Host Adapter Errors

**Problem**: Unknown host type
```bash
# List available adapters
./start_server.sh --help

# Use valid host type
./start_server.sh --host claude-desktop  # ✅ Valid
./start_server.sh --host invalid-host    # ❌ Invalid
```

**Problem**: Adapter initialization fails
```bash
# Check adapter configuration
python -c "
from local_mcp.adapters.factory import AdapterFactory
from mcp.server import Server
adapter = AdapterFactory.create_adapter('claude-desktop', Server('test'))
print('✅ Adapter created successfully')
"
```

### Performance Optimization

**For High-Frequency Usage**:
- Use `claude-desktop` adapter for Claude Desktop (optimized)
- Use `generic` adapter as fallback for unknown clients
- Monitor server logs for performance bottlenecks

**For Development**:
- Use `generic` adapter for testing with multiple clients
- Enable debug logging: `./start_server.sh --host generic --debug`
- Test adapter switching without restarting tools

## Configuration Templates

The system includes templates for common configurations:

```bash
server/config_templates/
├── claude-desktop.json      # Claude Desktop setup
├── generic-mcp.json         # Generic MCP client
├── google-gemini-cli.json   # Google Gemini CLI
└── docker-compose.yml       # Docker deployment
```

Use templates as starting points:
```bash
cp server/config_templates/claude-desktop.json ~/my-claude-config.json
# Edit paths and customize as needed
```

## Future Host Support

**Planned Adapters**:
- 🔄 VSCode MCP Extension
- 🔄 Cursor IDE Integration  
- 🔄 JetBrains MCP Plugin
- 🔄 Web Browser Extension
- 🔄 Discord Bot Integration

**Contributing**: To add support for a new host type, create an adapter following the pattern above and submit a pull request with:
- Adapter implementation extending `HostAdapter`
- Configuration template in `config_templates/`
- Documentation updates
- Integration tests

```bash
tail -f config/server.log
```

## Adding New Host Types

The adapter system is extensible. To add a new host type:

1. Create a new adapter class in `src/local_mcp/adapters/`
2. Implement the `HostAdapter` interface
3. Register it in the `AdapterFactory`
4. Add configuration templates and examples

See the existing adapters for implementation patterns.

## Future Enhancements

Planned improvements:
- HTTP/WebSocket support for generic adapter
- Auto-detection of host environments  
- Additional host-specific optimizations
- Enhanced configuration validation