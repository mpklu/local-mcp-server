#!/usr/bin/env python3
"""
Build script to compile individual tool configs into tools.json
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add the src directory to path so we can import local_mcp modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from local_mcp.config import Config, ScriptConfig
except ImportError:
    # If we can't import, we'll work without the config classes for now
    Config = None
    ScriptConfig = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_individual_tool_configs(config_dir: Path) -> Dict[str, Any]:
    """Load all individual tool configuration files."""
    tools_dir = config_dir / "tools"
    tools_config = {}
    
    if not tools_dir.exists():
        logger.warning(f"Tools config directory does not exist: {tools_dir}")
        return tools_config
    
    # Load all .json files in the tools directory
    for config_file in tools_dir.glob("*.json"):
        try:
            with open(config_file, 'r') as f:
                tool_data = json.load(f)
            
            # Extract tool name from filename
            tool_name = config_file.stem
            
            # Validate the structure
            if 'script_config' not in tool_data:
                logger.error(f"Invalid tool config structure in {config_file}: missing 'script_config'")
                continue
                
            # Use the script_config portion for the compiled tools.json
            script_config = tool_data['script_config'].copy()
            
            # Add tags from the top-level individual config to script_config
            if 'tags' in tool_data:
                script_config['tags'] = tool_data['tags']
            
            tools_config[tool_name] = script_config
            
            logger.info(f"Loaded config for tool: {tool_name}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {config_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading {config_file}: {e}")
    
    return tools_config


def build_tools_json(config_dir: Path, output_file: Path = None) -> bool:
    """Build the main tools.json from individual tool config files."""
    if output_file is None:
        output_file = config_dir / "tools.json"
    
    logger.info("Building tools.json from individual tool configurations...")
    
    # Load individual configs
    tools_config = load_individual_tool_configs(config_dir)
    
    if not tools_config:
        logger.warning("No individual tool configurations found. Creating empty tools.json.")
    
    # Filter out disabled tools
    enabled_tools = {}
    for tool_name, config in tools_config.items():
        if config.get('enabled', True):  # Default to enabled if not specified
            enabled_tools[tool_name] = config
        else:
            logger.info(f"Skipping disabled tool: {tool_name}")
    
    # Write the compiled configuration
    try:
        with open(output_file, 'w') as f:
            json.dump(enabled_tools, f, indent=2)
        
        logger.info(f"Successfully built tools.json with {len(enabled_tools)} enabled tools")
        logger.info(f"Output written to: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing tools.json: {e}")
        return False


def migrate_existing_tools_json(config_dir: Path) -> bool:
    """Migrate existing tools.json to individual tool config files."""
    tools_json_path = config_dir / "tools.json"
    tools_dir = config_dir / "tools"
    
    if not tools_json_path.exists():
        logger.info("No existing tools.json found to migrate")
        return True
    
    # Ensure tools directory exists
    tools_dir.mkdir(exist_ok=True)
    
    try:
        with open(tools_json_path, 'r') as f:
            tools_config = json.load(f)
        
        logger.info(f"Migrating {len(tools_config)} tools from tools.json to individual configs...")
        
        for tool_name, tool_config in tools_config.items():
            # Create individual tool config structure
            individual_config = {
                "enabled": tool_config.get('enabled', True),
                "last_modified": datetime.now().isoformat(),
                "auto_detected": True,
                "migrated_from_tools_json": True,
                "tags": tool_config.get('tags', []),  # Extract tags if they exist
                "script_config": tool_config
            }
            
            # Remove tags from script_config if they exist (since they're now at top level)
            if 'tags' in individual_config['script_config']:
                del individual_config['script_config']['tags']
            
            # Write individual config file
            config_file = tools_dir / f"{tool_name}.json"
            with open(config_file, 'w') as f:
                json.dump(individual_config, f, indent=2)
            
            logger.info(f"Migrated tool: {tool_name}")
        
        # Backup the original tools.json
        backup_path = config_dir / f"tools.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tools_json_path.rename(backup_path)
        logger.info(f"Original tools.json backed up to: {backup_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False


def main():
    """Main entry point for the build script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build tools.json from individual configurations")
    parser.add_argument("--config-dir", type=Path, default=Path(__file__).parent / "config",
                       help="Configuration directory path")
    parser.add_argument("--migrate", action="store_true",
                       help="Migrate existing tools.json to individual configs first")
    parser.add_argument("--output", type=Path,
                       help="Output file path (default: config/tools.json)")
    
    args = parser.parse_args()
    
    config_dir = args.config_dir.resolve()
    
    if not config_dir.exists():
        logger.error(f"Configuration directory does not exist: {config_dir}")
        return 1
    
    success = True
    
    # Run migration if requested
    if args.migrate:
        success = migrate_existing_tools_json(config_dir)
        if not success:
            logger.error("Migration failed")
            return 1
    
    # Build tools.json
    success = build_tools_json(config_dir, args.output)
    
    if success:
        logger.info("Build completed successfully!")
        return 0
    else:
        logger.error("Build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
