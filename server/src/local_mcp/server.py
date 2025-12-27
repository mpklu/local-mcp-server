#!/usr/bin/env python3
"""
Local MCP Server - Main Entry Point

A Model Context Protocol server that exposes local scripts in the tools directory
for execution through Claude Desktop.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .config import Config
from .discovery import ScriptDiscovery
from .executor import ScriptExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LocalMCPServer:
    """Main MCP server class."""
    
    def __init__(self, tools_dir: Path, config_dir: Path):
        self.tools_dir = tools_dir
        self.config_dir = config_dir
        self.config = Config(config_dir)
        
        # Setup logging first
        from .logging_config import setup_logging
        from .sanitization import SensitiveDataRedactor
        
        log_dir = Path(self.config.get_global_config().log_dir)
        self.audit_logger = setup_logging(
            log_dir=log_dir,
            level=self.config.get_global_config().log_level,
            enable_json=self.config.get_global_config().enable_json_logging,
            enable_file_logging=self.config.get_global_config().enable_file_logging,
            enable_audit_logging=self.config.get_global_config().enable_audit_logging,
            max_bytes=self.config.get_global_config().log_max_bytes,
            backup_count=self.config.get_global_config().log_backup_count
        )
        
        # Setup redactor
        self.redactor = SensitiveDataRedactor()
        self.redact_enabled = self.config.get_global_config().redact_sensitive_data
        
        # Use configurable server name
        server_name = self.config.get_global_config().server_name
        self.server = Server(server_name)
        
        self.discovery = ScriptDiscovery(tools_dir, self.config)
        self.executor = ScriptExecutor(tools_dir, self.config)
        
        # Cleanup old temporary files on startup
        cleanup_stats = self.executor.cleanup_temp_files()
        if cleanup_stats and cleanup_stats.get('cleaned', 0) > 0:
            logger.info(f"Cleaned up {cleanup_stats['cleaned']} old temp directories, "
                       f"freed {cleanup_stats['size_freed'] / (1024*1024):.2f} MB")
        
        # Setup server handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server request handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """Return available tools discovered from scripts."""
            try:
                tools = await self.discovery.get_available_tools()
                logger.info(f"Listed {len(tools)} available tools")
                return tools
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return []
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[dict]:
            """Execute a tool with given arguments."""
            from .logging_config import generate_request_id
            from .sanitization import SensitiveDataRedactor
            
            request_id = generate_request_id()
            
            # Redact sensitive data for logging
            if self.redact_enabled:
                redacted_args = SensitiveDataRedactor.redact_for_logging(
                    arguments,
                    sensitive_keys=set(self.config.get_global_config().sensitive_keys)
                )
            else:
                redacted_args = str(arguments)
            
            logger.info(f"[{request_id}] Executing tool: {name} with args: {redacted_args}")
            
            # Audit log start
            if self.audit_logger:
                audit_args = SensitiveDataRedactor.redact_for_audit(
                    arguments,
                    sensitive_keys=set(self.config.get_global_config().sensitive_keys)
                )
                self.audit_logger.log_tool_execution_start(
                    request_id=request_id,
                    tool_name=name,
                    arguments=audit_args,
                    confirmed=arguments.get('confirm', False)
                )
            
            try:
                # Validate arguments against tool schema
                tools = await list_tools()
                tool = next((t for t in tools if t.name == name), None)
                
                if tool:
                    from .utils import validate_script_arguments
                    validation_errors = validate_script_arguments(arguments, tool.inputSchema)
                    
                    if validation_errors:
                        error_msg = f"Validation failed for tool {name}:\n" + "\n".join(validation_errors)
                        logger.error(f"[{request_id}] {error_msg}")
                        
                        # Enhanced audit logging for validation failures
                        if self.audit_logger:
                            # Log security event for validation failure
                            self.audit_logger.log_security_event(
                                event_type="validation_failure",
                                description=f"Parameter validation failed for tool {name}",
                                tool_name=name,
                                request_id=request_id,
                                details={
                                    "validation_errors": validation_errors,
                                    "error_count": len(validation_errors)
                                }
                            )
                            
                            self.audit_logger.log_tool_execution_end(
                                request_id=request_id,
                                tool_name=name,
                                success=False,
                                exit_code=1,
                                execution_time=0.0,
                                error_message="Validation failed"
                            )
                        
                        return [{"type": "text", "text": error_msg}]
                
                # Execute tool and get structured result
                result_obj = await self.executor.execute_script_structured(
                    name, arguments, request_id=request_id
                )
                
                # Calculate output size before truncation
                output_size = len(result_obj.stdout) if result_obj.stdout else 0
                was_truncated = output_size > self.config.get_global_config().max_output_length
                
                # Enhanced audit log completion
                if self.audit_logger:
                    # Add output size to audit log
                    extra_info = {
                        'output_size': output_size,
                        'was_truncated': was_truncated
                    }
                    
                    # Log security event if output was unusually large
                    if output_size > 100000:  # 100KB threshold
                        self.audit_logger.log_security_event(
                            event_type="large_output",
                            description=f"Tool {name} generated large output: {output_size} bytes",
                            tool_name=name,
                            request_id=request_id,
                            details=extra_info
                        )
                    
                    self.audit_logger.log_tool_execution_end(
                        request_id=request_id,
                        tool_name=name,
                        success=result_obj.success,
                        exit_code=result_obj.exit_code,
                        execution_time=result_obj.execution_time,
                        error_message=result_obj.stderr if not result_obj.success else None
                    )
                
                logger.info(
                    f"[{request_id}] Tool execution completed: {name} "
                    f"(output: {output_size} bytes, time: {result_obj.execution_time:.2f}s)"
                )
                
                # Return output with structured format support (Option 1: Tool-Driven Output)
                if result_obj.success:
                    # Apply truncation
                    output = result_obj.to_string(
                        max_length=self.config.get_global_config().max_output_length
                    )
                    
                    # Try to parse as JSON for structured output
                    try:
                        import json
                        parsed_data = json.loads(output)
                        
                        # Successfully parsed JSON - return structured format
                        logger.debug(f"[{request_id}] Tool output is valid JSON, returning structured format")
                        return [{
                            "type": "text",
                            "text": json.dumps({
                                "status": "success",
                                "data": parsed_data,
                                "format": "json",
                                "metadata": {
                                    "execution_time": result_obj.execution_time,
                                    "exit_code": result_obj.exit_code
                                }
                            }, indent=2)
                        }]
                    except (json.JSONDecodeError, ValueError):
                        # Not JSON or invalid JSON - return as plain text
                        logger.debug(f"[{request_id}] Tool output is plain text, returning text format")
                        return [{
                            "type": "text",
                            "text": output
                        }]
                else:
                    # Format error message
                    error_output = result_obj.to_string(
                        max_length=self.config.get_global_config().max_output_length
                    )
                    
                    # Try to parse stderr as structured error JSON
                    try:
                        import json
                        parsed_error = json.loads(result_obj.stderr)
                        
                        # Tool returned structured error
                        logger.debug(f"[{request_id}] Tool error is structured JSON")
                        return [{
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": parsed_error,
                                "format": "json",
                                "metadata": {
                                    "execution_time": result_obj.execution_time,
                                    "exit_code": result_obj.exit_code
                                }
                            }, indent=2)
                        }]
                    except (json.JSONDecodeError, ValueError):
                        # Return plain text error
                        return [{
                            "type": "text",
                            "text": error_output
                        }]
                
            except Exception as e:
                # Log full error internally with all details
                from .sanitization import SafeErrorFormatter
                SafeErrorFormatter.log_error(
                    logger,
                    error=e,
                    tool_name=name,
                    request_id=request_id,
                    arguments=arguments
                )
                
                # Return sanitized error to client
                safe_error_msg = SafeErrorFormatter.format_error(
                    error=e,
                    tool_name=name,
                    request_id=request_id
                )
                
                # Enhanced audit log for exceptions
                if self.audit_logger:
                    # Log security event for unexpected exceptions
                    self.audit_logger.log_security_event(
                        event_type="execution_exception",
                        description=f"Unexpected exception during tool execution: {type(e).__name__}",
                        tool_name=name,
                        request_id=request_id,
                        details={
                            'exception_type': type(e).__name__,
                            'exception_module': type(e).__module__
                        }
                    )
                    
                    self.audit_logger.log_tool_execution_end(
                        request_id=request_id,
                        tool_name=name,
                        success=False,
                        exit_code=-1,
                        execution_time=0.0,
                        error_message=type(e).__name__  # Log type, not full message
                    )
                
                return [{"type": "text", "text": safe_error_msg}]
    
    async def run(self, force_discovery: bool = False, full_discovery: bool = False, host_type: str = "claude-desktop"):
        """Start the MCP server with the specified host adapter."""
        logger.info("Starting Local MCP Server...")
        logger.info(f"Tools directory: {self.tools_dir}")
        logger.info(f"Config directory: {self.config_dir}")
        logger.info(f"Host type: {host_type}")
        
        # Initialize discovery and load tools
        if force_discovery:
            if full_discovery:
                logger.info("Performing full tool discovery (ignoring modification times)")
                await self.discovery.discover_scripts(force_full=True)
            else:
                logger.info("Performing incremental tool discovery")
                await self.discovery.discover_scripts(force_full=False)
        else:
            logger.info("Skipping discovery - using existing tool configurations")
            await self.discovery.load_existing_tools()
        
        # Create and run host adapter
        from .adapters import AdapterFactory
        
        # Get host-specific configuration if available
        host_config = self.config.get_global_config().__dict__
        
        try:
            adapter = AdapterFactory.create_adapter(host_type, self.server, host_config)
            logger.info(f"Created {host_type} adapter")
            
            # Validate environment
            is_valid, issues = adapter.validate_environment()
            if not is_valid:
                logger.warning(f"Environment validation issues for {host_type}:")
                for issue in issues:
                    logger.warning(f"  - {issue}")
            
            # Run the adapter
            await adapter.run()
            
        except ValueError as e:
            logger.error(f"Failed to create adapter: {e}")
            available_types = AdapterFactory.get_available_types()
            logger.error(f"Available host types: {', '.join(available_types)}")
            raise
        except Exception as e:
            logger.error(f"Adapter error: {e}")
            raise


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Local MCP Server for executing tools directory scripts"
    )
    parser.add_argument(
        "--tools-dir",
        type=Path,
        help="Path to tools directory (default: ../tools relative to script)"
    )
    parser.add_argument(
        "--config-dir", 
        type=Path,
        help="Path to config directory (default: ./config relative to script)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Force discovery of tools (default: skip discovery and use existing config)"
    )
    parser.add_argument(
        "--force-discover",
        action="store_true",
        help="Force full rediscovery of all tools (ignores modification times)"
    )
    parser.add_argument(
        "--build-tools",
        action="store_true",
        help="Build tools.json from individual tool configs before starting server"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="claude-desktop",
        help="MCP host type (claude-desktop, generic, google-gemini-cli)"
    )
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine default paths relative to this script location
    # From src/local_mcp/server.py, go up to project root, then up one more level to find tools
    script_dir = Path(__file__).parent.parent.parent.parent  # Go up to workspace root
    tools_dir = args.tools_dir or script_dir / "tools"
    config_dir = args.config_dir or Path(__file__).parent.parent.parent / "config"
    
    # Build tools.json if requested
    if args.build_tools:
        logger.info("Building tools.json from individual tool configurations...")
        try:
            # Import and run the build function
            build_script = Path(__file__).parent.parent.parent / "build_tools.py"
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(build_script),
                "--config-dir", str(config_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Build failed with return code {process.returncode}")
                logger.error(f"Build stderr: {stderr.decode()}")
                sys.exit(1)
            else:
                logger.info("Build completed successfully")
                
        except Exception as e:
            logger.error(f"Build error: {e}")
            sys.exit(1)
    
    # Validate paths
    if not tools_dir.exists():
        logger.error(f"Tools directory not found: {tools_dir}")
        sys.exit(1)
    
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create and run server
    server = LocalMCPServer(tools_dir, config_dir)
    await server.run(
        force_discovery=args.discover or args.force_discover,
        full_discovery=args.force_discover,
        host_type=args.host
    )


def sync_main():
    """Synchronous wrapper for async main."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_main()
