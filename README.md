# Local MCP Server

A universal Model Context Protocol (MCP) server that automatically discovers and exposes local scripts to AI assistants through a modern web interface.

## 🌟 Features

- **Auto-Discovery**: Automatically detects Python and shell scripts in your `tools/` directory
- **Universal MCP Support**: Works with Claude Desktop, and any MCP-compatible AI assistant
- **Visual Management**: Modern React-based web interface for tool configuration
- **Dependency Isolation**: Each tool gets its own virtual environment
- **Secure Execution**: Sandboxed script execution with timeout protection
- **Real-time Monitoring**: Live server status and execution monitoring

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
   - Drop a Python script in the `tools/` directory
   - Open http://localhost:3000 to configure it via the web interface
   - The tool will automatically appear in your MCP-compatible AI assistant

### Configure with Claude Desktop

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "local-tools": {
      "command": "/path/to/local-mcp-server/server/start_server.sh",
      "cwd": "/path/to/local-mcp-server/server"
    }
  }
}
```

## 📁 Project Structure

```
local-mcp-server/
├── server/                    # MCP server core
│   ├── src/local_mcp/        # Main server code
│   ├── config/               # Server configurations
│   └── start_server.sh       # Server startup script
├── web-interface/            # Web management interface
│   ├── backend/              # FastAPI backend
│   ├── frontend/             # React frontend
│   └── start_dev.sh          # Development server
├── tools/                    # Your script tools (sample tools included)
├── docs/                     # Documentation
└── examples/                 # Usage examples and tutorials
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
- [Web Interface Guide](docs/web-interface.md)
- [Host Compatibility](docs/host-compatibility.md)
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

**Made with ❤️ for the MCP community**
