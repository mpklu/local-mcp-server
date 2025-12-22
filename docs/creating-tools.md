# Creating Tools for Local MCP Server

## Universal Entry Point Architecture

Local MCP Server uses a **standardized `run.sh` entry point** for all tools. This provides consistency, better dependency management, and support for any programming language or runtime.

## Quick Start

### 1. Create Tool Directory
```bash
cd tools/
mkdir my-awesome-tool
cd my-awesome-tool
```

### 2. Create run.sh Entry Point (REQUIRED)
Every tool **MUST** have a `run.sh` file that serves as the universal entry point:

```bash
cp ../TEMPLATE/run.sh ./run.sh
chmod +x run.sh
```

### 3. Create Your Tool Logic
Add your actual tool implementation:
- `main.py` for Python tools
- `script.sh` for shell tools
- `index.js` for Node.js tools
- Or any executable/binary

### 4. Auto-Generate Configuration
```bash
cd ../../server
python discover_tools.py
python build_tools.py
```

### 5. Configure via Web Interface (Optional)
- Open http://localhost:3000
- Your tool will appear in the tool list
- Configure parameters, metadata, and settings

## Tool Structure

Each tool follows this standardized structure:
```
tools/your-tool-name/
├── run.sh              # Universal entry point (REQUIRED)
├── main.py             # Your tool logic (Python example)
├── requirements.txt    # Dependencies (optional)
├── .venv/              # Tool-managed virtual environment
├── README.md           # Documentation (recommended)
└── config.yaml         # Tool config (optional)
```

## The run.sh Pattern

### Why run.sh?

The `run.sh` wrapper provides:
1. **Environment Setup**: Creates venvs, installs dependencies
2. **Execution**: Runs your actual tool with proper environment
3. **Logging**: Standardized logging with timestamps
4. **Cleanup**: Proper resource cleanup
5. **Health Checks**: Built-in health check support

### Template Structure

```bash
#!/bin/bash
# Tool: your-tool-name
# Description: What your tool does
#
# @param param1: Description (type: string, required: true)
# @param param2: Description (type: integer, required: false)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_NAME="your-tool-name"

# Logging helpers
log_info() { echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] [${TOOL_NAME}] INFO: $*" >&2; }
log_error() { echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] [${TOOL_NAME}] ERROR: $*" >&2; }

# 1. Environment Setup
setup_environment() {
    log_info "Setting up environment..."
    
    # Python tools: Create virtual environment
    if [[ -f "${TOOL_DIR}/requirements.txt" ]]; then
        VENV_DIR="${TOOL_DIR}/.venv"
        if [[ ! -d "${VENV_DIR}" ]]; then
            python3 -m venv "${VENV_DIR}"
            source "${VENV_DIR}/bin/activate"
            pip install -r "${TOOL_DIR}/requirements.txt"
        else
            source "${VENV_DIR}/bin/activate"
        fi
    fi
    
    log_info "Environment ready"
}

# 2. Execution
execute_tool() {
    log_info "Executing tool with args: $*"
    
    # Run your tool - examples:
    python3 "${TOOL_DIR}/main.py" "$@"        # Python
    # bash "${TOOL_DIR}/script.sh" "$@"       # Shell
    # node "${TOOL_DIR}/index.js" "$@"        # Node.js
    # "${TOOL_DIR}/bin/tool" "$@"             # Binary
    
    local exit_code=$?
    [[ ${exit_code} -eq 0 ]] && log_info "Success" || log_error "Failed"
    return ${exit_code}
}

# 3. Cleanup
cleanup() {
    deactivate 2>/dev/null || true
}
trap cleanup EXIT

# Main
main() {
    setup_environment
    execute_tool "$@"
}

## Language-Specific Examples

### Python Tool
```python
# tools/my-python-tool/main.py
import fire
import json

def process_data(input_file, output_format="json"):
    """Process data from input file.
    
    Args:
        input_file: Path to input file
        output_format: Output format (json|csv)
    """
    # Your logic here
    result = {"status": "success", "format": output_format}
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    fire.Fire(process_data)
```

### Node.js Tool
```javascript
// tools/my-node-tool/index.js
#!/usr/bin/env node
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

function processData(inputFile, outputFormat = 'json') {
  // Your logic here
  console.log(JSON.stringify({
    status: 'success',
    format: outputFormat
  }, null, 2));
}

const argv = yargs(hideBin(process.argv))
  .command('process', 'Process data', {
    inputFile: { type: 'string', demandOption: true },
    outputFormat: { type: 'string', default: 'json' }
  })
  .parse();

processData(argv.inputFile, argv.outputFormat);
```

### Go Binary Tool
```go
// tools/my-go-tool/main.go
package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"
)

func main() {
    inputFile := flag.String("input", "", "Input file path")
    outputFormat := flag.String("format", "json", "Output format")
    flag.Parse()
    
    result := map[string]string{
        "status": "success",
        "format": *outputFormat,
    }
    
    json.NewEncoder(os.Stdout).Encode(result)
}
```

Then compile and reference in run.sh:
```bash
# tools/my-go-tool/run.sh
execute_tool() {
    "${TOOL_DIR}/bin/my-tool" "$@"
}
```

## Parameter Documentation Format

Document parameters in run.sh header comments for auto-discovery:

```bash
#!/bin/bash
# Tool: my-tool
# Description: Short description of what the tool does
#
# @param input_file: Path to input file (type: string, required: true)
# @param output_format: Output format (type: string, required: false, default: json)
# @param verbose: Enable verbose logging (type: boolean, required: false)
# @param count: Number of iterations (type: integer, required: false, default: 1)
```

## Best Practices

### 1. Environment Management
- **Tool-owned venvs**: Each tool creates and manages its own `.venv/`
- **Dependency isolation**: Use `requirements.txt`, `package.json`, etc.
- **Check system deps**: Validate required system tools in `setup_environment()`

### 2. Execution Patterns
- **Pass-through arguments**: Let `run.sh` forward args to your tool
- **Structured output**: Return JSON for better AI integration
- **Error handling**: Use proper exit codes (0 = success, non-zero = failure)

### 3. Logging Standards
- **Use log helpers**: `log_info()`, `log_error()` for consistent formatting
- **Stderr for logs**: Write logs to stderr, data to stdout
- **Timestamps**: Include UTC timestamps in all log messages

### 4. Health Checks
```bash
# Support --health flag
if [[ "${1:-}" == "--health" ]]; then
    # Check dependencies
    [[ -f "${TOOL_DIR}/.venv/bin/python" ]] || exit 1
    # Check connectivity, files, etc.
    exit 0
fi
```

## Testing Your Tool

### 1. Manual Testing
```bash
# Navigate to tool directory
cd tools/your-tool-name/

# Test entry point
./run.sh function_name param1 param2

# Test with named parameters
./run.sh --input="test.txt" --format="csv"

# Test health check
./run.sh --health
```

### 2. Discovery Testing  
```bash
cd server

# List discovered tools
python discover_tools.py --list

# Regenerate configs
python discover_tools.py

# Check compilation
python build_tools.py
```

### 3. Web Interface Testing
1. Start development server: `cd web-interface && ./start_dev.sh`
2. Open http://localhost:3000
3. Verify your tool appears in the tool list
4. Configure parameters and metadata
5. Use "Test Tool" feature to validate functionality

### 4. MCP Integration Testing
```bash
# Start server with your preferred host adapter
cd server
./start_server.sh --host claude-desktop

# In Claude Desktop, verify:
# - Tool appears in available tools
# - Parameters are correctly parsed
# - Results are properly formatted
```

## Common Patterns

### File Operations
```python
def process_file(file_path, output_format="json"):
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        
        # Process file
        result = {"success": True, "data": processed_data}
        return json.dumps(result, indent=2)
    except Exception as e:
        return {"error": str(e)}
```

### HTTP Requests
```python
def api_call(url, method="GET", headers=None):
    try:
        response = requests.request(method, url, headers=headers)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.headers.get("content-type") == "application/json" else response.text
        }
    except Exception as e:
        return {"error": str(e)}
```

### Long-Running Tasks
```python
def long_task(duration=10):
    try:
        for i in range(duration):
            print(f"Progress: {i+1}/{duration}")
            time.sleep(1)
        
        return {"completed": True, "duration": duration}
    except KeyboardInterrupt:
        return {"error": "Task interrupted by user"}
```

## Web Interface Integration

### Auto-Configuration
Tools are automatically detected and configured based on:
- **Directory structure**: Each folder in `tools/` becomes a tool
- **Entry point analysis**: Fire CLI inspection for parameters and functions
- **Docstring extraction**: Function descriptions become tool descriptions
- **Dependency detection**: `requirements.txt` automatically parsed

### Configuration Management
The web interface provides:
- **Visual Configuration**: Form-based parameter editing and metadata management
- **Dependency Management**: Automatic virtual environment setup and package installation
- **Real-time Testing**: Built-in tool testing with parameter validation
- **Status Monitoring**: Live execution status and error reporting
- **Bulk Operations**: Mass enable/disable, configuration import/export

### Discovery Integration
- **Auto-refresh**: New tools automatically appear after discovery scan
- **Config sync**: Changes sync between individual configs and compiled config
- **Validation**: Real-time validation of configurations and dependencies
- **Backup**: Automatic backup of configurations before changes

## Troubleshooting

### Tool Not Detected
1. **Check directory structure**: Ensure tool is in its own folder under `tools/`
2. **Verify entry point**: Confirm `run.py`, `run.sh`, or `run` exists and is executable
3. **Run discovery**: Execute `python server/discover_tools.py --list`
4. **Check permissions**: Ensure files are readable and executable
5. **Validate syntax**: Test entry point manually for syntax errors

### Configuration Issues
1. **Regenerate configs**: Run `python server/discover_tools.py` to recreate configs
2. **Check compilation**: Run `python server/build_tools.py` to verify compilation
3. **Validate JSON**: Check individual configs in `server/config/tools/` for syntax errors
4. **Review logs**: Check server logs for detailed configuration error messages

### Runtime Errors
1. **Test manually**: Run `python tools/your-tool/run.py function_name params`
2. **Check dependencies**: Verify `requirements.txt` and virtual environment setup
3. **Validate parameters**: Use Fire's help: `python run.py -- --help`
4. **Review output**: Ensure tool returns JSON-compatible results
5. **Check isolation**: Verify tool works in isolation without server context

### Integration Problems
1. **Server restart**: Restart MCP server after configuration changes
2. **Host adapter**: Verify correct host adapter for your MCP client
3. **Path issues**: Check that all file paths are absolute or relative to tool directory
4. **Memory/timeout**: Adjust server settings for resource-intensive tools