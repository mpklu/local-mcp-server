"""
Script execution engine for Local MCP Server with individual venv support.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from .config import Config
from .dependency_manager import IndividualVenvManager

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""
    pass


class ToolExecutionResult:
    """Structured result from tool execution."""
    
    def __init__(self, success: bool, exit_code: int, stdout: str, stderr: str, 
                 execution_time: float, error_type: Optional[str] = None,
                 tool_metadata: Optional[Dict] = None):
        self.success = success
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time = execution_time
        self.error_type = error_type
        self.tool_metadata = tool_metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "execution_time": self.execution_time,
            "error_type": self.error_type,
            "tool_metadata": self.tool_metadata
        }
    
    def to_string(self) -> str:
        """Convert to human-readable string."""
        if self.success:
            return self.stdout
        else:
            error_msg = f"Error executing tool (exit code {self.exit_code})"
            if self.error_type:
                error_msg += f" - {self.error_type}"
            if self.stderr:
                error_msg += f":\n{self.stderr}"
            return error_msg


class ScriptExecutor:
    """Executes scripts safely with proper isolation and individual venvs."""
    
    def __init__(self, tools_dir: Path, config: Config):
        self.tools_dir = tools_dir
        self.config = config
        self.global_config = config.get_global_config()
        self.venv_manager = IndividualVenvManager(
            config_dir=config.config_dir,
            tools_dir=tools_dir
        )
    
    async def execute_script(self, script_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a script with given arguments using individual venvs."""
        import time
        
        start_time = time.time()
        logger.info(f"Executing script: {script_name}")
        
        # Get script configuration
        script_config = self.config.get_script_config(script_name)
        if not script_config:
            result = ToolExecutionResult(
                success=False, exit_code=-1, stdout="", stderr=f"Unknown script: {script_name}",
                execution_time=0, error_type="validation"
            )
            return result.to_string()
        
        if not script_config.enabled:
            result = ToolExecutionResult(
                success=False, exit_code=-1, stdout="", stderr=f"Script {script_name} is disabled",
                execution_time=0, error_type="validation"
            )
            return result.to_string()
        
        # Check confirmation if required
        if script_config.requires_confirmation:
            confirm = arguments.get('confirm', False)
            if not confirm:
                return (
                    f"Script {script_name} requires confirmation. "
                    f"Please set 'confirm': true to execute."
                )
        
        # Build script path
        script_path = self.tools_dir / script_config.script_path
        if not script_path.exists():
            result = ToolExecutionResult(
                success=False, exit_code=-1, stdout="", stderr=f"Script not found: {script_path}",
                execution_time=time.time() - start_time, error_type="validation"
            )
            return result.to_string()
        
        try:
            if script_config.script_type == "python":
                result = await self._execute_python_script_with_venv(
                    script_name, script_path, arguments, script_config
                )
            elif script_config.script_type == "shell":
                result = await self._execute_shell_script(
                    script_path, arguments, script_config
                )
            else:
                result = ToolExecutionResult(
                    success=False, exit_code=-1, stdout="", 
                    stderr=f"Unsupported script type: {script_config.script_type}",
                    execution_time=time.time() - start_time, error_type="validation"
                )
            
            result.execution_time = time.time() - start_time
            result.tool_metadata.update({
                "tool_name": script_name,
                "tool_type": script_config.script_type
            })
            
            return result.to_string()
            
        except Exception as e:
            result = ToolExecutionResult(
                success=False, exit_code=-1, stdout="", stderr=str(e),
                execution_time=time.time() - start_time, error_type="execution",
                tool_metadata={"tool_name": script_name, "tool_type": script_config.script_type}
            )
            logger.error(f"Error executing {script_name}: {e}")
            return result.to_string()
    
    async def _execute_python_script_with_venv(
        self, 
        tool_name: str,
        script_path: Path, 
        arguments: Dict[str, Any], 
        script_config
    ) -> ToolExecutionResult:
        """Execute a Python script with its own virtual environment."""
        
        # Ensure tool environment is ready
        tool_dir = script_path.parent
        env_ready, env_message = await self.venv_manager.ensure_tool_environment(tool_name, tool_dir)
        
        if not env_ready:
            return ToolExecutionResult(
                success=False, exit_code=-1, stdout="", stderr=env_message,
                execution_time=0, error_type="dependency",
                tool_metadata={"tool_name": tool_name, "venv_path": str(self.venv_manager.get_tool_venv_path(tool_name))}
            )
        
        # Get Python executable from tool's venv
        python_exe = self.venv_manager.get_tool_python_executable(tool_name)
        
        # Check if tool has run.py entry point, otherwise use script directly
        run_py_path = tool_dir / "run.py"
        if run_py_path.exists():
            cmd = [python_exe, str(run_py_path.resolve())]
            logger.info(f"Using run.py entry point for {tool_name}")
        else:
            cmd = [python_exe, str(script_path.resolve())]
            logger.info(f"Using direct script execution for {tool_name}")
        
        # Handle script-specific argument mapping
        cmd.extend(self._build_script_arguments(arguments))
        
        # Execute the script
        return await self._run_subprocess_structured(cmd, tool_dir, tool_name)
    
    async def _execute_shell_script(
        self, 
        script_path: Path, 
        arguments: Dict[str, Any], 
        script_config
    ) -> ToolExecutionResult:
        """Execute a shell script."""
        
        # Make sure script is executable
        script_path.chmod(script_path.stat().st_mode | 0o111)
        
        # Build command
        cmd = [str(script_path)]
        cmd.extend(self._build_script_arguments(arguments))
        
        return await self._run_subprocess_structured(cmd, script_path.parent, script_config.name)
    
    def _build_script_arguments(self, arguments: Dict[str, Any]) -> list:
        """Build command line arguments from input parameters."""
        args = []
        
        # Remove MCP-specific arguments
        filtered_args = {k: v for k, v in arguments.items() if k not in ['confirm', 'function', 'command']}
        
        # Check if a specific function/command is requested for Python Fire tools
        function_name = arguments.get('function') or arguments.get('command')
        if function_name:
            args.append(function_name)
        
        # Handle different argument patterns based on script analysis
        # For Python Fire tools, use --param=value format for named parameters
        
        for key, value in filtered_args.items():
            if key.startswith('--'):
                # Already has -- prefix
                args.append(f'{key}={value}')
            elif len(key) == 1:
                # Single letter flag
                args.extend([f'-{key}', str(value)])
            else:
                # Named parameter - use Fire's --param=value format
                args.append(f'--{key}={value}')
        
        return args
    
    async def _run_subprocess_structured(self, cmd: list, working_dir: Path, tool_name: str) -> ToolExecutionResult:
        """Run subprocess with structured result and proper isolation."""
        import time
        
        start_time = time.time()
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Prepare environment
        env = os.environ.copy()
        
        try:
            # Run the subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=env
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.global_config.timeout_seconds
                )
                
                stdout_text = stdout.decode() if stdout else ""
                stderr_text = stderr.decode() if stderr else ""
                
                execution_time = time.time() - start_time
                
                return ToolExecutionResult(
                    success=process.returncode == 0,
                    exit_code=process.returncode,
                    stdout=stdout_text,
                    stderr=stderr_text,
                    execution_time=execution_time,
                    error_type=None if process.returncode == 0 else "execution",
                    tool_metadata={"tool_name": tool_name}
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                
                return ToolExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Script execution timed out after {self.global_config.timeout_seconds} seconds",
                    execution_time=time.time() - start_time,
                    error_type="timeout",
                    tool_metadata={"tool_name": tool_name}
                )
                
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time,
                error_type="execution",
                tool_metadata={"tool_name": tool_name}
            )
    
    async def _run_subprocess(self, cmd: list, temp_dir: Path, script_name: str) -> str:
        """Legacy method for backward compatibility."""
        result = await self._run_subprocess_structured(cmd, temp_dir, script_name)
        return result.to_string()
    
    def _get_temp_dir(self) -> Path:
        """Get or create temporary directory for script outputs."""
        if self.global_config.temp_dir:
            temp_base = Path(self.global_config.temp_dir)
        else:
            temp_base = Path(tempfile.gettempdir())
        
        # Create subdirectory for this MCP server
        temp_dir = temp_base / "local_mcp_server"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique subdirectory for this execution
        unique_dir = temp_dir / f"exec_{os.getpid()}_{id(self)}"
        unique_dir.mkdir(parents=True, exist_ok=True)
        
        return unique_dir
    
    def cleanup_temp_files(self):
        """Clean up old temporary files based on retention policy."""
        # This could be implemented to clean up old files
        # based on the temp_retention_hours setting
        pass
