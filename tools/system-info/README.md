# System Information Tool

This tool provides comprehensive system information including:

- Operating system details
- CPU specifications and usage
- Memory statistics  
- Disk usage for any path
- Network interface information

**Note**: This tool has been converted from Python Fire to **argparse** to demonstrate 
both argument parsing approaches in the Local MCP Server system.

## Usage Examples

### Get complete system information
```bash
python run.py get_system_info
```

### Check disk usage for a specific path
```bash
python run.py get_disk_usage --path /home/user
python run.py get_disk_usage "C:\Users"  # Windows
```

### Get network interface details
```bash
python run.py get_network_info
```

## Argparse vs Fire

This tool demonstrates **argparse** usage, while other tools in the system use **Python Fire**:

- **Argparse**: More explicit, traditional Python CLI approach
- **Fire**: More automatic, function-to-CLI mapping
- **Both work seamlessly** with the Local MCP Server's universal argument system!

## Features Demonstrated

- **Simple Execution**: No parameters required for basic system info
- **Parameter Handling**: Optional path parameter with validation
- **JSON Output**: Structured, parseable responses
- **Error Handling**: Graceful error messages
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Dependencies

Install dependencies with:
```bash
pip install -r requirements.txt
```
