#!/usr/bin/env python3
"""
Test Tool for Structured Output

This tool tests both JSON and plain text output modes.
"""

import json
import sys


def json_output(message="Hello, World!"):
    """Return structured JSON output.
    
    Args:
        message (str): Message to include in output
        
    Returns:
        str: JSON formatted output
    """
    result = {
        "message": message,
        "type": "json_test",
        "count": 42,
        "items": ["apple", "banana", "cherry"]
    }
    print(json.dumps(result))


def plain_text_output(message="Hello, World!"):
    """Return plain text output.
    
    Args:
        message (str): Message to return
        
    Returns:
        str: Plain text output
    """
    print(f"Plain text message: {message}")
    print("This is NOT JSON")
    print("Multiple lines of plain text")


def error_json():
    """Test structured error output."""
    error = {
        "code": "TEST_ERROR",
        "message": "This is a test error",
        "details": {
            "reason": "Testing error handling"
        }
    }
    print(json.dumps({"error": error}), file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    import fire
    fire.Fire({
        "json_output": json_output,
        "plain_text": plain_text_output,
        "error_json": error_json
    })
