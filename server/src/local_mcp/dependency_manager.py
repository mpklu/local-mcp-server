"""
Individual Virtual Environment Dependency Management for Local MCP Server tools.
Each tool gets its own isolated virtual environment for complete dependency isolation.
"""

import asyncio
import json
import logging
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import venv

logger = logging.getLogger(__name__)


class IndividualVenvManager:
    """Manages individual virtual environments for each MCP tool."""
    
    def __init__(self, config_dir: Path, tools_dir: Path):
        self.config_dir = config_dir
        self.tools_dir = tools_dir
        self.venvs_dir = config_dir.parent / "venvs"  # local_mcp_server/venvs/
"""
Individual Virtual Environment Dependency Management for Local MCP Server tools.
Each tool gets its own isolated virtual environment for complete dependency isolation.
"""

import asyncio
import json
import logging
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import venv

logger = logging.getLogger(__name__)


class DependencyInstallationError(Exception):
    """Raised when dependency installation fails."""
    pass


class VenvCreationError(Exception):
    """Raised when virtual environment creation fails."""
    pass


class IndividualVenvManager:
    """Manages individual virtual environments for each MCP tool."""
    
    def __init__(self, config_dir: Path, tools_dir: Path):
        self.config_dir = config_dir
        self.tools_dir = tools_dir
        self.venvs_dir = (config_dir.parent / "venvs").resolve()  # local_mcp_server/venvs/
        self.venvs_dir.mkdir(exist_ok=True)
    
    async def ensure_tool_environment(self, tool_name: str, tool_path: Path) -> Tuple[bool, str]:
        """
        Ensure a tool's virtual environment is ready with all dependencies.
        
        Args:
            tool_name: Name of the tool
            tool_path: Path to the tool directory
            
        Returns:
            Tuple of (success, message/error)
        """
        try:
            venv_path = self.venvs_dir / tool_name
            
            # Check if venv exists and is valid
            if not self._venv_exists(venv_path):
                logger.info(f"Creating virtual environment for tool: {tool_name}")
                await self._create_tool_venv(tool_name, venv_path)
            
            # Get tool dependencies
            dependencies = self._get_tool_dependencies(tool_path)
            
            if dependencies:
                # Check and install missing dependencies
                missing_deps = await self._check_missing_dependencies(venv_path, dependencies)
                if missing_deps:
                    logger.info(f"Installing dependencies for {tool_name}: {missing_deps}")
                    await self._install_dependencies(venv_path, missing_deps)
            
            return True, f"Environment ready for {tool_name}"
            
        except Exception as e:
            error_msg = f"Failed to prepare environment for {tool_name}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_tool_python_executable(self, tool_name: str) -> str:
        """Get the Python executable path for a tool's venv."""
        venv_path = self.venvs_dir / tool_name
        return str(Path(self._get_python_executable(venv_path)).resolve())
    
    def get_tool_venv_path(self, tool_name: str) -> Path:
        """Get the virtual environment path for a tool."""
        return self.venvs_dir / tool_name
    
    async def cleanup_tool_venv(self, tool_name: str) -> bool:
        """Remove a tool's virtual environment."""
        try:
            venv_path = self.venvs_dir / tool_name
            if venv_path.exists():
                shutil.rmtree(venv_path)
                logger.info(f"Removed virtual environment for {tool_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup venv for {tool_name}: {e}")
            return False
    
    def list_tool_venvs(self) -> List[str]:
        """List all existing tool virtual environments."""
        if not self.venvs_dir.exists():
            return []
        return [d.name for d in self.venvs_dir.iterdir() if d.is_dir()]
    
    def _venv_exists(self, venv_path: Path) -> bool:
        """Check if virtual environment exists and is valid."""
        python_exe = Path(self._get_python_executable(venv_path))
        return python_exe.exists() and python_exe.is_file()
    
    async def _create_tool_venv(self, tool_name: str, venv_path: Path) -> None:
        """Create a new virtual environment for a tool."""
        try:
            venv_path.mkdir(parents=True, exist_ok=True)
            
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            
            # Upgrade pip in the new venv
            await self._run_pip_command(venv_path, ["install", "--upgrade", "pip"])
            
            logger.info(f"Created virtual environment for {tool_name} at {venv_path}")
            
        except Exception as e:
            raise VenvCreationError(f"Failed to create venv for {tool_name}: {e}")
    
    def _get_tool_dependencies(self, tool_path: Path) -> List[str]:
        """
        Get dependencies for a tool from requirements.txt or pyproject.toml.
        
        Args:
            tool_path: Path to the tool directory
            
        Returns:
            List of package names
        """
        dependencies = []
        
        # Check for requirements.txt
        req_file = tool_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before any version specifier)
                            pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                            if not self._is_stdlib_module(pkg_name):
                                dependencies.append(line.strip())  # Keep full spec for installation
            except Exception as e:
                logger.warning(f"Error reading requirements file {req_file}: {e}")
        
        # TODO: Add pyproject.toml support with tomli if needed
        
        return dependencies
    
    async def _check_missing_dependencies(self, venv_path: Path, dependencies: List[str]) -> List[str]:
        """Check which dependencies are missing in the venv."""
        missing = []
        python_exe = self._get_python_executable(venv_path)
        
        for dep in dependencies:
            # Extract package name for import check
            pkg_name = dep.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
            try:
                process = await asyncio.create_subprocess_exec(
                    python_exe, "-c", f"import {pkg_name}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                if process.returncode != 0:
                    missing.append(dep)
            except Exception:
                missing.append(dep)
        
        return missing
    
    async def _install_dependencies(self, venv_path: Path, dependencies: List[str]) -> None:
        """Install dependencies in the tool's virtual environment."""
        if not dependencies:
            return
        
        try:
            await self._run_pip_command(venv_path, ["install"] + dependencies)
        except Exception as e:
            raise DependencyInstallationError(f"Failed to install dependencies {dependencies}: {e}")
    
    async def _run_pip_command(self, venv_path: Path, args: List[str]) -> None:
        """Run pip command in the specified virtual environment."""
        python_exe = self._get_python_executable(venv_path)
        cmd = [python_exe, "-m", "pip"] + args
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        _, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise DependencyInstallationError(f"Pip command failed: {error_msg}")
        
        logger.info(f"Pip command successful: {' '.join(args)}")
    
    def _get_python_executable(self, venv_path: Path) -> str:
        """Get path to Python executable in virtual environment."""
        if sys.platform == "win32":
            return str(venv_path / "Scripts" / "python.exe")
        else:
            return str(venv_path / "bin" / "python")
    
    def _is_stdlib_module(self, module_name: str) -> bool:
        """Check if a module is part of the standard library."""
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'math', 'random',
            'hashlib', 'base64', 'urllib', 'http', 'subprocess', 'pathlib',
            'typing', 'collections', 'itertools', 'functools', 're',
            'logging', 'argparse', 'configparser', 'csv', 'xml', 'sqlite3'
        }
        return module_name in stdlib_modules


# Legacy alias for backward compatibility
DependencyManager = IndividualVenvManager