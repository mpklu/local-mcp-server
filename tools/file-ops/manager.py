#!/usr/bin/env python3
"""
File Operations Tool

Provides basic file and directory operations with safety checks.
This tool showcases multiple parameters, file I/O, and confirmation workflows.
"""

import json
import os
import fire
from pathlib import Path
from datetime import datetime
from typing import Optional, List


def list_files(directory=".", pattern="*", include_hidden=False):
    """List files in a directory with optional pattern matching.
    
    Args:
        directory (str): Directory to list files from (default: current directory)
        pattern (str): Glob pattern to match files (default: "*" for all files)
        include_hidden (bool): Include hidden files/directories (default: False)
        
    Returns:
        str: JSON formatted list of files with details
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        if not path.is_dir():
            return f"Error: '{directory}' is not a directory"
        
        files = []
        for item in path.glob(pattern):
            # Skip hidden files unless requested
            if not include_hidden and item.name.startswith('.'):
                continue
                
            stat = item.stat()
            file_info = {
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size_bytes": stat.st_size if item.is_file() else 0,
                "size_human": _format_bytes(stat.st_size) if item.is_file() else "N/A",
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:]
            }
            files.append(file_info)
        
        # Sort by name
        files.sort(key=lambda x: x["name"].lower())
        
        result = {
            "directory": str(path.resolve()),
            "pattern": pattern,
            "total_items": len(files),
            "files": files
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error listing files: {str(e)}"


def read_file(file_path, lines=None, encoding="utf-8"):
    """Read file contents with optional line limit.
    
    Args:
        file_path (str): Path to the file to read
        lines (int, optional): Maximum number of lines to read (None for all)
        encoding (str): File encoding (default: utf-8)
        
    Returns:
        str: File contents or error message
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"
        
        if not path.is_file():
            return f"Error: '{file_path}' is not a file"
        
        with open(path, 'r', encoding=encoding) as f:
            if lines is None:
                content = f.read()
            else:
                content_lines = []
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    content_lines.append(line)
                content = ''.join(content_lines)
        
        result = {
            "file_path": str(path.resolve()),
            "size_bytes": path.stat().st_size,
            "encoding": encoding,
            "lines_requested": lines,
            "content": content
        }
        
        return json.dumps(result, indent=2)
        
    except UnicodeDecodeError as e:
        return f"Error: Cannot decode file with {encoding} encoding: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def create_file(file_path, content="", overwrite=False):
    """Create a new file with content.
    
    Args:
        file_path (str): Path where the file should be created
        content (str): Content to write to the file (default: empty)
        overwrite (bool): Whether to overwrite existing files (default: False)
        
    Returns:
        str: Success message or error
    """
    try:
        path = Path(file_path)
        
        # Check if file exists and overwrite is not allowed
        if path.exists() and not overwrite:
            return f"Error: File '{file_path}' already exists. Use overwrite=True to replace it."
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = {
            "file_path": str(path.resolve()),
            "content_length": len(content),
            "created": datetime.now().isoformat(),
            "overwritten": path.existed if overwrite else False
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error creating file: {str(e)}"


def get_file_info(file_path):
    """Get detailed information about a file or directory.
    
    Args:
        file_path (str): Path to examine
        
    Returns:
        str: JSON formatted file information
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: Path '{file_path}' does not exist"
        
        stat = path.stat()
        
        info = {
            "path": str(path.resolve()),
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "size_bytes": stat.st_size,
            "size_human": _format_bytes(stat.st_size),
            "permissions": oct(stat.st_mode)[-3:],
            "owner_readable": os.access(path, os.R_OK),
            "owner_writable": os.access(path, os.W_OK),
            "owner_executable": os.access(path, os.X_OK),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat()
        }
        
        # Add file-specific info
        if path.is_file():
            info["extension"] = path.suffix
            info["stem"] = path.stem
            
        # Add directory-specific info
        elif path.is_dir():
            try:
                children = list(path.iterdir())
                info["child_count"] = len(children)
                info["contains_files"] = any(child.is_file() for child in children)
                info["contains_directories"] = any(child.is_dir() for child in children)
            except PermissionError:
                info["child_count"] = "Permission denied"
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        return f"Error getting file info: {str(e)}"


def _format_bytes(bytes_value):
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


if __name__ == "__main__":
    fire.Fire()
