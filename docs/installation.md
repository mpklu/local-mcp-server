# Installation Guide

## Prerequisites

Before installing Local MCP Server, ensure you have:

- **Python 3.8+** - [Download from python.org](https://python.org)
- **Node.js 16+** - [Download from nodejs.org](https://nodejs.org) 
- **Git** - For cloning the repository

The installer will automatically install `uv` (Python package manager) if it's not present.

## Quick Install

### One-Command Setup

```bash
git clone https://github.com/yourusername/local-mcp-server.git
cd local-mcp-server
./scripts/setup.sh
```

This will:
- Install all dependencies
- Set up the development environment  
- Configure sample tools with directory-based structure
- Generate initial individual tool configurations
- Compile tools.json for MCP server
- Provide next steps for host adapter configuration

### Manual Installation

If you prefer manual setup:

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/local-mcp-server.git
cd local-mcp-server
```

#### 2. Install uv Package Manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 3. Setup Server
```bash
cd server
uv sync
mkdir -p config/tools
# Auto-generate tool configurations
python discover_tools.py
# Compile configurations
python build_tools.py
```

#### 4. Setup Web Interface
```bash
cd ../web-interface
uv sync                    # Backend
cd frontend && npm install # Frontend
```

## Starting the System

### Development Mode (Recommended for Setup)

Start both the MCP server and web interface:

```bash
cd web-interface
./start_dev.sh
```

This provides:
- **Backend**: http://localhost:8080 (API)
- **Frontend**: http://localhost:3000 (Web Interface)
- **Live Reload**: Automatic updates during development

### Production Mode

Start the MCP server for different host types:

```bash
cd server

# For Claude Desktop (default)
./start_server.sh --host claude-desktop

# For generic MCP clients
./start_server.sh --host generic

# For Google Gemini CLI
./start_server.sh --host google-gemini-cli
./start_server.sh
```

## Verification

### 1. Test Web Interface
Open http://localhost:3000 and verify:
- ✅ Dashboard loads with sample tools
- ✅ Tool list shows system-info, file-ops, etc.
- ✅ Can view and edit tool configurations

### 2. Test MCP Server
```bash
# In another terminal
cd server
./start_server.sh --help
```

Should show host adapter options and usage information without errors.

### 3. Test Discovery System
```bash
cd server
python discover_tools.py --list
```

Should show 5 discovered tools with configuration status.

### 4. Test Sample Tools
Through the web interface:
- Navigate to "Tools" → "system-info"
- Click "Test Tool" → "get_system_info"
- Should return JSON with system information

## Next Steps

1. **Configure with AI Assistant**: See [Host Adapter Guide](host-adapters.md)
2. **Create Your First Tool**: See [Creating Tools Guide](creating-tools.md)
3. **Understand Discovery System**: See [Discovery System Guide](discovery-system.md)  
4. **Web Interface Tutorial**: See [Web Interface Guide](web-interface.md)

## Common Issues

### uv Installation Fails
```bash
# Alternative installation methods
pip install uv
# OR with conda
conda install -c conda-forge uv
```

### Node.js Issues
Use Node Version Manager (nvm):
```bash
# Install nvm first: https://github.com/nvm-sh/nvm
nvm install 18
nvm use 18
```

### Permission Denied
```bash
chmod +x scripts/setup.sh
chmod +x server/start_server.sh
chmod +x web-interface/start_dev.sh
```

### Port Already in Use
```bash
# Kill processes using ports 3000 or 8080
lsof -ti:3000 | xargs kill
lsof -ti:8080 | xargs kill
```

## Docker Installation (Alternative)

For a containerized setup:

```bash
git clone https://github.com/yourusername/local-mcp-server.git
cd local-mcp-server
docker-compose up -d
```

Access via:
- **Web Interface**: http://localhost:3000
- **API**: http://localhost:8080

## Uninstall

To remove Local MCP Server:

```bash
# Remove the directory
rm -rf local-mcp-server/

# Remove uv (if installed by this project)
rm -rf ~/.local/share/uv ~/.local/bin/uv
```

## Support

- 📚 [Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/yourusername/local-mcp-server/issues)
- 💬 [Discussions](https://github.com/yourusername/local-mcp-server/discussions)
