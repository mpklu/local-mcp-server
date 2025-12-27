# Structured Output Guide for Tools

## Overview

As of December 2025, the Local MCP Server supports **structured output** from tools. Tools can now emit JSON to stdout, which will be automatically parsed and returned to AI assistants in a structured format.

## Benefits

- **Better AI Integration**: AI receives structured data instead of plain text strings
- **Type Safety**: Clients can parse and validate output programmatically
- **Richer Metadata**: Include execution time, status codes, and additional context
- **Backward Compatible**: Plain text output still works for existing tools

## How It Works

1. **Tool emits JSON** to stdout
2. **Server detects and parses** the JSON automatically
3. **Structured response** is returned to the AI with metadata
4. **Fallback**: If output isn't valid JSON, it's returned as plain text

## For Tool Authors

### Python Example

```python
import json

def list_files(directory="."):
    """List files in a directory with structured output."""
    import os
    
    files = []
    for item in os.listdir(directory):
        files.append({
            "name": item,
            "size": os.path.getsize(os.path.join(directory, item)),
            "is_dir": os.path.isdir(os.path.join(directory, item))
        })
    
    # Emit structured JSON output
    result = {
        "directory": directory,
        "total_items": len(files),
        "files": files
    }
    
    print(json.dumps(result))
```

### Shell Script Example

```bash
#!/bin/bash

# Simple JSON output
echo '{"status": "success", "message": "Operation completed", "count": 5}'

# Or with jq for complex structures
jq -n \
  --arg dir "$1" \
  --argjson count 3 \
  '{
    directory: $dir,
    total_items: $count,
    files: ["file1.txt", "file2.txt", "file3.txt"]
  }'
```

### Error Handling

You can also emit structured errors:

```python
import json
import sys

try:
    # Tool logic here
    result = {"status": "success", "data": {...}}
    print(json.dumps(result))
except FileNotFoundError as e:
    error = {
        "status": "error",
        "error": {
            "code": "NOT_FOUND",
            "message": str(e)
        }
    }
    print(json.dumps(error), file=sys.stderr)
    sys.exit(1)
```

## Response Format

When your tool emits JSON, the server wraps it in a structured response:

```json
{
  "status": "success",
  "data": {
    // Your tool's JSON output here
    "directory": "/tmp",
    "total_items": 5,
    "files": [...]
  },
  "format": "json",
  "metadata": {
    "execution_time": 0.15,
    "exit_code": 0
  }
}
```

## Best Practices

1. **Use consistent field names**: `status`, `data`, `error`, `message`
2. **Include useful metadata**: counts, timestamps, version info
3. **Validate your JSON**: Use `json.dumps()` in Python or `jq` in shell
4. **Handle errors gracefully**: Emit structured errors when possible
5. **Document your schema**: Comment what fields your tool returns

## Migration Guide

Existing tools don't need changes! Plain text output continues to work:

- **JSON output** → Automatically parsed and structured
- **Plain text output** → Returned as-is for backward compatibility

To upgrade a tool:

1. Modify your tool to emit JSON instead of plain text
2. Test with `./run.sh` to verify valid JSON
3. No server changes needed - it auto-detects JSON

## Examples in the Repository

See these tools for reference implementations:

- `tools/file-ops/manager.py` - Already emits JSON
- `tools/http-client/client.py` - Already emits JSON
- `tools/system-info/info.py` - Already emits JSON

## Testing Your JSON Output

```bash
# Test your tool locally
./run.sh list_files --directory=/tmp | jq .

# If jq parses it successfully, the server will too!
```

## Future Enhancements

In future versions, we plan to support:

- Output schema validation (see `SCHEMA_DRIVEN_OUTPUT.md`)
- Auto-generated TypeScript types from schemas
- UI rendering based on output structure
- Streaming output for long-running operations

---

**Status**: Implemented (December 27, 2025)  
**Version**: 1.0.0  
**Related**: See `TOOL_DRIVEN_OUTPUT_PLAN.md` for implementation details
