"""
Utility functions for Local MCP Server.
"""

import hashlib
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def hash_file_content(file_path: Path) -> str:
    """Generate a hash of file content for change detection."""
    try:
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()
    except Exception as e:
        logger.warning(f"Error hashing file {file_path}: {e}")
        return ""


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Replace unsafe characters
    safe_chars = []
    for char in name:
        if char.isalnum() or char in '-_':
            safe_chars.append(char)
        elif char in ' /\\':
            safe_chars.append('_')
    
    result = ''.join(safe_chars)
    
    # Ensure it's not empty and doesn't start with special chars
    if not result or result.startswith(('.', '_')):
        result = f"tool_{result}"
    
    return result


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def parse_script_shebang(script_path: Path) -> str:
    """Parse script shebang to determine interpreter."""
    try:
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        
        if first_line.startswith('#!'):
            shebang = first_line[2:].strip()
            if 'python' in shebang:
                return 'python'
            elif any(shell in shebang for shell in ['bash', 'sh', 'zsh']):
                return 'shell'
        
        # Fallback to extension
        if script_path.suffix == '.py':
            return 'python'
        
        return 'shell'
    
    except Exception as e:
        logger.debug(f"Error parsing shebang for {script_path}: {e}")
        return 'unknown'


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_script_arguments(arguments: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate script arguments against schema and return any errors."""
    errors = []
    
    # Check required arguments
    required = schema.get('required', [])
    for req_arg in required:
        if req_arg not in arguments:
            errors.append(f"Missing required argument: {req_arg}")
    
    # Check argument types (simplified validation)
    properties = schema.get('properties', {})
    for arg_name, arg_value in arguments.items():
        if arg_name in properties:
            expected_type = properties[arg_name].get('type', 'string')
            if expected_type == 'boolean' and not isinstance(arg_value, bool):
                errors.append(f"Argument {arg_name} must be boolean")
            elif expected_type == 'number' and not isinstance(arg_value, (int, float)):
                errors.append(f"Argument {arg_name} must be a number")
            elif expected_type == 'integer' and not isinstance(arg_value, int):
                errors.append(f"Argument {arg_name} must be an integer")
    
    return errors
