# Creating Tools for Local MCP Server

## Tool Structure Convention

All tools in the Local MCP Server follow a consistent structure for easy integration and management.

## Required Files

### 1. Entry Point: `run.py`
Every tool **must** have a `run.py` file as the primary entry point. This file should:
- Import functions from the main module
- Set up the Fire CLI interface
- Be executable (`chmod +x run.py`)

```python
#!/usr/bin/env python3
"""
Entry point for your-tool-name.
"""

if __name__ == "__main__":
    from your_module import *
    import fire
    fire.Fire()
```

### 2. Main Module
The core functionality should be in a descriptively named module:
- `info.py` for system information tools
- `client.py` for HTTP/API tools  
- `processor.py` for text processing tools
- `manager.py` for file operation tools

### 3. Dependencies: `requirements.txt`
List all Python dependencies:
```txt
fire
requests
pandas
```

### 4. Documentation: `README.md`
Comprehensive documentation including:
- Tool purpose and features
- Usage examples
- Parameter descriptions
- Installation instructions

## Tool Directory Structure

```
tools/your-tool-name/
├── run.py              # Entry point (required)
├── your_module.py      # Main functionality
├── requirements.txt    # Dependencies
├── README.md          # Documentation
└── test.py            # Tests (optional)
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

## Execution Flow

1. **MCP Server** calls `run.py` in tool directory
2. **run.py** imports functions and starts Fire interface
3. **Fire** parses arguments and calls appropriate function
4. **Function** executes and returns structured result
5. **Result** returned to MCP client (Claude, etc.)

## Best Practices

### Function Design
- Use descriptive function names
- Provide comprehensive docstrings
- Return JSON-structured data when possible
- Handle errors gracefully with try/catch blocks

### Parameter Validation
- Validate input parameters
- Provide helpful error messages
- Use type hints for clarity
- Set sensible default values

### Output Format
- Return JSON for structured data
- Include metadata (timestamps, execution info)
- Provide human-readable previews for large data
- Use consistent error message format

## Testing Your Tool

### Manual Testing
```bash
# Navigate to tool directory
cd tools/your-tool-name/

# Test directly
python run.py function_name param1 param2

# Test with named parameters
python run.py function_name --param1=value1 --param2=value2
```

### Web Interface Testing
1. Start the development server: `cd web-interface && ./start_dev.sh`
2. Open http://localhost:3000
3. Configure and test your tool via the web interface
4. Verify parameter validation and error handling

### MCP Integration Testing  
1. Configure tool in the MCP server
2. Test via Claude Desktop or other MCP client
3. Verify tool appears in available tools list
4. Test execution and result formatting

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

## Integration with Web Interface

The web interface provides:
- **Visual Configuration**: Form-based parameter input
- **Dependency Management**: One-click dependency installation
- **Execution Monitoring**: Real-time progress and status
- **Result Viewer**: Formatted output with export options
- **Error Handling**: User-friendly error messages and recovery

Tools are automatically discovered and configured based on:
- Function signatures from Fire analysis
- Parameter types and defaults
- Docstring descriptions
- Requirements.txt dependencies

## Troubleshooting

### Tool Not Detected
- Ensure `run.py` exists and is executable
- Check that Fire interface is properly configured
- Verify tool directory structure
- Run discovery scan in web interface

### Execution Errors
- Test tool manually: `python run.py function_name params`
- Check dependencies are installed
- Verify file paths and permissions
- Review server logs for detailed error information

### Parameter Issues
- Use Fire's built-in help: `python run.py function_name -- --help`
- Check parameter types and validation
- Test with web interface parameter editor
- Verify JSON parameter syntax