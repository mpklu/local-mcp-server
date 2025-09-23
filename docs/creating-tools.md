# Creating Tools for Local MCP Server

## Directory-Based Tool Architecture

Local MCP Server uses a directory-based approach where each tool lives in its own folder under `tools/`. This provides better organization, dependency isolation, and automatic discovery.

## Quick Start

### 1. Create Tool Directory
```bash
cd tools/
mkdir my-awesome-tool
cd my-awesome-tool
```

### 2. Create Entry Point
Every tool **must** have one of these entry points (in order of precedence):
- `run.py` (Python script - most common)
- `run.sh` (Shell script)  
- `run` (Executable file)

### 3. Auto-Generate Configuration
```bash
cd ../../server
python discover_tools.py
python build_tools.py
```

### 4. Configure via Web Interface
- Open http://localhost:3000
- Your tool will appear in the tool list
- Configure parameters, metadata, and settings

## Directory Structure

Each tool follows this structure:
```
tools/your-tool-name/
├── run.py              # Entry point (required)
├── your_module.py      # Main functionality (optional)
├── requirements.txt    # Dependencies (optional)
├── README.md          # Documentation (recommended)
└── test.py            # Tests (optional)
```

## Entry Point Patterns

### Python Tools (Recommended)
```python
#!/usr/bin/env python3
"""
Entry point for your-tool-name.
Automatically discovered by Local MCP Server.
"""

if __name__ == "__main__":
    from your_module import main_function
    import fire
    fire.Fire(main_function)
```

### Shell Script Tools
```bash
#!/bin/bash
# tools/my-tool/run.sh

set -e

function main_function() {
    local param1="$1"
    local param2="${2:-default_value}"
    
    echo "Processing with $param1 and $param2"
    # Your logic here
}

# Allow direct function calls
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    "$@"
fi
```

### Compiled Tools
```bash
#!/bin/bash
# tools/my-tool/run

# Wrapper for compiled binary
exec "./my-compiled-tool" "$@"
```

## Python Fire Integration

All tools use Python Fire for CLI interface generation:

```python
import fire

def your_function(param1, param2="default"):
    """Your function documentation."""
    return result

if __name__ == "__main__":
    fire.Fire()
```

### Parameter Handling
- **Positional Arguments**: `python run.py value1 value2`
- **Named Arguments**: `python run.py --param1=value1 --param2=value2` 
- **Boolean Flags**: `python run.py --enable_feature`
- **JSON Objects**: `python run.py --config='{"key": "value"}'`

## Discovery and Configuration Pipeline

### Auto-Discovery Process
1. **Directory Scan**: Discovery system finds all folders in `tools/`
2. **Entry Point Detection**: Locates `run.py`, `run.sh`, or `run` in each folder
3. **Config Generation**: Creates individual config in `config/tools/{tool-name}.json`
4. **Compilation**: `build_tools.py` compiles individual configs into `tools.json`
5. **Server Integration**: MCP server loads compiled configuration

### Configuration Flow
```
tools/my-tool/          →  config/tools/my-tool.json  →  config/tools.json  →  MCP Server
(directory + entry)        (individual config)           (compiled config)      (runtime)
```

## Best Practices

### Directory Organization
- **One tool per directory**: Keep tools isolated and focused
- **Descriptive names**: Use clear, hyphen-separated names (`text-processor`, `api-client`)
- **Standard entry points**: Stick to `run.py` for consistency
- **Complete documentation**: Include README.md with examples

### Function Design
- **Single responsibility**: Each tool should have a clear, focused purpose
- **Comprehensive docstrings**: Used for auto-generated MCP tool descriptions
- **JSON output**: Return structured data for better AI integration
- **Error handling**: Graceful failure with informative messages

### Configuration Management
- **Auto-discovery friendly**: Design tools to work with minimal configuration
- **Parameter validation**: Validate inputs and provide helpful error messages  
- **Metadata-rich**: Use docstrings and type hints for better auto-configuration
- **Dependency specification**: Always include `requirements.txt` for Python tools

## Testing Your Tool

### 1. Manual Testing
```bash
# Navigate to tool directory
cd tools/your-tool-name/

# Test entry point directly
python run.py function_name param1 param2

# Test with named parameters
python run.py function_name --param1=value1 --param2=value2

# Test Fire help system
python run.py -- --help
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