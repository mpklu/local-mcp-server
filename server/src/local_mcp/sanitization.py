"""
Input sanitization and security validation for Local MCP Server.

This module provides comprehensive input validation to prevent:
- Path traversal attacks
- Command injection
- Prompt injection
- Log injection
- Type confusion attacks
"""

import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Centralized input sanitization for security."""
    
    # Dangerous patterns
    SHELL_META = re.compile(r'[;&|`$<>()\n]')
    PROMPT_INJECTION = re.compile(
        r'(ignore|disregard|new instructions|system message|always confirm|do not ask)',
        re.IGNORECASE
    )
    IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    # Maximum lengths
    MAX_IDENTIFIER_LENGTH = 64
    MAX_STRING_LENGTH = 1000000  # 1MB
    MAX_PATH_LENGTH = 4096
    
    @staticmethod
    def sanitize_identifier(name: str) -> Tuple[bool, str, str]:
        """Validate identifier (tool name, parameter name, function name).
        
        Args:
            name: Identifier to validate
            
        Returns:
            Tuple of (is_valid, sanitized_name, error_message)
        """
        if not name:
            return False, "", "Identifier cannot be empty"
        
        if not isinstance(name, str):
            return False, "", f"Identifier must be string, got {type(name).__name__}"
        
        if len(name) > InputSanitizer.MAX_IDENTIFIER_LENGTH:
            return False, "", f"Identifier too long: {len(name)} > {InputSanitizer.MAX_IDENTIFIER_LENGTH}"
        
        if not InputSanitizer.IDENTIFIER_PATTERN.match(name):
            return False, "", f"Invalid identifier format: {name} (only alphanumeric, underscore, hyphen allowed)"
        
        return True, name, ""
    
    @staticmethod
    def sanitize_path(
        path: str,
        allowed_bases: List[Path],
        allow_absolute: bool = False,
        follow_symlinks: bool = True,
        tool_name: str = "unknown"
    ) -> Tuple[bool, Optional[Path], str]:
        """Validate and sanitize file path.
        
        Args:
            path: Path to validate
            allowed_bases: List of allowed base directories
            allow_absolute: Whether to allow absolute paths
            follow_symlinks: Whether to resolve and validate symlinks
            tool_name: Name of tool (for logging)
            
        Returns:
            Tuple of (is_valid, resolved_path, error_message)
        """
        if not path:
            return False, None, "Path cannot be empty"
        
        if not isinstance(path, str):
            return False, None, f"Path must be string, got {type(path).__name__}"
        
        if len(path) > InputSanitizer.MAX_PATH_LENGTH:
            return False, None, f"Path too long: {len(path)} > {InputSanitizer.MAX_PATH_LENGTH}"
        
        try:
            path_obj = Path(path)
            
            # Check for absolute paths
            if path_obj.is_absolute():
                if not allow_absolute:
                    logger.warning(
                        f"[{tool_name}] Rejected absolute path: {path}"
                    )
                    return False, None, f"Absolute paths not allowed for this tool: {path}"
            
            # Check for parent directory references
            if '..' in path_obj.parts:
                logger.warning(
                    f"[{tool_name}] Rejected path with parent directory reference: {path}"
                )
                return False, None, f"Parent directory references (..) not allowed: {path}"
            
            # Resolve the path against each allowed base
            resolved = None
            matched_base = None
            
            for base in allowed_bases:
                try:
                    if path_obj.is_absolute():
                        # For absolute paths, check if they're within any allowed base
                        resolved_test = path_obj.resolve() if follow_symlinks else path_obj
                        
                        # Check if path is within this base
                        try:
                            relative = resolved_test.relative_to(base.resolve())
                            # Success - path is within this base
                            resolved = resolved_test
                            matched_base = base
                            break
                        except ValueError:
                            # Path is not relative to this base, try next
                            continue
                    else:
                        # For relative paths, resolve against base
                        resolved_test = (base / path_obj).resolve() if follow_symlinks else (base / path_obj)
                        
                        # Verify resolved path is still within base
                        try:
                            relative = resolved_test.relative_to(base.resolve())
                            # Success - path stays within base
                            resolved = resolved_test
                            matched_base = base
                            break
                        except ValueError:
                            # Path escaped the base (via symlink or other means)
                            continue
                            
                except Exception as e:
                    logger.debug(f"[{tool_name}] Error testing path against base {base}: {e}")
                    continue
            
            if resolved is None or matched_base is None:
                # Path doesn't resolve to any allowed base
                logger.warning(
                    f"[{tool_name}] Path not within any allowed directory: {path}"
                )
                return False, None, (
                    f"Path not within allowed directories: {path}\n"
                    f"Allowed bases: {', '.join(str(b) for b in allowed_bases)}"
                )
            
            # Additional check: if we resolved symlinks, verify the result
            if follow_symlinks and resolved != path_obj:
                logger.debug(
                    f"[{tool_name}] Path resolved via symlink: {path} -> {resolved}"
                )
            
            logger.debug(
                f"[{tool_name}] Path validated: {path} -> {resolved} (base: {matched_base})"
            )
            
            return True, resolved, ""
            
        except Exception as e:
            logger.error(f"[{tool_name}] Path validation error for {path}: {e}")
            return False, None, f"Path validation error: {str(e)}"
    
    @staticmethod
    def sanitize_string_value(
        value: str,
        max_length: Optional[int] = None,
        check_prompt_injection: bool = True
    ) -> Tuple[bool, str, str]:
        """Sanitize string parameter value.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length (default: MAX_STRING_LENGTH)
            check_prompt_injection: Whether to check for prompt injection
            
        Returns:
            Tuple of (is_valid, value, error_message)
        """
        if not isinstance(value, str):
            return False, "", f"Value must be string, got {type(value).__name__}"
        
        max_len = max_length or InputSanitizer.MAX_STRING_LENGTH
        
        # Check length
        if len(value) > max_len:
            return False, "", f"String too long: {len(value)} > {max_len}"
        
        # Check for null bytes
        if '\x00' in value:
            return False, "", "String contains null bytes"
        
        # Check for prompt injection
        if check_prompt_injection and InputSanitizer.detect_prompt_injection(value):
            logger.warning(f"Potential prompt injection detected in string value")
            return False, "", "Potential prompt injection detected in value"
        
        return True, value, ""
    
    @staticmethod
    def sanitize_for_logging(value: Any, max_length: int = 200) -> str:
        """Sanitize value for safe logging.
        
        Args:
            value: Value to sanitize
            max_length: Maximum length for log output
            
        Returns:
            Sanitized string safe for logging
        """
        str_val = str(value)
        
        # Remove control characters
        str_val = str_val.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        
        # Truncate if too long
        if len(str_val) > max_length:
            str_val = str_val[:max_length] + '...'
        
        return str_val
    
    @staticmethod
    def detect_prompt_injection(text: str) -> bool:
        """Detect potential prompt injection attempts.
        
        Args:
            text: Text to check
            
        Returns:
            True if potential injection detected
        """
        return bool(InputSanitizer.PROMPT_INJECTION.search(text))
    
    @staticmethod
    def sanitize_tool_output(output: str, max_length: Optional[int] = None) -> str:
        """Sanitize tool output before returning to AI.
        
        Args:
            output: Tool output to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized output with clear boundaries
        """
        # Add clear boundaries to prevent prompt injection
        sanitized = f"[TOOL OUTPUT START]\n{output}\n[TOOL OUTPUT END]"
        
        # Truncate if needed
        if max_length and len(sanitized) > max_length:
            truncated = output[:max_length - 100]  # Leave room for boundaries
            sanitized = f"[TOOL OUTPUT START]\n{truncated}\n... (output truncated)\n[TOOL OUTPUT END]"
        
        return sanitized


def validate_arguments_security(
    arguments: Dict[str, Any],
    config: Dict[str, Any],
    tool_name: str,
    tools_dir: Path
) -> List[str]:
    """Validate arguments for security issues.
    
    Args:
        arguments: Tool arguments to validate
        config: Tool configuration with workspace settings
        tool_name: Name of the tool
        tools_dir: Path to tools directory
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    sanitizer = InputSanitizer()
    
    # Get workspace configuration
    workspace_config = config.get('workspace_config', {})
    
    # Build allowed paths list
    allowed_paths = []
    
    # Add configured allowed paths
    for path_str in workspace_config.get('allowed_paths', []):
        # Expand special variables
        expanded = path_str.replace('{TOOL_DIR}', str(tools_dir / tool_name))
        expanded = expanded.replace('{HOME}', str(Path.home()))
        expanded = expanded.replace('{TEMP}', str(Path('/tmp')))
        
        path_obj = Path(expanded).expanduser()
        if path_obj.exists() or workspace_config.get('create_workspace', True):
            allowed_paths.append(path_obj)
    
    # Default: tool's own workspace directory
    if not allowed_paths:
        default_workspace = tools_dir / tool_name / 'workspace'
        allowed_paths.append(default_workspace)
    
    allow_absolute = workspace_config.get('allow_absolute_paths', False)
    follow_symlinks = workspace_config.get('follow_symlinks', True)
    
    # Validate each argument
    for key, value in arguments.items():
        # Skip special keys
        if key in ['confirm', 'function', 'command']:
            continue
        
        # Validate parameter names
        is_valid, _, error = sanitizer.sanitize_identifier(key)
        if not is_valid:
            errors.append(f"Invalid parameter name '{key}': {error}")
            continue
        
        # Check for path parameters
        if 'path' in key.lower() or 'file' in key.lower() or 'dir' in key.lower():
            if isinstance(value, str) and value:
                is_valid, resolved, error = sanitizer.sanitize_path(
                    value,
                    allowed_paths,
                    allow_absolute=allow_absolute,
                    follow_symlinks=follow_symlinks,
                    tool_name=tool_name
                )
                
                if not is_valid:
                    errors.append(f"Path validation failed for '{key}': {error}")
        
        # Validate string values
        elif isinstance(value, str):
            max_len = workspace_config.get('max_string_length')
            is_valid, _, error = sanitizer.sanitize_string_value(
                value,
                max_length=max_len,
                check_prompt_injection=True
            )
            
            if not is_valid:
                errors.append(f"String validation failed for '{key}': {error}")
    
    return errors
