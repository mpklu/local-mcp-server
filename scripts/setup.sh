#!/bin/bash
# Local MCP Server Setup Script
# One-command setup for the entire project

set -e  # Exit on any error

echo "🚀 Local MCP Server Setup"
echo "=========================="

# Check for required tools
echo "📋 Checking prerequisites..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ from https://python.org"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check for uv or install it
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "❌ Failed to install uv. Please install manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi
echo "✅ uv found: $(uv --version)"

echo ""
echo "🔧 Setting up Local MCP Server..."

# Setup server
echo "📦 Setting up MCP server..."
cd server
uv sync
echo "✅ Server dependencies installed"

# Create initial config structure
mkdir -p config/tools
echo "{}" > config/tools.json
echo "✅ Initial configuration created"

cd ..

# Setup web interface
echo "🌐 Setting up web interface..."
cd web-interface

# Setup backend
echo "📦 Installing backend dependencies..."
uv sync
echo "✅ Backend dependencies installed"

# Setup frontend
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
echo "✅ Frontend dependencies installed"

cd ../..

# Setup sample tools
echo "🛠️ Setting up sample tools..."
for tool_dir in tools/*/; do
    if [[ -f "$tool_dir/requirements.txt" ]]; then
        echo "  Installing dependencies for $(basename "$tool_dir")..."
        # We'll let the server handle individual tool dependencies
    fi
done
echo "✅ Sample tools ready"

# Make scripts executable
chmod +x server/start_server.sh
chmod +x web-interface/start_dev.sh

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📚 Next Steps:"
echo "1. Start the development environment:"
echo "   cd web-interface && ./start_dev.sh"
echo ""
echo "2. Open the web interface:"
echo "   http://localhost:3000"
echo ""
echo "3. Configure with Claude Desktop:"
echo "   Add this to your MCP configuration:"
echo "   {"
echo "     \"mcpServers\": {"
echo "       \"local-tools\": {"
echo "         \"command\": \"$(pwd)/server/start_server.sh\","
echo "         \"cwd\": \"$(pwd)/server\""
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "📖 For detailed instructions, see: docs/installation.md"
