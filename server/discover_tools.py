#!/usr/bin/env python3
"""
Discovery tool to generate individual tool configuration files.

This script scans the tools/ directory and creates individual configuration
files in config/tools/ for any tools that don't already have them.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Set

# Add the src directory to path so we can import local_mcp modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from local_mcp.config import Config
    from local_mcp.discovery import ScriptDiscovery
except ImportError as e:
    print(f"Error importing local_mcp modules: {e}")
    print("Make sure you're running this from the server directory")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ToolConfigGenerator:
    """Generates individual tool configuration files for newly discovered tools."""
    
    def __init__(self, tools_dir: Path, config_dir: Path):
        self.tools_dir = tools_dir
        self.config_dir = config_dir
        self.tools_config_dir = config_dir / "tools"
        self.config = Config(config_dir)
        self.discovery = ScriptDiscovery(tools_dir, self.config)
    
    def get_existing_configs(self) -> Set[str]:
        """Get set of tool names that already have individual config files."""
        existing = set()
        
        if not self.tools_config_dir.exists():
            return existing
        
        for config_file in self.tools_config_dir.glob("*.json"):
            tool_name = config_file.stem
            existing.add(tool_name)
            
        return existing
    
    async def discover_new_tools(self) -> Dict[str, Dict[str, Any]]:
        """Discover tools in the tools directory."""
        logger.info("Discovering tools...")
        discovered = await self.discovery.discover_scripts(force_full=True)
        logger.info(f"Found {len(discovered)} tools in {self.tools_dir}")
        return discovered
    
    def create_individual_config(self, tool_name: str, script_config: Dict[str, Any]) -> bool:
        """Create an individual config file for a tool."""
        try:
            # Ensure tools config directory exists
            self.tools_config_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert ScriptConfig to dict if needed
            if hasattr(script_config, '__dict__'):
                script_config_dict = script_config.__dict__.copy()
            elif hasattr(script_config, 'dict'):
                script_config_dict = script_config.dict()
            else:
                script_config_dict = dict(script_config) if isinstance(script_config, dict) else script_config
            
            # Create the individual config structure
            individual_config = {
                "enabled": True,
                "last_modified": datetime.now().isoformat(),
                "auto_detected": True,
                "created_by": "discovery_tool",
                "tags": script_config_dict.get("tags", []),
                "script_config": script_config_dict
            }
            
            # Remove tags from script_config if they exist (avoid duplication)
            if "tags" in individual_config["script_config"]:
                del individual_config["script_config"]["tags"]
            
            # Write the config file
            config_file = self.tools_config_dir / f"{tool_name}.json"
            with open(config_file, 'w') as f:
                json.dump(individual_config, f, indent=2)
            
            logger.info(f"✅ Created config for: {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create config for {tool_name}: {e}")
            return False
    
    async def generate_missing_configs(self, dry_run: bool = False) -> Dict[str, bool]:
        """Generate individual configs for tools that don't have them yet."""
        # Get existing configs
        existing_configs = self.get_existing_configs()
        logger.info(f"Found {len(existing_configs)} existing individual configs")
        
        # Discover all tools
        discovered_tools = await self.discover_new_tools()
        
        # Find tools that need configs
        new_tools = {}
        for tool_name, tool_data in discovered_tools.items():
            if tool_name not in existing_configs:
                new_tools[tool_name] = tool_data
        
        if not new_tools:
            logger.info("🎉 All tools already have individual config files")
            return {}
        
        logger.info(f"📝 Found {len(new_tools)} tools that need individual configs:")
        for tool_name in new_tools:
            logger.info(f"  - {tool_name}")
        
        if dry_run:
            logger.info("🔍 Dry run mode - no files will be created")
            return {name: True for name in new_tools}
        
        # Create configs for new tools
        results = {}
        for tool_name, tool_data in new_tools.items():
            # Extract the ScriptConfig from the discovery data
            script_config = tool_data.get('config') if isinstance(tool_data, dict) else tool_data
            success = self.create_individual_config(tool_name, script_config)
            results[tool_name] = success
        
        return results
    
    def list_tools_status(self) -> None:
        """List all tools and their config status."""
        import asyncio
        
        async def _list_status():
            existing_configs = self.get_existing_configs()
            discovered_tools = await self.discover_new_tools()
            
            print("\n📋 Tool Configuration Status:")
            print("=" * 50)
            
            all_tools = set(discovered_tools.keys()) | existing_configs
            
            for tool_name in sorted(all_tools):
                has_config = tool_name in existing_configs
                discovered = tool_name in discovered_tools
                
                status = "✅" if has_config else "❌"
                discovery_status = "📁" if discovered else "🚫"
                
                print(f"{status} {discovery_status} {tool_name}")
                
                if discovered:
                    tool_data = discovered_tools[tool_name]
                    script_path = tool_data.get("script_path", "Unknown")
                    description = tool_data.get("description", "No description")
                    print(f"     Path: {script_path}")
                    print(f"     Desc: {description}")
                
                if not has_config and discovered:
                    print(f"     ⚠️  Needs individual config file")
                elif has_config and not discovered:
                    print(f"     ⚠️  Config exists but tool not found in filesystem")
                    
                print()
            
            print(f"Legend:")
            print(f"  ✅/❌ = Has/Missing individual config file")
            print(f"  📁/🚫 = Found/Missing in tools directory")
        
        asyncio.run(_list_status())


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate individual tool configuration files for newly discovered tools"
    )
    parser.add_argument(
        "--tools-dir", 
        type=Path, 
        default=Path(__file__).parent.parent / "tools",
        help="Tools directory path (default: ../tools)"
    )
    parser.add_argument(
        "--config-dir", 
        type=Path, 
        default=Path(__file__).parent / "config",
        help="Configuration directory path (default: ./config)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be created without actually creating files"
    )
    parser.add_argument(
        "--list", 
        action="store_true",
        help="List all tools and their configuration status"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tools_dir = args.tools_dir.resolve()
    config_dir = args.config_dir.resolve()
    
    if not tools_dir.exists():
        logger.error(f"Tools directory does not exist: {tools_dir}")
        return 1
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    generator = ToolConfigGenerator(tools_dir, config_dir)
    
    if args.list:
        generator.list_tools_status()
        return 0
    
    # Generate configs
    import asyncio
    
    async def run_generation():
        results = await generator.generate_missing_configs(dry_run=args.dry_run)
        
        if not results:
            return 0
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        if args.dry_run:
            logger.info(f"🔍 Dry run complete: {total_count} configs would be created")
        else:
            logger.info(f"✅ Created {success_count}/{total_count} individual configs")
            
            if success_count < total_count:
                logger.warning("Some configs failed to create - check logs above")
                return 1
        
        return 0
    
    return asyncio.run(run_generation())


if __name__ == "__main__":
    sys.exit(main())