# Local MCP Server

A universal Model Context Protocol (MCP) server that automatically discovers and exposes local tools to AI assistants through a modern web interface and pluggable host adapter system.

## 🌟 Features

- **Directory-Based Auto-Discovery**: Automatically detects tools organized in individual folders under `tools/`
- **Universal Host Support**: Works with Claude Desktop, Generic MCP clients, and Google Gemini CLI through pluggable adapters
- **Intelligent Discovery Pipeline**: Auto-generates configurations for new tools with dual-config system
- **Visual Management**: Modern React-based web interface for tool configuration and monitoring
- **Host Adapter Architecture**: Pluggable system supporting different MCP communication protocols
- **Dependency Isolation**: Each tool gets its own virtual environment with automatic dependency management
- **Secure Execution**: Sandboxed script execution with timeout protection and structured result handling
- **Real-time Monitoring**: Live server status, execution monitoring, and configuration management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for web interface)
- `uv` package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/local-mcp-server.git
   cd local-mcp-server
   ```

2. **Start the development environment**
   ```bash
   # This will set up both server and web interface
   ./scripts/setup.sh
   ```

3. **Add your first tool**
   - Create a folder in `tools/` with your tool name (e.g., `tools/my-tool/`)
   - Copy the template: `cp tools/TEMPLATE/run.sh tools/my-tool/run.sh`
   - Add your tool logic (Python, Node.js, or any executable)
   - Edit `run.sh` to call your tool
   - Run `python server/discover_tools.py` to auto-generate configuration
   - Open http://localhost:3000 to configure it via the web interface
   - The tool will automatically appear in your MCP-compatible AI assistant

### Configure with Your MCP Host

#### Claude Desktop (Default)
```json
{
  "mcpServers": {
    "local-tools": {
      "command": "/path/to/local-mcp-server/server/start_server.sh",
      "args": ["--host=claude-desktop"],
      "cwd": "/path/to/local-mcp-server/server"
    }
  }
}
```

#### Generic MCP Client
```bash
# Start server for any MCP-compatible client
./server/start_server.sh --host=generic
```

#### Google Gemini CLI
```bash
# Start server for Google Gemini CLI
./server/start_server.sh --host=google-gemini-cli
```

See [Host Adapter Guide](docs/host-adapters.md) for detailed configuration instructions and supported features.

## 📁 Project Structure

```
local-mcp-server/
├── server/                    # MCP server core
│   ├── src/local_mcp/        # Main server code
│   │   ├── adapters/         # Host adapter system
│   │   ├── config.py         # Configuration management
│   │   ├── discovery.py      # Tool discovery system
│   │   └── server.py         # Main MCP server
│   ├── config/               # Server configurations
│   │   ├── tools/            # Individual tool configs
│   │   ├── tools.json        # Compiled tool config
│   │   └── config_templates/ # Host-specific templates
│   ├── discover_tools.py     # Discovery tool utility
│   ├── build_tools.py        # Config compilation utility
│   └── start_server.sh       # Server startup script
├── web-interface/            # Web management interface
│   ├── backend/              # FastAPI backend
│   ├── frontend/             # React frontend
│   └── start_dev.sh          # Development server
├── tools/                    # Directory-based tools (each in own folder)
│   ├── demo-features/        # Sample: Advanced features showcase
│   ├── file-ops/             # Sample: File operations
│   ├── http-client/          # Sample: HTTP utilities
│   ├── system-info/          # Sample: System information
│   └── text-utils/           # Sample: Text processing
├── docs/                     # Documentation
└── examples/                 # Host-specific configuration examples
```

## 🛠️ Sample Tools

The project includes several sample tools to help you get started:

- **System Info**: Get system information and metrics
- **File Operations**: File reading, writing, and listing utilities  
- **Text Processing**: Text manipulation and analysis tools
- **HTTP Client**: Make HTTP requests and API calls
- **Demo Features**: Showcase advanced configuration features

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Creating Tools](docs/creating-tools.md)
- [Host Adapter System](docs/host-adapters.md)
- [Discovery System](docs/discovery-system.md)
- [Web Interface Guide](docs/web-interface.md)
- [Configuration Management](docs/configuration.md)
- [API Reference](docs/api-reference.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- [Documentation](docs/)
- [GitHub Issues](https://github.com/yourusername/local-mcp-server/issues)
- [Discussions](https://github.com/yourusername/local-mcp-server/discussions)

---
