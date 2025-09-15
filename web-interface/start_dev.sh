#!/bin/bash

# MCP Web Configuration Tool - Development Startup Script

echo "🚀 Starting MCP Web Configuration Tool"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the web_config directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists uv; then
    echo "❌ Error: uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ Error: npm is not installed. Please install Node.js first:"
    echo "   https://nodejs.org/"
    exit 1
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
if ! uv sync; then
    echo "❌ Error: Failed to install backend dependencies"
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if ! npm install; then
    echo "❌ Error: Failed to install frontend dependencies"
    exit 1
fi
cd ..

# Check if migration is needed
echo "🔄 Checking if migration is needed..."
TOOLS_JSON="../local_mcp_server/config/tools.json"
TOOLS_DIR="../local_mcp_server/config/tools"

if [ -f "$TOOLS_JSON" ] && [ ! -d "$TOOLS_DIR" ]; then
    echo "📋 Found existing tools.json - running migration..."
    cd ../local_mcp_server
    if python build_tools.py --migrate; then
        echo "✅ Migration completed successfully"
    else
        echo "⚠️  Migration failed, but continuing..."
    fi
    cd ../web_config
fi

# Start services
echo ""
echo "🚀 Starting services..."
echo "🔧 Backend will run on: http://localhost:8080"
echo "🌐 Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "▶️  Starting backend..."
uv run python -m backend.main &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend in background
echo "▶️  Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for user to stop
echo ""
echo "🎉 Services are running!"
echo "   Backend API: http://localhost:8080/api/health"
echo "   Frontend UI: http://localhost:3000"
echo ""
echo "📖 Check the README.md for usage instructions"
echo ""

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
