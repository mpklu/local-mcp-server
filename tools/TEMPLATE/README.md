# TEMPLATE Tool

This is a template for creating new tools for Local MCP Server.

## Structure

All tools must have:
- `run.sh` - Universal entry point (REQUIRED)
- `main.py` / `script.sh` / `index.js` - Actual tool logic
- `requirements.txt` - Dependencies (if applicable)
- `README.md` - Documentation

## Creating a New Tool

1. Copy this template:
   ```bash
   cp -r tools/TEMPLATE tools/my-new-tool
   ```

2. Edit `run.sh`:
   - Update tool name and description in header
   - Modify parameter definitions in comments
   - Update the `execute_tool()` function to call your script

3. Create your tool logic:
   - `main.py` for Python tools
   - `script.sh` for shell tools
   - `index.js` for Node.js tools

4. Add dependencies if needed:
   - `requirements.txt` for Python
   - `package.json` for Node.js

5. Run discovery:
   ```bash
   cd server
   python discover_tools.py
   python build_tools.py
   ```

## Example

See the sample tools for examples:
- `demo-features` - Python tool with advanced features
- `file-ops` - File operations
- `system-info` - System information gathering
