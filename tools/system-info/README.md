# System Information Tool

This tool provides comprehensive system information including:

- Operating system details
- CPU specifications and usage
- Memory statistics  
- Disk usage for any path
- Network interface information

## Usage Examples

### Get complete system information
```bash
python info.py get_system_info
```

### Check disk usage for a specific path
```bash
python info.py get_disk_usage /home/user
python info.py get_disk_usage "C:\Users"  # Windows
```

### Get network interface details
```bash
python info.py get_network_info
```

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
