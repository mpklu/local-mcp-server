# Claude Desktop Configuration

This example shows how to configure Local MCP Server with Claude Desktop.

## Configuration Steps

1. **Find your Claude Desktop configuration file:**

   **macOS:**
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

   **Windows:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Update the configuration:**

   Replace the paths in `mcp-config.json` with your actual installation path:
   
   ```json
   {
     "mcpServers": {
       "local-tools": {
         "command": "/Users/yourname/local-mcp-server/server/start_server.sh",
         "args": ["--host=claude-desktop"],
         "cwd": "/Users/yourname/local-mcp-server/server",
         "env": {
           "PYTHONPATH": "/Users/yourname/local-mcp-server/server/src"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Verify the connection:**
   - Open Claude Desktop
   - You should see your tools appear in the interface
   - Test with: "What tools do you have available?"

## Alternative Configuration (Direct Python)

If you prefer to run Python directly:

```json
{
  "mcpServers": {
    "local-tools": {
      "command": "/path/to/local-mcp-server/server/.venv/bin/python3",
      "args": ["-m", "local_mcp.server"],
      "cwd": "/path/to/local-mcp-server/server"
    }
  }
}
```

**Note:** The shell script approach is recommended as it provides better logging and environment handling.

## Troubleshooting

- **Tools not appearing**: Check the server logs at `server/config/server.log`
- **Permission denied**: Ensure the startup script is executable: `chmod +x server/start_server.sh`
- **Path issues**: Use absolute paths in the configuration
- **Dependencies**: Make sure all tool dependencies are installed via the web interface
