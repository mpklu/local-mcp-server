"""
Input sanitization and security validation for Local MCP Server.

This module provides comprehensive input validation to prevent:
- Path traversal attacks
- Command injection
- Prompt injection
- Log injection
- Type confusion attacks
- Sensitive data leakage in logs
"""

import re
import logging
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Set

logger = logging.getLogger(__name__)


class SensitiveDataRedactor:
    """Redact sensitive data from logs and outputs."""
    
    # Sensitive key patterns (case-insensitive)
    SENSITIVE_KEYS = {
        'password', 'passwd', 'pwd',
        'secret', 'token', 'key', 'api_key', 'apikey', 'api-key',
        'authorization', 'auth', 'auth_token',
        'private_key', 'private-key', 'privatekey',
        'access_key', 'access-key', 'accesskey',
        'secret_key', 'secret-key', 'secretkey',
        'ssn', 'social_security',
        'credit_card', 'creditcard', 'ccn', 'card_number',
        'pin', 'cvv', 'cvc',
        'bearer', 'oauth', 'session',
        'cookie', 'csrf'
    }
    
    # Sensitive value patterns (regex)
    PATTERNS = {
        'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'api_key_generic': re.compile(r'\b[a-zA-Z0-9_-]{32,}\b'),
        'aws_key': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
        'github_token': re.compile(r'\bghp_[a-zA-Z0-9]{36}\b'),
        'gitlab_token': re.compile(r'\bglpat-[a-zA-Z0-9_-]{20}\b'),
        'openai_key': re.compile(r'\bsk-[a-zA-Z0-9]{48}\b'),
        'jwt': re.compile(r'\beyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b'),
        'private_key': re.compile(r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'),
    }
    
    @staticmethod
    def redact_dict(
        data: Dict[str, Any],
        sensitive_keys: Optional[Set[str]] = None,
        redaction_style: str = "full",
        scan_values: bool = True
    ) -> Dict[str, Any]:
        """Redact sensitive data from dictionary.
        
        Args:
            data: Dictionary to redact
            sensitive_keys: Additional keys to treat as sensitive
            redaction_style: "full" (***REDACTED***), "partial" (abc***xyz), "hint" (<redacted:8_chars>)
            scan_values: Whether to scan string values for sensitive patterns
            
        Returns:
            Dictionary with sensitive data redacted
        """
        if sensitive_keys is None:
            sensitive_keys = set()
        
        all_sensitive_keys = SensitiveDataRedactor.SENSITIVE_KEYS | sensitive_keys
        result = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if key is sensitive
            is_sensitive_key = any(sk in key_lower for sk in all_sensitive_keys)
            
            if is_sensitive_key:
                # Redact based on style
                if isinstance(value, str):
                    result[key] = SensitiveDataRedactor._redact_string(
                        value, redaction_style, f"key:{key}"
                    )
                else:
                    result[key] = "***REDACTED***"
            elif isinstance(value, dict):
                # Recursively redact nested dicts
                result[key] = SensitiveDataRedactor.redact_dict(
                    value, sensitive_keys, redaction_style, scan_values
                )
            elif isinstance(value, list):
                # Redact lists
                result[key] = [
                    SensitiveDataRedactor.redact_dict(item, sensitive_keys, redaction_style, scan_values)
                    if isinstance(item, dict)
                    else SensitiveDataRedactor._redact_value(item, redaction_style, scan_values)
                    for item in value
                ]
            else:
                # Check value for patterns
                result[key] = SensitiveDataRedactor._redact_value(value, redaction_style, scan_values)
        
        return result
    
    @staticmethod
    def _redact_value(value: Any, redaction_style: str, scan_values: bool) -> Any:
        """Redact a single value if it contains sensitive patterns."""
        if not scan_values or not isinstance(value, str):
            return value
        
        # Check for sensitive patterns
        for pattern_name, pattern in SensitiveDataRedactor.PATTERNS.items():
            if pattern.search(value):
                return SensitiveDataRedactor._redact_string(
                    value, redaction_style, f"pattern:{pattern_name}"
                )
        
        return value
    
    @staticmethod
    def _redact_string(value: str, redaction_style: str, reason: str) -> str:
        """Redact a string based on style."""
        if redaction_style == "full":
            return "***REDACTED***"
        elif redaction_style == "partial" and len(value) > 8:
            return f"{value[:3]}***{value[-3:]}"
        elif redaction_style == "hint":
            return f"<redacted:{len(value)}_chars:{reason}>"
        else:
            return "***REDACTED***"
    
    @staticmethod
    def redact_for_logging(
        data: Any,
        max_length: int = 500,
        sensitive_keys: Optional[Set[str]] = None
    ) -> str:
        """Redact and format data for logging.
        
        Args:
            data: Data to redact and format
            max_length: Maximum length of output
            sensitive_keys: Additional sensitive keys
            
        Returns:
            Redacted string safe for logging
        """
        if isinstance(data, dict):
            redacted = SensitiveDataRedactor.redact_dict(
                data,
                sensitive_keys=sensitive_keys,
                redaction_style="full",
                scan_values=True
            )
            result = str(redacted)
        else:
            result = str(data)
        
        # Scan result for patterns one more time
        for pattern_name, pattern in SensitiveDataRedactor.PATTERNS.items():
            result = pattern.sub("***REDACTED***", result)
        
        # Remove control characters
        result = result.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        
        # Truncate if too long
        if len(result) > max_length:
            result = result[:max_length] + '...'
        
        return result
    
    @staticmethod
    def redact_for_audit(
        data: Any,
        sensitive_keys: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """Redact data for audit logs (with hints for debugging).
        
        Args:
            data: Data to redact
            sensitive_keys: Additional sensitive keys
            
        Returns:
            Redacted dictionary with type hints
        """
        if isinstance(data, dict):
            return SensitiveDataRedactor.redact_dict(
                data,
                sensitive_keys=sensitive_keys,
                redaction_style="hint",
                scan_values=True
            )
        else:
            return {"value": str(data)}


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


class SafeErrorFormatter:
    """Format exceptions safely for client consumption, preventing information leakage."""
    
    # Map exception types to safe, user-friendly messages
    SAFE_ERROR_MESSAGES = {
        # File system errors
        FileNotFoundError: "The requested resource was not found",
        PermissionError: "Permission denied - insufficient access rights",
        IsADirectoryError: "Invalid operation on directory",
        NotADirectoryError: "Expected directory but found file",
        FileExistsError: "Resource already exists",
        OSError: "System error occurred",
        
        # Import and module errors
        ModuleNotFoundError: "Required module is not available",
        ImportError: "Failed to import required module",
        
        # Execution errors
        TimeoutError: "Operation timed out",
        subprocess.TimeoutExpired: "Tool execution timed out",
        ConnectionError: "Connection failed",
        ConnectionRefusedError: "Connection refused",
        ConnectionResetError: "Connection reset",
        BrokenPipeError: "Connection interrupted",
        
        # Value errors
        ValueError: "Invalid input value",
        TypeError: "Invalid input type",
        KeyError: "Missing required field",
        IndexError: "Index out of range",
        AttributeError: "Invalid attribute access",
        
        # Runtime errors
        RuntimeError: "Runtime error occurred",
        MemoryError: "Insufficient memory",
        RecursionError: "Operation too complex",
        
        # JSON errors
        json.JSONDecodeError: "Invalid JSON format",
        
        # Other common errors
        UnicodeDecodeError: "Invalid character encoding",
        UnicodeEncodeError: "Character encoding error",
    }
    
    # Patterns to scrub from error messages
    SCRUB_PATTERNS = [
        # Absolute filesystem paths
        (re.compile(r'/[a-zA-Z0-9/_.-]+'), '<path>'),
        (re.compile(r'[A-Z]:\\[a-zA-Z0-9\\_.-]+'), '<path>'),
        
        # Usernames
        (re.compile(r'/Users/[a-zA-Z0-9_-]+'), '/Users/<user>'),
        (re.compile(r'/home/[a-zA-Z0-9_-]+'), '/home/<user>'),
        
        # IP addresses
        (re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'), '<ip_address>'),
        
        # Port numbers in URLs
        (re.compile(r':\d{2,5}(/|$)'), ':<port>\\1'),
        
        # Hostnames
        (re.compile(r'@[a-zA-Z0-9.-]+\.[a-z]{2,}'), '@<hostname>'),
        
        # Database connection strings
        (re.compile(r'(postgresql|mysql|mongodb|redis)://[^\s]+'), '<database_url>'),
        
        # Environment variable values
        (re.compile(r'([A-Z_]+)=[^\s]+'), '\\1=<value>'),
    ]
    
    @classmethod
    def format_error(
        cls,
        error: Exception,
        tool_name: Optional[str] = None,
        include_type: bool = False,
        request_id: Optional[str] = None
    ) -> str:
        """Format an exception into a safe, client-facing error message.
        
        Args:
            error: The exception to format
            tool_name: Optional tool name for context
            include_type: Whether to include exception type name
            request_id: Optional request ID for correlation
            
        Returns:
            Safe error message string
        """
        error_type = type(error)
        
        # Get base safe message
        safe_message = cls.SAFE_ERROR_MESSAGES.get(
            error_type,
            "An error occurred during tool execution"
        )
        
        # Add tool context if provided
        if tool_name:
            safe_message = f"Tool '{tool_name}' failed: {safe_message}"
        
        # Add exception type if requested (useful for debugging)
        if include_type:
            safe_message = f"[{error_type.__name__}] {safe_message}"
        
        # Add request ID for correlation
        if request_id:
            safe_message += f" (Request ID: {request_id})"
        
        return safe_message
    
    @classmethod
    def format_error_with_details(
        cls,
        error: Exception,
        tool_name: Optional[str] = None,
        allow_partial_message: bool = False,
        request_id: Optional[str] = None
    ) -> str:
        """Format error with scrubbed details from original message.
        
        Args:
            error: The exception to format
            tool_name: Optional tool name for context
            allow_partial_message: If True, includes scrubbed error message
            request_id: Optional request ID for correlation
            
        Returns:
            Safe error message with optional scrubbed details
        """
        # Start with safe base message
        message = cls.format_error(error, tool_name, include_type=True, request_id=request_id)
        
        # Optionally add scrubbed details
        if allow_partial_message and str(error):
            scrubbed = cls._scrub_sensitive_info(str(error))
            message += f"\nDetails: {scrubbed}"
        
        return message
    
    @classmethod
    def _scrub_sensitive_info(cls, text: str) -> str:
        """Remove sensitive information from error text.
        
        Args:
            text: Text to scrub
            
        Returns:
            Scrubbed text with sensitive info replaced
        """
        scrubbed = text
        
        for pattern, replacement in cls.SCRUB_PATTERNS:
            scrubbed = pattern.sub(replacement, scrubbed)
        
        # Limit length
        if len(scrubbed) > 200:
            scrubbed = scrubbed[:200] + "..."
        
        return scrubbed
    
    @classmethod
    def log_error(
        cls,
        logger: logging.Logger,
        error: Exception,
        tool_name: Optional[str] = None,
        request_id: Optional[str] = None,
        arguments: Optional[Dict[str, Any]] = None
    ):
        """Log full error details internally (not sent to client).
        
        Args:
            logger: Logger instance to use
            error: The exception to log
            tool_name: Optional tool name
            request_id: Optional request ID for correlation
            arguments: Optional arguments (will be redacted)
        """
        extra = {
            'error_type': type(error).__name__,
            'request_id': request_id,
            'tool_name': tool_name
        }
        
        if arguments:
            # Redact sensitive arguments before logging
            extra['arguments'] = SensitiveDataRedactor.redact_for_logging(
                arguments,
                sensitive_keys={'password', 'token', 'key', 'secret'}
            )
        
        logger.error(
            f"Tool execution error: {type(error).__name__}: {error}",
            exc_info=True,
            extra=extra
        )
