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
        
        # Use configurable server name
        server_name = self.config.get_global_config().server_name
        self.server = Server(server_name)
        
        self.discovery = ScriptDiscovery(tools_dir, self.config)
        self.executor = ScriptExecutor(tools_dir, self.config)
        
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
            try:
                logger.info(f"Executing tool: {name} with args: {arguments}")
                
                # Validate arguments against tool schema
                tools = await list_tools()
                tool = next((t for t in tools if t.name == name), None)
                
                if tool:
                    from .utils import validate_script_arguments
                    validation_errors = validate_script_arguments(arguments, tool.inputSchema)
                    
                    if validation_errors:
                        error_msg = f"Validation failed for tool {name}:\n" + "\n".join(validation_errors)
                        logger.error(error_msg)
                        return [{"type": "text", "text": error_msg}]
                
                result = await self.executor.execute_script(name, arguments)
                return [{"type": "text", "text": result}]
            except Exception as e:
                error_msg = f"Error executing tool {name}: {e}"
                logger.error(error_msg)
                return [{"type": "text", "text": error_msg}]
    
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
