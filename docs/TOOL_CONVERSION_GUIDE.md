# Tool Creation & Conversion Guide

**Quick Reference for Developers and AI Agents**

This guide provides everything you need to create or convert tools for the Local MCP Server. For detailed documentation, see [creating-tools.md](creating-tools.md).

---

## 🎯 Single-Function Tool Principle

**IMPORTANT**: MCP systems work best when each tool performs a **single, well-defined function**.

### Why Single-Function Tools?

1. **Better Discoverability**: AI agents can easily understand what each tool does
2. **Clearer Parameters**: Each tool has only the parameters it needs
3. **Simpler Documentation**: Each tool's purpose is immediately clear
4. **Easier Testing**: Single-function tools are easier to test and validate
5. **Better Error Handling**: Errors are specific to one operation

### Multi-Function vs Single-Function

❌ **Avoid Multi-Function Tools**:
```bash
# @param function: The function to execute: list, read, write, delete (type: string, required: true)
# @param filepath: Path to file (type: string, required: false)
# @param content: Content to write (type: string, required: false)
```
This creates confusion - which parameters are needed for which function?

✅ **Prefer Separate Single-Function Tools**:
```
tools/file-list/      # Lists files in directory
tools/file-read/      # Reads file content
tools/file-write/     # Writes content to file
tools/file-delete/    # Deletes a file
```
Each tool has clear, specific parameters for its one task.

### Converting Multi-Function Tools

If you have a tool with multiple functions (e.g., using Python Fire with multiple methods), create separate tools:

1. Create a directory for each function
2. Share the common code (copy or symlink `manager.py`)
3. Create a specific `run.sh` for each that calls only one function
4. Document only the relevant parameters in each `run.sh`

**Example**: See `mp-list-databases`, `mp-show-tables`, `mp-search-column`, `mp-table-sizes`, and `mp-largest-tables` - five separate tools that share the same underlying `manager.py` but each expose one function with specific parameters.

---

## Quick Checklist

Before moving a tool to production:

- [ ] **Single Function**: Tool performs ONE well-defined operation
- [ ] **File Structure**: Has `run.sh`, `manager.py`/`main.py`, `requirements.txt`, `README.md`
- [ ] **run.sh Header**: Contains `@param` annotations for all parameters
- [ ] **JSON Output**: Tool emits structured JSON to stdout
- [ ] **Health Check**: Responds to `--health` flag
- [ ] **Testing**: All functions tested manually with `./run.sh`
- [ ] **Documentation**: README explains usage with examples
- [ ] **Cleanup**: No `__pycache__`, old entry points, or unnecessary files

---

## Required File Structure

```
tools/your-tool/
├── run.sh              # Universal entry point (REQUIRED)
├── manager.py          # Python Fire interface (REQUIRED for Python tools)
├── requirements.txt    # Dependencies (REQUIRED if using external packages)
├── README.md           # Documentation (STRONGLY RECOMMENDED)
├── .venv/              # Virtual environment (auto-created)
└── test.py             # Test script (optional but recommended)
```

**Essential Files:**
1. **run.sh** - Bash entry point that handles environment setup and execution
2. **manager.py** - Python Fire-based interface with your tool's functions
3. **requirements.txt** - Python dependencies including `fire>=0.7.1`

---

## Step 1: Create run.sh Entry Point

**For Single-Function Tools** (recommended):

```bash
#!/bin/bash
# Tool: list-databases
# Description: List all databases on the MySQL server
#
# ===========================
# PARAMETER DOCUMENTATION (REQUIRED)
# ===========================
# This tool has no parameters - it lists all available databases
#
# ===========================
# OUTPUT FORMAT
# ===========================
# This tool outputs structured JSON for easy AI parsing.

set -euo pipefail

# Configuration
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_NAME="$(basename "${TOOL_DIR}")"
LOG_PREFIX="[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] [${TOOL_NAME}]"

# Logging helpers
log_info() { echo "${LOG_PREFIX} INFO: $*" >&2; }
log_error() { echo "${LOG_PREFIX} ERROR: $*" >&2; }

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
        else
            source "${VENV_DIR}/bin/activate"
        fi
    fi
    
    log_info "Environment ready"
}

# Tool execution - calls specific function directly
execute_tool() {
    log_info "Executing tool with args: $*"
    python3 "${TOOL_DIR}/manager.py" list_databases "$@"
}

# Health check
health_check() {
    echo '{"status":"healthy","tool":"'"${TOOL_NAME}"'"}'
    return 0
}

# Main execution
main() {
    case "${1:-}" in
        health)
            health_check
            ;;
        *)
            setup_environment
            execute_tool "$@"
            ;;
    esac
}

main "$@"
```

**Or for tools with parameters**:

```bash
#!/bin/bash
# Tool: search-tables-by-column
# Description: Search for tables containing a specific column name
#
# ===========================
# PARAMETER DOCUMENTATION (REQUIRED)
# ===========================
# @param database: Database name to search in (type: string, required: false, default: macpractice)
# @param column_name: Column name to search for (type: string, required: true)
#
# Supported types: string, integer, number, boolean, array, object
# Format: @param name: description (type: TYPE, required: BOOL, default: VALUE)
#
# ===========================
# OUTPUT FORMAT
# ===========================
# This tool outputs structured JSON for easy AI parsing.

set -euo pipefail

# Configuration
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_NAME="$(basename "${TOOL_DIR}")"
LOG_PREFIX="[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] [${TOOL_NAME}]"

# Logging helpers
log_info() { echo "${LOG_PREFIX} INFO: $*" >&2; }
log_error() { echo "${LOG_PREFIX} ERROR: $*" >&2; }

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
        else
            source "${VENV_DIR}/bin/activate"
        fi
    fi
    
    log_info "Environment ready"
}

# Health check
health_check() {
    log_info "Running health check..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi
    
    if [[ ! -f "${TOOL_DIR}/manager.py" ]]; then
        log_error "manager.py not found"
        exit 1
    fi
    
    log_info "Health check passed"
    exit 0
}

# Tool execution - calls specific function with parameters
execute_tool() {
    log_info "Executing tool with args: $*"
    python3 "${TOOL_DIR}/manager.py" search_tables_by_column "$@"
}

# Health check
health_check() {
    echo '{"status":"healthy","tool":"'"${TOOL_NAME}"'"}'
    return 0
}

# Main execution
main() {
    case "${1:-}" in
        health)
            health_check
            ;;
        *)
            setup_environment
            execute_tool "$@"
            ;;
    esac
}

main "$@"
```

**Key sections to customize:**
- Lines 2-3: Tool name and clear, specific description
- Lines 7-9: `@param` annotations - only for parameters this specific tool needs
- Line 141: Call the specific function directly (e.g., `search_tables_by_column` not a generic function dispatcher)

### ⚠️ Avoid Function Parameter Pattern

**Don't do this**:
```bash
# @param function: The function to execute (type: string, required: true)
execute_tool() {
    python3 "${TOOL_DIR}/manager.py" "$@"  # Generic - routes to multiple functions
}
```

**Instead, create separate tools**:
```bash
# In tools/search-by-column/run.sh
execute_tool() {
    python3 "${TOOL_DIR}/manager.py" search_tables_by_column "$@"  # Specific function
}

# In tools/show-tables/run.sh  
execute_tool() {
    python3 "${TOOL_DIR}/manager.py" show_table_count "$@"  # Different specific function
}
```

---

## Step 2: Document Parameters with @param

Each parameter **MUST** be documented in the run.sh header. Since each tool performs a single function, you only document the parameters relevant to that specific operation.

**Single-Function Example** (no parameters):
```bash
# Tool: mp-list-databases
# Description: List all databases on the MySQL server
#
# ===========================
# PARAMETER DOCUMENTATION
# ===========================
# This tool has no parameters
```

**Single-Function Example** (with parameters):
```bash
# Tool: mp-search-column
# Description: Search for tables containing a specific column name
#
# ===========================
# PARAMETER DOCUMENTATION (REQUIRED)
# ===========================
# @param database: Database name to search in (type: string, required: false, default: macpractice)
# @param column_name: Column name to search for (type: string, required: true)
```

**Format Rules:**
- `@param name:` - Parameter name (must match function signature)
- `description` - Clear explanation of what it does
- `(type: TYPE, required: BOOL)` - Type and required flag
- `default: VALUE` - Optional default value

**Supported Types:**
- `string` - Text values
- `integer` - Whole numbers
- `number` - Floating point numbers
- `boolean` - true/false values
- `array` - Lists of values
- `object` - Complex objects

---

## Step 3: Create Python Fire Manager

This file exposes your tool's functions via Python Fire:

```python
#!/usr/bin/env python3
"""
Your Tool Name

Brief description of what this tool does.
"""

import json
import sys
from pathlib import Path

# Import your core library/logic
from your_module import YourToolClass


def function1(param1, param2="default"):
    """
    Brief description of function1.
    
    Args:
        param1 (str): Description of param1
        param2 (str): Description of param2
        
    Returns:
        JSON string with results
    """
    try:
        # Your tool logic here
        result = YourToolClass.do_something(param1, param2)
        
        # Return structured JSON
        output = {
            "status": "success",
            "data": result,
            "message": "Operation completed successfully"
        }
        
        print(json.dumps(output, indent=2))
        return 0
        
    except Exception as e:
        error_output = {
            "status": "error",
            "error": {
                "code": "ERROR_CODE",
                "message": str(e)
            }
        }
        print(json.dumps(error_output, indent=2), file=sys.stderr)
        return 1


def function2(param1):
    """Another function."""
    try:
        # Implementation
        output = {
            "status": "success",
            "data": {"result": "value"}
        }
        print(json.dumps(output, indent=2))
        return 0
    except Exception as e:
        error_output = {
            "status": "error",
            "error": {"code": "ERROR_CODE", "message": str(e)}
        }
        print(json.dumps(error_output, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    import fire
    fire.Fire({
        'function1': function1,
        'function2': function2,
    })
```

**Key Patterns:**
- Each function returns JSON via `print(json.dumps(...))`
- Errors go to stderr: `print(..., file=sys.stderr)`
- Use `fire.Fire()` with explicit function mapping
- Consistent error format with `code` and `message`

---

## Step 4: JSON Output Format

All tools should emit structured JSON:

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "result": "your actual data here"
  },
  "message": "Human-readable success message"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

**Best Practices:**
- Always use `json.dumps()` to ensure valid JSON
- Include a `status` field: "success" or "error"
- Put actual data in a `data` object
- Use consistent error codes (e.g., "NOT_FOUND", "INVALID_INPUT")

---

## Step 5: Create requirements.txt

List all Python dependencies:

```txt
fire>=0.7.1
# Add your tool's dependencies here
requests>=2.28.0
pydantic>=2.0.0
```

**Important:**
- `fire>=0.7.1` is **REQUIRED** for Python Fire-based tools
- Pin major versions to avoid breaking changes
- Keep dependencies minimal for faster installation

---

## Step 6: Testing Your Tool

### Manual Testing

```bash
# Navigate to tool directory
cd tools/your-tool/

# Test each function
./run.sh function1 --param1="test value" --param2="test"

# Verify JSON output with jq
./run.sh function1 --param1="test" | jq .

# Test health check
./run.sh --health

# Test help
./run.sh --help
```

### Validation Checklist

- [ ] All functions return valid JSON
- [ ] Error cases return error JSON with appropriate codes
- [ ] Health check passes
- [ ] No errors in logs (check stderr)
- [ ] Parameters are correctly parsed
- [ ] Output is readable and structured

---

## Step 7: Common Patterns

### File Operations
```python
def read_file(filepath):
    """Read file with error handling."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        return json.dumps({
            "status": "success",
            "data": {"content": content, "size": len(content)}
        })
    except FileNotFoundError:
        return json.dumps({
            "status": "error",
            "error": {"code": "NOT_FOUND", "message": f"File not found: {filepath}"}
        })
```

### Date Handling
```python
import datetime

def get_current_date():
    """Get current date."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    return json.dumps({
        "status": "success",
        "data": {"date": today}
    })
```

### HTTP Requests
```python
import requests

def fetch_url(url):
    """Fetch URL content."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return json.dumps({
            "status": "success",
            "data": {
                "content": response.text,
                "status_code": response.status_code
            }
        })
    except requests.RequestException as e:
        return json.dumps({
            "status": "error",
            "error": {"code": "HTTP_ERROR", "message": str(e)}
        })
```

---

## Conversion Workflow

For converting existing tools from `candidates/` to `tools/`:

### Step-by-Step Process

1. **Analyze existing tool**
   ```bash
   cd local_mcp_tools/candidates/your-tool/
   ls -la
   cat run.py  # Check current implementation
   ```

2. **Create new run.sh**
   - Copy from template
   - Add `@param` annotations
   - Update tool name and description

3. **Create manager.py**
   - Import existing logic
   - Wrap functions with JSON output
   - Add Python Fire interface

4. **Update requirements.txt**
   - Add `fire>=0.7.1`
   - Keep existing dependencies

5. **Test thoroughly**
   ```bash
   ./run.sh function1 --param="test"
   ./run.sh --health
   ```

6. **Clean up**
   ```bash
   rm -rf __pycache__
   rm old_entry_point.py  # If not needed
   ```

7. **Move to tools/**
   ```bash
   cp -r ../candidates/your-tool ../tools/
   cd ../tools/your-tool
   ./run.sh --health  # Verify in new location
   ```

8. **Create README.md** (see template below)

---

## README Template

```markdown
# Your Tool Name

Brief description of what this tool does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Usage

### Function 1

```bash
./run.sh function1 --param1="value" --param2="value"
```

Output:
```json
{
  "status": "success",
  "data": {
    "result": "value"
  }
}
```

### Function 2

```bash
./run.sh function2 --param="value"
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| param1 | string | Yes | - | Description |
| param2 | integer | No | 10 | Description |

## Error Codes

- `NOT_FOUND` - Resource not found
- `INVALID_INPUT` - Invalid parameter value
- `PROCESSING_ERROR` - Error during processing

## Examples

### Example 1
```bash
./run.sh function1 --param1="example"
```

## Dependencies

- Python 3.7+
- See requirements.txt for package dependencies
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'fire'"

**Fix:** Ensure `fire>=0.7.1` is in requirements.txt and run:
```bash
rm -rf .venv
./run.sh --health  # Will recreate venv and install deps
```

### "Permission denied" when running run.sh

**Fix:** Make it executable:
```bash
chmod +x run.sh
```

### JSON parsing errors

**Fix:** Use `json.dumps()` for all output:
```python
print(json.dumps({"key": "value"}))  # ✅ Correct
print('{"key": "value"}')             # ❌ Error-prone
```

### Tool not discovered by server

**Fix:** Check discovery:
```bash
cd ../../local-mcp-server/server
python discover_tools.py --list
```

---

## Quick Reference

### run.sh Template Location
```bash
cp tools/TEMPLATE/run.sh tools/your-tool/run.sh
```

### Test Command Pattern
```bash
./run.sh function_name --param1="value" --param2="value"
```

### JSON Validation
```bash
./run.sh function_name | jq .
# If jq parses it successfully, the server will too!
```

### Health Check
```bash
./run.sh --health
echo $?  # Should be 0
```

---

## Additional Resources

- **Full Documentation**: [creating-tools.md](creating-tools.md)
- **Structured Output Guide**: [STRUCTURED_OUTPUT.md](STRUCTURED_OUTPUT.md)
- **Example Tools**: Check `tools/demo-features/`, `tools/file-ops/`, `tools/http-client/`
- **Template**: `tools/TEMPLATE/` - Complete reference implementation

---

**Last Updated:** December 27, 2025  
**Version:** 1.0.0
