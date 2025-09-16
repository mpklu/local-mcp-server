# Host Compatibility Guide

The Local MCP Server now supports multiple MCP host types through its adapter system. This guide explains how to configure and use different host types.

## Supported Host Types

### 1. Claude Desktop (Default)
- **Host Type**: `claude-desktop`
- **Protocol**: stdio (stdin/stdout)
- **Status**: ✅ Fully supported
- **Use Case**: Default behavior for Claude Desktop application

### 2. Generic MCP
- **Host Type**: `generic`
- **Protocol**: stdio with generic MCP protocol
- **Status**: ✅ Basic support (stdio fallback)
- **Use Case**: Any MCP-compatible client

### 3. Google Gemini CLI
- **Host Type**: `google-gemini-cli`
- **Protocol**: stdio (Gemini CLI specific)
- **Status**: ⚠️ Experimental (based on expected behavior)
- **Use Case**: Google's Gemini CLI tool

## Quick Start

### Using the Startup Script

```bash
# Default (Claude Desktop)
./start_server.sh

# Generic MCP client
./start_server.sh --host=generic

# Google Gemini CLI
./start_server.sh --host=google-gemini-cli
```

### Using Python Directly

```bash
# Default behavior
uv run python -m local_mcp.server

# Specify host type
uv run python -m local_mcp.server --host=claude-desktop
uv run python -m local_mcp.server --host=generic
uv run python -m local_mcp.server --host=google-gemini-cli
```

## Configuration Examples

Each host type has its own configuration format and requirements.

### Claude Desktop

**Configuration Location**: `~/.config/claude/claude_desktop_config.json` (Linux/macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "local-tools": {
      "command": "/path/to/local-mcp-server/server/start_server.sh",
      "args": ["--host=claude-desktop"],
      "cwd": "/path/to/local-mcp-server/server",
      "env": {
        "PYTHONPATH": "/path/to/local-mcp-server/server/src"
      }
    }
  }
}
```

### Generic MCP Client

```json
{
  "mcp_server": {
    "type": "stdio",
    "command": "/path/to/local-mcp-server/server/start_server.sh",
    "args": ["--host=generic"],
    "working_directory": "/path/to/local-mcp-server/server",
    "environment": {
      "PYTHONPATH": "/path/to/local-mcp-server/server/src"
    }
  }
}
```

### Google Gemini CLI

⚠️ **Note**: This configuration is based on expected behavior. Please refer to official Google Gemini CLI documentation.

```json
{
  "gemini_cli": {
    "mcp_servers": {
      "local-tools": {
        "command": "/path/to/local-mcp-server/server/start_server.sh",
        "args": ["--host=google-gemini-cli"],
        "working_directory": "/path/to/local-mcp-server/server",
        "environment": {
          "PYTHONPATH": "/path/to/local-mcp-server/server/src"
        }
      }
    }
  }
}
```

**Required Environment Variables**:
```bash
export GOOGLE_AI_STUDIO_KEY="your-api-key"
export GEMINI_PROJECT_ID="your-project-id"
export GEMINI_CLI_CONFIG="/path/to/gemini/config"
```

## Configuration Templates

Pre-built configuration templates are available in the `server/config_templates/` directory:

- `claude-desktop.json.template`
- `generic-mcp.json.template`
- `google-gemini-cli.json.template`
- `docker-compose.yml.template`

## Backward Compatibility

✅ **Full backward compatibility** is maintained:
- Default behavior unchanged (Claude Desktop via stdio)
- Existing configurations continue to work
- No breaking changes to existing tools or web interface

## Environment Validation

Each adapter performs environment validation:

```bash
# Check if your environment is compatible
uv run python -c "
from local_mcp.adapters import AdapterFactory
from local_mcp.server import LocalMCPServer
from pathlib import Path

# Test each adapter
for host_type in AdapterFactory.get_available_types():
    server = LocalMCPServer(Path('../tools'), Path('./config'))
    adapter = AdapterFactory.create_adapter(host_type, server.server, {})
    is_valid, issues = adapter.validate_environment()
    print(f'{host_type}: {\"✅\" if is_valid else \"❌\"}')
    for issue in issues:
        print(f'  - {issue}')
"
```

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=/path/to/local-mcp-server/server/src
   ```

2. **Permission Issues**
   ```bash
   # Make startup script executable
   chmod +x start_server.sh
   ```

3. **Host-Specific Issues**
   ```bash
   # Check adapter validation
   ./start_server.sh --host=your-host-type --debug
   ```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
./start_server.sh --host=generic --debug
```

### Log Files

Logs are written to `config/server.log` and can help diagnose issues:

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