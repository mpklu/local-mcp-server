#!/bin/bash
# Test MCP Server with Inspector
# Quick development testing without restarting Claude Desktop

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="${SCRIPT_DIR}/server"
TOOLS_DIR="${SCRIPT_DIR}/../local_mcp_tools/tools"
CONFIG_DIR="${SERVER_DIR}/config"
INSPECTOR_PORT=6274

echo_info() { echo -e "${BLUE}ℹ${NC} $*"; }
echo_success() { echo -e "${GREEN}✓${NC} $*"; }
echo_warning() { echo -e "${YELLOW}⚠${NC} $*"; }
echo_error() { echo -e "${RED}✗${NC} $*"; }

# Check if inspector is installed
check_inspector() {
    echo_info "Checking for MCP Inspector..."
    
    if ! command -v npx &> /dev/null; then
        echo_error "npx not found. Please install Node.js and npm first."
        echo_info "Visit: https://nodejs.org/"
        exit 1
    fi
    
    # Quick check: try to run with --help and timeout after 3 seconds
    if timeout 3 npx --yes @modelcontextprotocol/inspector --help &> /dev/null 2>&1; then
        echo_success "MCP Inspector is available"
        return 0
    else
        # If timeout command doesn't exist (macOS), try without it
        if ! command -v timeout &> /dev/null; then
            echo_info "Quick check skipped (timeout not available)"
            echo_warning "Will attempt to use inspector (may download if not cached)"
            return 0
        fi
    fi
    
    return 1
}

# Install inspector
install_inspector() {
    echo_info "Note: npx will download @modelcontextprotocol/inspector on first use"
    echo_info "This is normal and only happens once (cached afterward)"
    echo_success "No installation needed - npx will handle it automatically"
}

# Run discovery to ensure tools are configured
run_discovery() {
    echo_info "Running tool discovery..."
    
    cd "${SERVER_DIR}"
    
    # Run discovery and build
    "${UV_CMD}" run python discover_tools.py --tools-dir "${TOOLS_DIR}"
    "${UV_CMD}" run python build_tools.py
    
    # Verify the compiled config was created
    if [[ -f "${CONFIG_DIR}/tools.json" ]]; then
        local tool_count=$(jq 'length' "${CONFIG_DIR}/tools.json" 2>/dev/null || echo "0")
        echo_success "Discovery complete - found ${tool_count} tools"
        echo_info "Config file: ${CONFIG_DIR}/tools.json"
    else
        echo_error "Config file not created: ${CONFIG_DIR}/tools.json"
        exit 1
    fi
}

# Stop any running MCP server
stop_server() {
    echo_info "Stopping any running MCP servers..."
    
    # Find and kill processes running local_mcp.server
    if pgrep -f "local_mcp.server" > /dev/null; then
        pkill -f "local_mcp.server" && echo_success "Stopped existing server" || echo_warning "Could not stop server"
        sleep 1
    else
        echo_info "No running server found"
    fi
    
    # Also check for inspector on the port
    if lsof -i :${INSPECTOR_PORT} > /dev/null 2>&1; then
        echo_warning "Port ${INSPECTOR_PORT} is in use. Attempting to free it..."
        lsof -ti :${INSPECTOR_PORT} | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Find uv executable
find_uv() {
    if command -v uv &> /dev/null; then
        echo "uv"
        return 0
    fi
    
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

# Validate directories
validate_setup() {
    echo_info "Validating setup..."
    
    if [[ ! -d "${TOOLS_DIR}" ]]; then
        echo_error "Tools directory not found: ${TOOLS_DIR}"
        exit 1
    fi
    
    if [[ ! -d "${CONFIG_DIR}" ]]; then
        echo_error "Config directory not found: ${CONFIG_DIR}"
        exit 1
    fi
    
    if [[ ! -d "${SERVER_DIR}" ]]; then
        echo_error "Server directory not found: ${SERVER_DIR}"
        exit 1
    fi
    
    # Check for uv
    UV_CMD=$(find_uv)
    if [[ -z "$UV_CMD" ]]; then
        echo_error "uv package manager not found!"
        echo_info "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    echo_success "Setup validated"
    echo_info "Tools directory: ${TOOLS_DIR}"
    echo_info "Config directory: ${CONFIG_DIR}"
    echo_success "Found uv at: ${UV_CMD}"
}

# Start server with inspector
start_inspector() {
    echo ""
    echo_info "Starting MCP Server with Inspector..."
    echo_info "Inspector will open at: http://localhost:${INSPECTOR_PORT}"
    echo_info "(First run may download @modelcontextprotocol/inspector)"
    echo ""
    echo_warning "Press Ctrl+C to stop the server"
    echo ""
    
    cd "${SERVER_DIR}"
    
    # Start with inspector using uv (same as start_server.sh)
    npx --yes @modelcontextprotocol/inspector \
        "${UV_CMD}" run python -m local_mcp.server \
        --tools-dir "${TOOLS_DIR}" \
        --config-dir "${CONFIG_DIR}"
}

# Display usage
show_usage() {
    cat << EOF
${GREEN}MCP Server Development Testing${NC}

This script helps you test your MCP server during development without
restarting Claude Desktop.

${BLUE}What it does:${NC}
  1. Checks and installs MCP Inspector if needed
  2. Stops any running MCP servers
  3. Starts server with Inspector web interface
  4. Opens browser at http://localhost:${INSPECTOR_PORT}

${BLUE}After starting:${NC}
  • Make changes to your tools
  • Refresh the Inspector page to reload
  • Test tools instantly with the web UI
  • View JSON responses in real-time

${BLUE}Usage:${NC}
  ./test_with_inspector.sh [options]

${BLUE}Options:${NC}
  -h, --help            Show this help message
  -s, --skip            Skip inspector check (assume installed)
  -d, --skip-discovery  Skip tool discovery (faster, use when only changing tool code)

${BLUE}Examples:${NC}
  ./test_with_inspector.sh                    # Full check and start
  ./test_with_inspector.sh --skip-discovery   # Skip discovery for faster iteration
  ./test_with_inspector.sh -s -d              # Skip both checks (fastest)

${BLUE}Tips:${NC}
  • Test tools directly first: cd tools/your-tool && ./run.sh function
  • Use Inspector for MCP protocol testing
  • Use --skip-discovery when only changing tool code (much faster)
  • Run full discovery when adding/removing tools or changing parameters
  • Only test with Claude Desktop when fully ready

EOF
}

# Main function
main() {
    local skip_check=false
    local skip_discovery=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -s|--skip)
                skip_check=true
                shift
                ;;
            -d|--skip-discovery)
                skip_discovery=true
                shift
                ;;
            *)
                echo_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    echo ""
    echo_info "MCP Server Development Testing"
    echo ""
    
    # Validate setup
    validate_setup
    
    # Run discovery unless skipped
    if [[ "${skip_discovery}" == false ]]; then
        run_discovery
    else
        echo_warning "Skipping tool discovery - using existing config"
        if [[ ! -f "${CONFIG_DIR}/tools.json" ]]; then
            echo_error "No existing config found. Run without --skip-discovery first."
            exit 1
        fi
    fi
    
    # Check/install inspector
    if [[ "${skip_check}" == false ]]; then
        if ! check_inspector; then
            echo_info "Inspector will be downloaded by npx on first use"
            echo_info "This is the recommended approach (no global install needed)"
        fi
    fi
    
    # Stop existing server
    stop_server
    
    # Start with inspector
    start_inspector
}

# Run main
main "$@"
