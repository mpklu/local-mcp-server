#!/bin/bash
# Local MCP Server Startup Script
# Universal startup script for any environment

# Function to find uv in common locations
find_uv() {
    # Check if uv is already in PATH
    if command -v uv &> /dev/null; then
        echo "uv"
        return 0
    fi
    
    # Common uv installation paths
    local uv_paths=(
        "$HOME/.local/bin/uv"
        "$HOME/.cargo/bin/uv"
        "/usr/local/bin/uv"
        "/opt/homebrew/bin/uv"
    )
    
    for path in "${uv_paths[@]}"; do
        if [[ -x "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    echo ""
    return 1
}

# Ensure we're in the server directory
cd "$(dirname "$0")"

# Display usage if help is requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Local MCP Server Startup Script"
    echo ""
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "Startup Modes:"
    echo "  (default)         Fast startup - loads existing config"
    echo "  --discover        Incremental discovery - checks for changes"
    echo "  --force-discover  Full discovery - complete refresh (slower)"
    echo ""
    echo "Options:"
    echo "  --debug           Enable debug logging"
    echo "  --tools-dir DIR   Override tools directory path"
    echo "  --config-dir DIR  Override config directory path"
    echo "  --host HOST       MCP host type (claude-desktop, generic, google-gemini-cli)"
    echo ""
    echo "Examples:"
    echo "  $0                              # Fast startup (recommended)"
    echo "  $0 --discover                   # Check for tool changes"
    echo "  $0 --force-discover             # Full refresh"
    echo "  $0 --debug                      # Debug mode"
    echo "  $0 --host=generic               # Generic MCP host"
    echo "  $0 --host=google-gemini-cli     # Google Gemini CLI host"
    echo ""
    echo "Requirements:"
    echo "  - Python 3.8+"
    echo "  - uv package manager (https://docs.astral.sh/uv/)"
    echo ""
    exit 0
fi

# Find uv executable
UV_CMD=$(find_uv)
if [[ -z "$UV_CMD" ]]; then
    echo "Error: uv package manager not found!"
    echo "Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
    echo ""
    echo "Quick install:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  # or with pip: pip install uv"
    exit 1
fi

# Create config directory if it doesn't exist
mkdir -p config

# Create tools directory if it doesn't exist (relative to server root)
mkdir -p ../tools

# Run the server
# Redirect logs to server.log for web interface monitoring
echo "Starting Local MCP Server..."
echo "Logs will be written to: $(pwd)/config/server.log"

exec "$UV_CMD" run python -m local_mcp.server "$@" >> config/server.log 2>&1
