"""
Structured logging configuration for Local MCP Server.

Provides:
- JSON formatted logs
- Rotating file handlers
- Separate audit log
- Request correlation IDs
"""

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import uuid


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add thread/process info
        if record.process:
            log_data["process_id"] = record.process
        if record.thread:
            log_data["thread_id"] = record.thread
        
        # Add custom fields from extra
        for key in ['request_id', 'tool_name', 'event', 'user_context', 'arguments',
                    'execution_time', 'exit_code', 'success', 'error_type', 'result_length']:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class AuditLogger:
    """Dedicated audit logger for security-critical events."""
    
    def __init__(self, log_dir: Path, max_bytes: int = 50*1024*1024, backup_count: int = 10):
        """Initialize audit logger.
        
        Args:
            log_dir: Directory for log files
            max_bytes: Max size per log file
            backup_count: Number of backup files to keep
        """
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Don't propagate to root logger
        
        # Create audit log file handler
        log_file = log_dir / 'audit.log'
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def log_tool_execution_start(
        self,
        request_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        user_context: Optional[str] = None,
        confirmed: bool = False
    ):
        """Log start of tool execution."""
        self.logger.info(
            f"Tool execution started: {tool_name}",
            extra={
                'event': 'tool_execution_start',
                'request_id': request_id,
                'tool_name': tool_name,
                'arguments': arguments,  # Already redacted by caller
                'user_context': user_context,
                'confirmed': confirmed
            }
        )
    
    def log_tool_execution_end(
        self,
        request_id: str,
        tool_name: str,
        success: bool,
        exit_code: int,
        execution_time: float,
        error_message: Optional[str] = None
    ):
        """Log end of tool execution."""
        self.logger.info(
            f"Tool execution completed: {tool_name} (success={success})",
            extra={
                'event': 'tool_execution_end',
                'request_id': request_id,
                'tool_name': tool_name,
                'success': success,
                'exit_code': exit_code,
                'execution_time': execution_time,
                'error_message': error_message
            }
        )
    
    def log_security_event(
        self,
        event_type: str,
        description: str,
        tool_name: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security-related event."""
        extra = {
            'event': 'security_event',
            'event_type': event_type,
            'description': description
        }
        
        if tool_name:
            extra['tool_name'] = tool_name
        if request_id:
            extra['request_id'] = request_id
        if details:
            extra.update(details)
        
        self.logger.warning(f"Security event: {event_type} - {description}", extra=extra)
    
    def log_configuration_change(
        self,
        change_type: str,
        description: str,
        user_context: Optional[str] = None
    ):
        """Log configuration changes."""
        self.logger.info(
            f"Configuration changed: {change_type}",
            extra={
                'event': 'configuration_change',
                'change_type': change_type,
                'description': description,
                'user_context': user_context
            }
        )


def setup_logging(
    log_dir: Path,
    level: str = "INFO",
    enable_json: bool = False,
    enable_file_logging: bool = True,
    enable_audit_logging: bool = True,
    max_bytes: int = 10*1024*1024,
    backup_count: int = 5
) -> Optional[AuditLogger]:
    """Configure logging for the MCP server.
    
    Args:
        log_dir: Directory for log files
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Use JSON formatter for structured logs
        enable_file_logging: Enable file logging (vs stdout only)
        enable_audit_logging: Enable separate audit log
        max_bytes: Max size per log file
        backup_count: Number of backup files to keep
        
    Returns:
        AuditLogger instance if audit logging enabled, None otherwise
    """
    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    if enable_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if enable_file_logging:
        log_file = log_dir / 'mcp-server.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        if enable_json:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
        root_logger.addHandler(file_handler)
    
    # Audit logger (optional)
    audit_logger = None
    if enable_audit_logging:
        audit_logger = AuditLogger(log_dir, max_bytes=max_bytes*5, backup_count=backup_count*2)
    
    return audit_logger


def generate_request_id() -> str:
    """Generate unique request ID for correlation."""
    return str(uuid.uuid4())
