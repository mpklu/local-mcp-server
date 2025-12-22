#!/bin/bash
# Tool: TEMPLATE
# Description: Template for creating new tools with standardized run.sh entry point
#
# @param example_param: An example parameter (type: string, required: false)
# @param count: Number of iterations (type: integer, required: false, default: 1)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ===========================
# CONFIGURATION
# ===========================
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_NAME="$(basename "${TOOL_DIR}")"
LOG_PREFIX="[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] [${TOOL_NAME}]"

# ===========================
# LOGGING HELPERS
# ===========================
log_info() { echo "${LOG_PREFIX} INFO: $*" >&2; }
log_error() { echo "${LOG_PREFIX} ERROR: $*" >&2; }
log_debug() { [[ "${DEBUG:-0}" == "1" ]] && echo "${LOG_PREFIX} DEBUG: $*" >&2 || true; }

# ===========================
# ENVIRONMENT SETUP
# ===========================
setup_environment() {
    log_info "Setting up environment..."
    
    # Example: Python tool with virtual environment
    if [[ -f "${TOOL_DIR}/requirements.txt" ]]; then
        VENV_DIR="${TOOL_DIR}/.venv"
        
        if [[ ! -d "${VENV_DIR}" ]]; then
            log_info "Creating virtual environment..."
            python3 -m venv "${VENV_DIR}"
            source "${VENV_DIR}/bin/activate"
            pip install --quiet --upgrade pip
            pip install --quiet -r "${TOOL_DIR}/requirements.txt"
            log_info "Installed dependencies from requirements.txt"
        else
            source "${VENV_DIR}/bin/activate"
            log_debug "Using existing virtual environment"
        fi
    fi
    
    # Example: Check system dependencies
    # if ! command -v jq &> /dev/null; then
    #     log_error "Required dependency 'jq' not found. Install with: brew install jq"
    #     exit 1
    # fi
    
    # Example: Set environment variables
    # export MY_TOOL_CONFIG="${TOOL_DIR}/config.yaml"
    
    log_info "Environment ready"
}

# ===========================
# HEALTH CHECK
# ===========================
health_check() {
    log_info "Running health check..."
    
    # Verify tool dependencies are available
    if [[ -f "${TOOL_DIR}/requirements.txt" ]] && [[ ! -d "${TOOL_DIR}/.venv" ]]; then
        log_error "Virtual environment not found. Run setup first."
        exit 1
    fi
    
    # Add custom health checks here
    
    log_info "Health check passed"
    exit 0
}

# ===========================
# TOOL EXECUTION
# ===========================
execute_tool() {
    log_info "Executing tool with args: $*"
    local start_time=$(date +%s)
    
    # OPTION 1: Python tool (most common)
    python3 "${TOOL_DIR}/main.py" "$@"
    
    # OPTION 2: Shell script
    # bash "${TOOL_DIR}/script.sh" "$@"
    
    # OPTION 3: Node.js tool
    # node "${TOOL_DIR}/index.js" "$@"
    
    # OPTION 4: Compiled binary
    # "${TOOL_DIR}/bin/tool" "$@"
    
    # OPTION 5: Docker container
    # docker run --rm -v "${TOOL_DIR}:/workspace" my-tool:latest "$@"
    
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ ${exit_code} -eq 0 ]]; then
        log_info "Tool completed successfully in ${duration}s"
    else
        log_error "Tool failed with exit code ${exit_code} after ${duration}s"
    fi
    
    return ${exit_code}
}

# ===========================
# CLEANUP
# ===========================
cleanup() {
    log_debug "Performing cleanup..."
    # Deactivate virtual environment
    deactivate 2>/dev/null || true
    # Clean up temp files, connections, etc.
}
trap cleanup EXIT

# ===========================
# MAIN ENTRY POINT
# ===========================
main() {
    # Handle special commands
    case "${1:-}" in
        --health)
            health_check
            ;;
        --version)
            echo "1.0.0"
            exit 0
            ;;
        --help)
            cat <<EOF
Tool: ${TOOL_NAME}
Description: Template for creating new tools

Usage: ./run.sh [OPTIONS] [COMMAND]

Options:
  --health      Run health check
  --version     Show version
  --help        Show this help message

Parameters:
  --example_param   An example parameter
  --count          Number of iterations (default: 1)

Examples:
  ./run.sh --example_param="hello" --count=5
  ./run.sh --health

EOF
            exit 0
            ;;
    esac
    
    # Setup and execute
    setup_environment
    execute_tool "$@"
}

main "$@"
