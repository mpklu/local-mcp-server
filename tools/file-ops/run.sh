#!/bin/bash
# Tool: file-ops
# Description: File operations utilities for reading, writing, and listing files
#
# @param function: The function to execute (type: string, required: true)
# @param filepath: Path to the file (type: string, required: false)
# @param content: Content to write (type: string, required: false)
# @param directory: Directory path (type: string, required: false)

set -euo pipefail

# Configuration
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_NAME="file-ops"
LOG_PREFIX="[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] [${TOOL_NAME}]"

# Logging helpers
log_info() { echo "${LOG_PREFIX} INFO: $*" >&2; }
log_error() { echo "${LOG_PREFIX} ERROR: $*" >&2; }
log_debug() { [[ "${DEBUG:-0}" == "1" ]] && echo "${LOG_PREFIX} DEBUG: $*" >&2 || true; }

# Environment setup
setup_environment() {
    log_info "Setting up environment..."
    
    if [[ -f "${TOOL_DIR}/requirements.txt" ]]; then
        VENV_DIR="${TOOL_DIR}/.venv"
        
        if [[ ! -d "${VENV_DIR}" ]]; then
            log_info "Creating virtual environment..."
            python3 -m venv "${VENV_DIR}"
            source "${VENV_DIR}/bin/activate"
            pip install --quiet --upgrade pip
            pip install --quiet -r "${TOOL_DIR}/requirements.txt"
            log_info "Installed dependencies"
        else
            source "${VENV_DIR}/bin/activate"
        fi
    fi
    
    log_info "Environment ready"
}

# Tool execution
execute_tool() {
    log_info "Executing file-ops with args: $*"
    
    python3 "${TOOL_DIR}/manager.py" "$@"
    
    local exit_code=$?
    
    if [[ ${exit_code} -eq 0 ]]; then
        log_info "Tool completed successfully"
    else
        log_error "Tool failed with exit code ${exit_code}"
    fi
    
    return ${exit_code}
}

# Cleanup
cleanup() {
    log_debug "Performing cleanup..."
    deactivate 2>/dev/null || true
}
trap cleanup EXIT

# Main
main() {
    case "${1:-}" in
        --health)
            log_info "Health check passed"
            exit 0
            ;;
        --version)
            echo "1.0.0"
            exit 0
            ;;
    esac
    
    setup_environment
    execute_tool "$@"
}

main "$@"
