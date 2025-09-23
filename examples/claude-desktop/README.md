# Claude Desktop Configuration

This example shows how to configure Local MCP Server with Claude Desktop using the host adapter system.

## Quick Setup

1. **Auto-discover and configure tools:**
   ```bash
   cd /path/to/local-mcp-server/server
   python discover_tools.py
   python build_tools.py
   ```

2. **Find your Claude Desktop configuration file:**

   **macOS:**
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

   **Windows:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

3. **Update the configuration:**

   Replace the paths in `mcp-config.json` with your actual installation path:
   
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

   **Important**: Use absolute paths and ensure `start_server.sh` is executable.

3. **Restart Claude Desktop**

4. **Verify the connection:**
   - Open Claude Desktop
   - You should see your tools appear in the interface
   - Test with: "What tools do you have available?"

4. **Restart Claude Desktop and verify:**
   - Close and reopen Claude Desktop application  
   - You should see your tools appear in Claude's interface
   - Test with: "What tools are available to you?"

## Directory-Based Tool Management

With the new discovery system, tools are organized in directories:

```bash
tools/
├── system-info/         # System information tool
├── file-ops/            # File operation utilities  
├── http-client/         # HTTP request tools
├── text-utils/          # Text processing utilities
└── demo-features/       # Feature demonstration
```

Each tool is automatically discovered and configured. Use the web interface at http://localhost:3000 to manage tool settings.

## Verification Steps

1. **Test server startup:**
   ```bash
   cd /path/to/local-mcp-server/server
   ./start_server.sh --host claude-desktop
   # Should show "MCP Server running with claude-desktop adapter"
   ```

2. **Check tool discovery:**
   ```bash
   python discover_tools.py --list
   # Should show 5 discovered tools with ✅ status
   ```

3. **Verify Claude Desktop connection:**
   - Open Claude Desktop
   - Ask: "List your available tools"
   - Should see: system-info, file-ops, http-client, text-utils, demo-features

## Alternative Configuration (Direct Python)

For advanced users who prefer direct Python execution:

```json
{
  "mcpServers": {
    "local-tools": {
      "command": "uv",
      "args": ["run", "python", "-m", "local_mcp.server", "--host", "claude-desktop"],
      "cwd": "/absolute/path/to/local-mcp-server/server"
    }
  }
}
```

**Note:** The shell script approach is recommended as it handles environment setup automatically.

## Troubleshooting

- **Tools not appearing**: Check the server logs at `server/config/server.log`
- **Permission denied**: Ensure the startup script is executable: `chmod +x server/start_server.sh`
- **Path issues**: Use absolute paths in the configuration
- **Dependencies**: Make sure all tool dependencies are installed via the web interface
