"""
Configuration management for Local MCP Server.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WorkspaceConfig(BaseModel):
    """Workspace and security configuration for a tool."""
    # Path security settings
    allowed_paths: List[str] = Field(default_factory=lambda: ['{TOOL_DIR}/workspace'])
    allow_absolute_paths: bool = False
    follow_symlinks: bool = True
    create_workspace: bool = True
    
    # String validation settings
    max_string_length: Optional[int] = None
    check_prompt_injection: bool = True
    
    # Output settings
    max_output_length: Optional[int] = None


class ScriptConfig(BaseModel):
    """Configuration for a single script."""
    name: str
    title: Optional[str] = None  # Human-friendly display name (MCP 1.25.0+)
    description: str
    script_path: str
    script_type: str  # "python" or "shell"
    requires_confirmation: bool = True
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    interactive: bool = False
    wrapper_function: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True
    workspace_config: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    
    # Tool annotations (MCP 1.25.0+)
    read_only: bool = False  # Tool only reads data, doesn't modify
    destructive: bool = False  # Tool performs destructive operations


class GlobalConfig(BaseModel):
    """Global configuration settings."""
    # Server configuration
    server_name: str = "local-mcp-server"
    server_version: str = "1.0.0"
    
    # Execution settings
    temp_dir: Optional[str] = None
    max_output_length: int = 10000
    timeout_seconds: int = 300
    auto_cleanup_temp: bool = True
    temp_retention_hours: int = 24
    
    # Logging settings
    log_dir: str = "config/logs"
    log_level: str = "INFO"
    enable_json_logging: bool = False
    enable_file_logging: bool = True
    enable_audit_logging: bool = True
    log_max_bytes: int = 10*1024*1024  # 10MB
    log_backup_count: int = 5
    
    # Redaction settings
    redact_sensitive_data: bool = True
    sensitive_keys: List[str] = Field(default_factory=list)
    scan_values_for_patterns: bool = True
    redaction_style: str = "full"  # full, partial, hint
    
    # Resource limits (Unix only)
    enable_resource_limits: bool = True
    max_cpu_seconds: int = 60  # CPU time limit per execution
    max_memory_mb: int = 512  # Memory limit in MB
    max_processes: int = 10  # Max number of child processes
    max_file_size_mb: int = 100  # Max file size a tool can create
    
    # Concurrent execution limits
    max_concurrent_executions: int = 5  # Max tools running at once
    
    # Rate limiting
    enable_rate_limiting: bool = True
    max_executions_per_minute: int = 10  # Per tool rate limit


class Config:
    """Configuration manager for the MCP server."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.tools_config_path = config_dir / "tools.json"
        self.global_config_path = config_dir / "global.json"
        self.overrides_config_path = config_dir / "overrides.json"
        
        self._tools_config: Dict[str, ScriptConfig] = {}
        self._global_config = GlobalConfig()
        self._overrides: Dict[str, Any] = {}
        
        self._load_configs()
    
    def _load_configs(self):
        """Load all configuration files."""
        # Load global config
        if self.global_config_path.exists():
            try:
                with open(self.global_config_path) as f:
                    data = json.load(f)
                self._global_config = GlobalConfig(**data)
                logger.info("Loaded global configuration")
            except Exception as e:
                logger.warning(f"Error loading global config: {e}")
        
        # Load tools config
        if self.tools_config_path.exists():
            try:
                with open(self.tools_config_path) as f:
                    data = json.load(f)
                for name, config_data in data.items():
                    self._tools_config[name] = ScriptConfig(**config_data)
                logger.info(f"Loaded {len(self._tools_config)} tool configurations")
            except Exception as e:
                logger.warning(f"Error loading tools config: {e}")
        
        # Load overrides
        if self.overrides_config_path.exists():
            try:
                with open(self.overrides_config_path) as f:
                    self._overrides = json.load(f)
                logger.info("Loaded configuration overrides")
            except Exception as e:
                logger.warning(f"Error loading overrides: {e}")
    
    def save_tools_config(self):
        """Save tools configuration to file."""
        try:
            data = {}
            for name, config in self._tools_config.items():
                data[name] = config.model_dump()
            
            with open(self.tools_config_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Saved tools configuration")
        except Exception as e:
            logger.error(f"Error saving tools config: {e}")
    
    def get_script_config(self, name: str) -> Optional[ScriptConfig]:
        """Get configuration for a specific script."""
        return self._tools_config.get(name)
    
    def set_script_config(self, name: str, config: ScriptConfig):
        """Set configuration for a specific script."""
        self._tools_config[name] = config
    
    def get_all_script_configs(self) -> Dict[str, ScriptConfig]:
        """Get all script configurations."""
        return self._tools_config.copy()
    
    def get_global_config(self) -> GlobalConfig:
        """Get global configuration."""
        return self._global_config
    
    def get_override(self, key: str, default: Any = None) -> Any:
        """Get a configuration override value."""
        return self._overrides.get(key, default)
    
    def is_script_enabled(self, name: str) -> bool:
        """Check if a script is enabled."""
        config = self.get_script_config(name)
        if config:
            return config.enabled
        # Default to enabled if no config exists
        return True
    
    def create_default_script_config(
        self,
        name: str,
        script_path: str,
        script_type: str,
        description: str = "",
        **kwargs
    ) -> ScriptConfig:
        """Create a default configuration for a discovered script."""
        config = ScriptConfig(
            name=name,
            description=description or f"Auto-discovered {script_type} script",
            script_path=script_path,
            script_type=script_type,
            **kwargs
        )
        self.set_script_config(name, config)
        return config
