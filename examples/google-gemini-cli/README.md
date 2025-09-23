# Google Gemini CLI Configuration

This example demonstrates how to configure Local MCP Server with Google's Gemini CLI using the experimental host adapter.

## ⚠️ Experimental Status

The Google Gemini CLI adapter is **experimental** and based on anticipated MCP protocol support. This configuration is prepared for future Gemini CLI MCP integration.

## Quick Setup

1. **Prepare Local MCP Server:**
   ```bash
   cd /absolute/path/to/local-mcp-server/server
   python discover_tools.py     # Auto-discover tools
   python build_tools.py        # Compile configuration
   ```

2. **Start server for Gemini CLI:**
   ```bash
   ./start_server.sh --host google-gemini-cli
   ```

3. **Configure Gemini CLI** (when available):
   - Follow Google's official MCP integration documentation
   - Use provided configuration template
   - Set required environment variables

## Host Adapter Features (Planned)

The Google Gemini CLI adapter will provide:
- 🔄 Gemini CLI protocol compatibility  
- 🔄 Google Cloud authentication integration
- 🔄 Optimized result formatting for Gemini models
- 🔄 Context-aware error handling and recovery
- 🔄 Integration with Google AI Studio workflows

## Current Implementation

Currently provides:
- ✅ Standard MCP stdio protocol (fallback)
- ✅ Tool discovery and registration
- ✅ Basic parameter validation
- ✅ JSON-RPC message handling
- ⚠️ Gemini-specific optimizations (prepared for future)

## Configuration Template

When Google Gemini CLI supports MCP, use this configuration structure:

```json
{
  "mcp_servers": {
    "local-tools": {
      "command": "/absolute/path/to/local-mcp-server/server/start_server.sh",
      "args": ["--host", "google-gemini-cli"],
      "cwd": "/absolute/path/to/local-mcp-server/server"
    }
  }
}
```

## Environment Setup (Anticipated)

Expected environment variables for full Gemini integration:
- `GOOGLE_AI_STUDIO_KEY`: Your Google AI Studio API key
- `GEMINI_PROJECT_ID`: Your Google Cloud project ID

Optional:
- `PYTHONPATH`: Ensure Python can find the server modules
- `GEMINI_DEBUG`: Enable debug logging for Gemini CLI

## Configuration Notes

⚠️ **Important**: This configuration is based on expected Gemini CLI behavior. 
The actual configuration format may differ. Please refer to the official 
Google Gemini CLI documentation for the most up-to-date configuration format.

## Troubleshooting

Common issues:
1. **Authentication**: Ensure your Google AI Studio key is valid
2. **Project Access**: Verify your project ID has Gemini API access
3. **CLI Version**: Make sure you have a compatible Gemini CLI version
4. **Network**: Check firewall and proxy settings

## Features

The Gemini CLI integration supports:
- All standard Local MCP Server tools
- Google AI Studio integration
- Project-based organization
- Environment-based configuration