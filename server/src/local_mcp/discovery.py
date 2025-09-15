"""
Script discovery and tool registration for Local MCP Server.
"""

import ast
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.types import Tool

from .config import Config, ScriptConfig

logger = logging.getLogger(__name__)


class ScriptDiscovery:
    """Discovers and analyzes scripts in the tools directory."""
    
    def __init__(self, tools_dir: Path, config: Config):
        self.tools_dir = tools_dir
        self.config = config
        self._discovered_scripts: Dict[str, Dict[str, Any]] = {}
    
    async def discover_scripts(self, force_full: bool = False) -> Dict[str, Dict[str, Any]]:
        """Discover all executable scripts in the tools directory.
        
        Args:
            force_full: If True, perform full rediscovery. If False, use incremental discovery.
        """
        logger.info(f"Discovering scripts in: {self.tools_dir}")
        
        if not force_full:
            # Try incremental discovery first
            if self._try_incremental_discovery():
                logger.info("Used incremental discovery - no changes detected")
                return self._discovered_scripts
        
        logger.info("Performing full script discovery")
        return await self._full_discovery()
    
    def _try_incremental_discovery(self) -> bool:
        """Try to use incremental discovery based on file modification times.
        
        Returns:
            True if incremental discovery was successful, False if full discovery is needed.
        """
        # Load existing configuration
        if not self._load_existing_configurations():
            logger.info("No existing configurations found - full discovery required")
            return False
        
        # Check if any script files have been modified since last discovery
        last_discovery_time = self._get_last_discovery_time()
        if last_discovery_time is None:
            logger.info("No discovery timestamp found - full discovery required")
            return False
        
        # Check for file changes
        if self._has_file_changes_since(last_discovery_time):
            logger.info("File changes detected - full discovery required")
            return False
        
        # Incremental discovery successful
        return True
    
    async def _full_discovery(self) -> Dict[str, Dict[str, Any]]:
        """Perform full script discovery."""
        
        # Find Python scripts
        python_scripts = list(self.tools_dir.rglob("*.py"))
        shell_scripts = []
        
        # Find shell scripts (executable files without .py extension)
        for item in self.tools_dir.rglob("*"):
            if (item.is_file() and 
                not item.name.endswith('.py') and
                not item.name.startswith('.') and
                item.stat().st_mode & 0o111):  # Check if executable
                shell_scripts.append(item)
        
        # Filter out unwanted scripts
        python_scripts = self._filter_scripts(python_scripts)
        shell_scripts = self._filter_scripts(shell_scripts)
        
        # Analyze each script
        for script_path in python_scripts:
            await self._analyze_python_script(script_path)
        
        for script_path in shell_scripts:
            await self._analyze_shell_script(script_path)
        
        # Save discovered configurations
        self.config.save_tools_config()
        self._save_discovery_timestamp()
        
        logger.info(f"Discovered {len(self._discovered_scripts)} scripts")
        return self._discovered_scripts
    
    async def load_existing_tools(self):
        """Load tools from existing configuration without rediscovery."""
        logger.info("Loading existing tool configurations")
        self._load_existing_configurations()
        logger.info(f"Loaded {len(self._discovered_scripts)} existing tools")
    
    def _load_existing_configurations(self) -> bool:
        """Load existing configurations from tools.json.
        
        Returns:
            True if configurations were loaded successfully, False otherwise.
        """
        try:
            tools_config = self.config.get_all_script_configs()
            if not tools_config:
                return False
            
            # Rebuild _discovered_scripts from existing configuration
            self._discovered_scripts = {}
            for tool_name, config in tools_config.items():
                # Create a script_info structure similar to what discovery creates
                script_path = self.tools_dir / config.script_path
                if script_path.exists():
                    self._discovered_scripts[tool_name] = {
                        'config': config,
                        'metadata': {
                            'description': config.description,
                            'parameters': config.parameters,
                            'interactive': config.interactive,
                            'examples': config.examples
                        },
                        'full_path': script_path
                    }
            
            return len(self._discovered_scripts) > 0
            
        except Exception as e:
            logger.warning(f"Failed to load existing configurations: {e}")
            return False
    
    def _get_last_discovery_time(self) -> Optional[float]:
        """Get the timestamp of the last discovery run."""
        timestamp_file = self.config.config_dir / ".discovery_timestamp"
        try:
            if timestamp_file.exists():
                return float(timestamp_file.read_text().strip())
        except Exception as e:
            logger.warning(f"Failed to read discovery timestamp: {e}")
        return None
    
    def _save_discovery_timestamp(self):
        """Save the current timestamp as the last discovery time."""
        timestamp_file = self.config.config_dir / ".discovery_timestamp"
        try:
            timestamp_file.write_text(str(time.time()))
        except Exception as e:
            logger.warning(f"Failed to save discovery timestamp: {e}")
    
    def _has_file_changes_since(self, last_discovery_time: float) -> bool:
        """Check if any files in the tools directory have been modified since the given time.
        
        Args:
            last_discovery_time: Unix timestamp of last discovery
            
        Returns:
            True if changes detected, False otherwise
        """
        try:
            # Check for new/modified Python scripts
            for script_path in self.tools_dir.rglob("*.py"):
                if script_path.stat().st_mtime > last_discovery_time:
                    logger.info(f"Modified Python script detected: {script_path}")
                    return True
            
            # Check for new/modified shell scripts (limit depth to avoid infinite recursion)
            for root in [self.tools_dir] + [d for d in self.tools_dir.iterdir() if d.is_dir()]:
                for item in root.rglob("*"):
                    if (item.is_file() and 
                        not item.name.endswith('.py') and
                        not item.name.startswith('.') and
                        not str(item).endswith('.pyc') and  # Skip python cache files
                        item.stat().st_mode & 0o111 and  # executable
                        item.stat().st_mtime > last_discovery_time):
                        logger.info(f"Modified shell script detected: {item}")
                        return True
                    
                    # Limit recursion depth
                    if len(item.parts) - len(self.tools_dir.parts) > 3:
                        break
                        
            return False
            
        except Exception as e:
            logger.warning(f"Error checking file changes: {e}")
            return True  # Assume changes if we can't check
    
    def _filter_scripts(self, scripts: List[Path]) -> List[Path]:
        """Filter out unwanted scripts like build artifacts, git hooks, etc."""
        filtered = []
        
        # Exclude patterns
        exclude_patterns = [
            '.build/',
            '.git/',
            '__pycache__/',
            '/hooks/',
            '.sample',
            'ISSUE_TEMPLATE',
            'checkouts/',
            'repositories/',
            '/gyb.py',
            '/build-asm.py'
        ]
        
        for script in scripts:
            script_str = str(script)
            
            # Skip if matches exclude patterns
            if any(pattern in script_str for pattern in exclude_patterns):
                continue
                
            # Skip files that are clearly not meant to be executed directly
            if script.name.endswith(('.sample', '.md', '.txt', '.json')):
                continue
                
            filtered.append(script)
        
        return filtered
    
    async def _analyze_python_script(self, script_path: Path):
        """Analyze a Python script to extract metadata."""
        try:
            relative_path = script_path.relative_to(self.tools_dir)
            script_name = self._generate_script_name(relative_path)
            
            # Skip if already configured and enabled
            existing_config = self.config.get_script_config(script_name)
            if existing_config and not existing_config.enabled:
                return
            
            # Read and parse the script
            content = script_path.read_text(encoding='utf-8')
            
            # Extract metadata
            metadata = self._extract_python_metadata(content, script_path)
            
            # Create or update configuration
            if existing_config:
                # Update existing config with new metadata
                config = existing_config
                if not config.description and metadata.get('description'):
                    config.description = metadata['description']
            else:
                # Create new configuration
                config = self.config.create_default_script_config(
                    name=script_name,
                    script_path=str(relative_path),
                    script_type="python",
                    description=metadata.get('description', ''),
                    parameters=metadata.get('parameters', []),
                    examples=metadata.get('examples', []),
                    interactive=metadata.get('interactive', False),
                    dependencies=metadata.get('dependencies', [])
                )
            
            self._discovered_scripts[script_name] = {
                'config': config,
                'metadata': metadata,
                'full_path': script_path
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing Python script {script_path}: {e}")
    
    async def _analyze_shell_script(self, script_path: Path):
        """Analyze a shell script to extract metadata."""
        try:
            relative_path = script_path.relative_to(self.tools_dir)
            script_name = self._generate_script_name(relative_path)
            
            # Skip if already configured and disabled
            existing_config = self.config.get_script_config(script_name)
            if existing_config and not existing_config.enabled:
                return
            
            # Read the script
            content = script_path.read_text(encoding='utf-8')
            
            # Extract metadata
            metadata = self._extract_shell_metadata(content, script_path)
            
            # Create or update configuration
            if existing_config:
                config = existing_config
                if not config.description and metadata.get('description'):
                    config.description = metadata['description']
                # Update parameters if they were detected
                if metadata.get('parameters'):
                    config.parameters = metadata['parameters']
                # Update interactive flag if detected
                if metadata.get('interactive') is not None:
                    config.interactive = metadata['interactive']
                # Update examples if detected
                if metadata.get('examples'):
                    config.examples = metadata['examples']
            else:
                config = self.config.create_default_script_config(
                    name=script_name,
                    script_path=str(relative_path),
                    script_type="shell",
                    description=metadata.get('description', ''),
                    parameters=metadata.get('parameters', []),
                    examples=metadata.get('examples', []),
                    interactive=metadata.get('interactive', False)
                )
            
            self._discovered_scripts[script_name] = {
                'config': config,
                'metadata': metadata,
                'full_path': script_path
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing shell script {script_path}: {e}")
    
    def _generate_script_name(self, relative_path: Path) -> str:
        """Generate a unique tool name from script path."""
        # Replace path separators with underscores and remove extension
        name = str(relative_path).replace('/', '_').replace('\\', '_')
        if name.endswith('.py'):
            name = name[:-3]
        
        # Remove other file extensions that might be problematic
        extensions_to_remove = ['.sh', '.bash', '.zsh', '.fish', '.ps1']
        for ext in extensions_to_remove:
            if name.endswith(ext):
                name = name[:-len(ext)]
                break
        
        # Ensure name only contains valid characters for MCP
        # Pattern: ^[a-zA-Z0-9_-]{1,64}$
        import re
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        
        # Ensure it doesn't start with numbers or special chars
        if name and name[0] not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            name = f"tool_{name}"
        
        # Limit to 64 characters
        if len(name) > 64:
            name = name[:64]
        
        # Ensure it's not empty
        if not name:
            name = "unnamed_tool"
            
        return name
    
    def _extract_python_metadata(self, content: str, script_path: Path) -> Dict[str, Any]:
        """Extract metadata from Python script."""
        metadata = {
            'description': '',
            'parameters': [],
            'examples': [],
            'dependencies': [],
            'interactive': False
        }
        
        try:
            # Parse AST to extract docstring and analyze code
            tree = ast.parse(content)
            
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant)):
                docstring = tree.body[0].value.value
                if isinstance(docstring, str):
                    metadata.update(self._parse_docstring(docstring))
            
            # Look for argparse usage to detect parameters
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check for argparse.ArgumentParser usage
                    if (hasattr(node.func, 'attr') and node.func.attr == 'add_argument'):
                        metadata['parameters'].extend(self._extract_argparse_params(node))
                    
                    # Check for input() calls (interactive scripts)
                    if (hasattr(node.func, 'id') and node.func.id == 'input'):
                        metadata['interactive'] = True
        
        except Exception as e:
            logger.debug(f"Error parsing Python AST for {script_path}: {e}")
        
        # Look for import statements to detect dependencies
        metadata['dependencies'] = self._extract_python_dependencies(content)
        
        return metadata
    
    def _extract_shell_metadata(self, content: str, script_path: Path) -> Dict[str, Any]:
        """Extract metadata from shell script."""
        metadata = {
            'description': '',
            'parameters': [],
            'examples': [],
            'interactive': False
        }
        
        lines = content.split('\n')
        
        # Look for description in comments
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            if line.startswith('#') and 'description' in line.lower():
                # Extract description from comment
                desc_match = re.search(r'description[:\s]*(.+)', line, re.IGNORECASE)
                if desc_match:
                    metadata['description'] = desc_match.group(1).strip()
        
        # Detect positional parameters ($1, $2, etc.)
        parameters = self._detect_shell_parameters(content, lines)
        metadata['parameters'] = parameters
        
        # Check for interactive input (read commands)
        if 'read ' in content or 'read -' in content:
            metadata['interactive'] = True
        
        # Look for usage function
        usage_match = re.search(r'usage\(\)\s*{(.+?)}', content, re.DOTALL)
        if usage_match:
            usage_text = usage_match.group(1)
            if 'Usage:' in usage_text:
                metadata['examples'] = [usage_text.strip()]
        
        return metadata
    
    def _detect_shell_parameters(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect parameters from shell script by analyzing positional arguments."""
        parameters = []
        param_assignments = {}
        
        # Look for variable assignments with positional parameters ($1, $2, etc.)
        for line in lines[:50]:  # Check first 50 lines for assignments
            line = line.strip()
            
            # Pattern: VARIABLE=$1, VARIABLE=$2, etc.
            assignment_match = re.match(r'^(\w+)=\$(\d+)', line)
            if assignment_match:
                var_name = assignment_match.group(1)
                param_num = int(assignment_match.group(2))
                param_assignments[param_num] = var_name
        
        # Also look for direct usage of $1, $2, etc. (but don't override existing assignments)
        for match in re.finditer(r'\$(\d+)', content):
            param_num = int(match.group(1))
            if param_num not in param_assignments and param_num > 0:  # Ignore $0 (script name)
                param_assignments[param_num] = f"arg{param_num}"
        
        # Convert to parameter list
        for param_num in sorted(param_assignments.keys()):
            if param_num == 0:  # Skip $0 (script name)
                continue
                
            var_name = param_assignments[param_num]
            
            # Try to infer parameter purpose from variable name
            description = self._infer_parameter_description(var_name)
            required = True  # Shell positional parameters are typically required
            
            parameters.append({
                "name": var_name.lower(),
                "type": "string",
                "description": description,
                "required": required
            })
        
        return parameters
    
    def _infer_parameter_description(self, var_name: str) -> str:
        """Infer parameter description from variable name."""
        name_lower = var_name.lower()
        
        # Common patterns
        if 'path' in name_lower:
            return f"Path to the {name_lower.replace('_path', '').replace('path', '')} directory or file".strip()
        elif 'dir' in name_lower:
            return f"Directory path for {name_lower.replace('_dir', '').replace('dir', '')}".strip()
        elif 'file' in name_lower:
            return f"File path for {name_lower.replace('_file', '').replace('file', '')}".strip()
        elif 'url' in name_lower:
            return f"URL for {name_lower.replace('_url', '').replace('url', '')}".strip()
        elif 'name' in name_lower:
            return f"Name for {name_lower.replace('_name', '').replace('name', '')}".strip()
        else:
            return f"Input parameter: {var_name}"
    
    def _parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse Python docstring to extract metadata."""
        result = {
            'description': '',
            'examples': []
        }
        
        lines = docstring.strip().split('\n')
        if lines:
            # First non-empty line is usually the description
            result['description'] = lines[0].strip()
        
        # Look for examples section
        in_examples = False
        current_example = []
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('example'):
                in_examples = True
                continue
            elif in_examples:
                if line and not line.startswith(' '):
                    # End of examples section
                    if current_example:
                        result['examples'].append('\n'.join(current_example))
                    break
                elif line:
                    current_example.append(line)
        
        if current_example:
            result['examples'].append('\n'.join(current_example))
        
        return result
    
    def _extract_argparse_params(self, node: ast.Call) -> List[Dict[str, Any]]:
        """Extract parameter info from argparse add_argument call."""
        # This is a simplified extraction - could be enhanced
        params = []
        # Implementation would analyze the AST node to extract parameter details
        return params
    
    def _extract_python_dependencies(self, content: str) -> List[str]:
        """Extract import dependencies from Python script."""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for import statements
            if line.startswith('import ') or line.startswith('from '):
                # Extract module name
                if line.startswith('import '):
                    module = line[7:].split()[0]
                else:  # from ... import
                    module = line.split()[1]
                
                # Skip standard library modules (simplified check)
                if module not in ['os', 'sys', 'json', 'argparse', 'pathlib', 're']:
                    dependencies.append(module)
        
        return dependencies
    
    async def get_available_tools(self) -> List[Tool]:
        """Get list of available tools for MCP."""
        tools = []
        
        for script_name, script_info in self._discovered_scripts.items():
            config = script_info['config']
            
            if not config.enabled:
                continue
            
            # Build parameter schema
            properties = {}
            required = []
            
            # Add common parameters that all scripts might need
            properties["confirm"] = {
                "type": "boolean",
                "description": "Confirm execution of this script",
                "default": False
            }
            
            if config.requires_confirmation:
                required.append("confirm")
            
            # Add script-specific parameters based on analysis
            for param in config.parameters:
                param_name = param.get('name', 'value')
                properties[param_name] = {
                    "type": param.get('type', 'string'),
                    "description": param.get('description', f'Parameter for {script_name}')
                }
                if param.get('required', False):
                    required.append(param_name)
            
            tool = Tool(
                name=script_name,
                description=config.description or f"Execute {config.script_type} script: {config.script_path}",
                inputSchema={
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            )
            
            tools.append(tool)
        
        return tools
