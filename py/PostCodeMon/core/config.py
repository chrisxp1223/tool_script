"""Configuration management for PostCodeMon."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
import json
from dataclasses import dataclass, field
from .errors import ConfigurationError


@dataclass
class ToolConfig:
    """Configuration for a specific Windows tool."""
    name: str
    executable_path: str
    default_args: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_attempts: int = 3
    environment_vars: Dict[str, str] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    working_directory: Optional[str] = None


@dataclass 
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    json_format: bool = False
    remote_endpoint: Optional[str] = None


@dataclass
class WrapperConfig:
    """Main wrapper configuration."""
    tools: Dict[str, ToolConfig] = field(default_factory=dict)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    global_timeout: int = 600
    max_concurrent_jobs: int = 10
    temp_directory: Optional[str] = None
    monitoring_enabled: bool = False
    metrics_endpoint: Optional[str] = None


class ConfigManager:
    """Manages hierarchical configuration for PostCodeMon."""
    
    CONFIG_FILENAME = "postcodemon.yaml"
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = config_path
        self._config: Optional[WrapperConfig] = None
        self._config_search_paths = self._get_config_search_paths()
    
    def _get_config_search_paths(self) -> List[Path]:
        """Get ordered list of paths to search for configuration files."""
        paths = []
        
        # 1. Explicit path provided
        if self.config_path:
            paths.append(Path(self.config_path))
        
        # 2. Current directory
        paths.append(Path.cwd() / self.CONFIG_FILENAME)
        
        # 3. User config directory
        if sys.platform == "win32":
            user_config = Path.home() / "AppData" / "Local" / "PostCodeMon" / self.CONFIG_FILENAME
        else:
            user_config = Path.home() / ".config" / "postcodemon" / self.CONFIG_FILENAME
        paths.append(user_config)
        
        # 4. System config directory
        if sys.platform == "win32":
            system_config = Path("C:/ProgramData/PostCodeMon") / self.CONFIG_FILENAME
        else:
            system_config = Path("/etc/postcodemon") / self.CONFIG_FILENAME
        paths.append(system_config)
        
        return paths
    
    def load_config(self) -> WrapperConfig:
        """Load configuration from files with hierarchical merging."""
        if self._config is not None:
            return self._config
        
        # Start with default configuration
        config_data = {}
        
        # Load configurations in reverse order (system -> user -> project -> explicit)
        for config_path in reversed(self._config_search_paths):
            if config_path.exists():
                try:
                    loaded_config = self._load_config_file(config_path)
                    config_data = self._merge_configs(config_data, loaded_config)
                except Exception as e:
                    raise ConfigurationError(
                        f"Failed to load configuration from {config_path}: {e}",
                        str(config_path)
                    )
        
        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)
        
        # Validate and create configuration object
        try:
            self._config = self._create_config_object(config_data)
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration: {e}")
        
        return self._config
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load a single configuration file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif config_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ConfigurationError(f"Unsupported configuration file format: {config_path.suffix}")
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        # Support common environment variable patterns
        env_mappings = {
            'POSTCODEMON_LOG_LEVEL': ('logging', 'level'),
            'POSTCODEMON_LOG_FILE': ('logging', 'file_path'),
            'POSTCODEMON_TIMEOUT': ('global_timeout',),
            'POSTCODEMON_MAX_JOBS': ('max_concurrent_jobs',),
            'POSTCODEMON_TEMP_DIR': ('temp_directory',),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to the nested configuration location
                current = config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Set the value with appropriate type conversion
                final_key = config_path[-1]
                if final_key in ['global_timeout', 'max_concurrent_jobs']:
                    current[final_key] = int(value)
                elif final_key in ['monitoring_enabled']:
                    current[final_key] = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    current[final_key] = value
        
        return config
    
    def _create_config_object(self, config_data: Dict[str, Any]) -> WrapperConfig:
        """Create WrapperConfig object from dictionary data."""
        # Extract tool configurations
        tools = {}
        if 'tools' in config_data:
            for tool_name, tool_data in config_data['tools'].items():
                tools[tool_name] = ToolConfig(
                    name=tool_name,
                    executable_path=tool_data.get('executable_path', ''),
                    default_args=tool_data.get('default_args', []),
                    timeout_seconds=tool_data.get('timeout_seconds', 300),
                    retry_attempts=tool_data.get('retry_attempts', 3),
                    environment_vars=tool_data.get('environment_vars', {}),
                    validation_rules=tool_data.get('validation_rules', {}),
                    working_directory=tool_data.get('working_directory')
                )
        
        # Extract logging configuration
        logging_data = config_data.get('logging', {})
        logging_config = LoggingConfig(
            level=logging_data.get('level', 'INFO'),
            format=logging_data.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=logging_data.get('file_path'),
            max_file_size=logging_data.get('max_file_size', 10485760),
            backup_count=logging_data.get('backup_count', 5),
            json_format=logging_data.get('json_format', False),
            remote_endpoint=logging_data.get('remote_endpoint')
        )
        
        return WrapperConfig(
            tools=tools,
            logging=logging_config,
            profiles=config_data.get('profiles', {}),
            global_timeout=config_data.get('global_timeout', 600),
            max_concurrent_jobs=config_data.get('max_concurrent_jobs', 10),
            temp_directory=config_data.get('temp_directory'),
            monitoring_enabled=config_data.get('monitoring_enabled', False),
            metrics_endpoint=config_data.get('metrics_endpoint')
        )
    
    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """Get configuration for a specific tool."""
        config = self.load_config()
        return config.tools.get(tool_name)
    
    def get_profile_config(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific profile."""
        config = self.load_config()
        return config.profiles.get(profile_name)
    
    def save_config(self, config: WrapperConfig, path: Optional[Union[str, Path]] = None) -> None:
        """Save configuration to file."""
        if path is None:
            path = self._config_search_paths[1]  # Use project-level config by default
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert configuration to dictionary
        config_dict = {
            'tools': {name: {
                'executable_path': tool.executable_path,
                'default_args': tool.default_args,
                'timeout_seconds': tool.timeout_seconds,
                'retry_attempts': tool.retry_attempts,
                'environment_vars': tool.environment_vars,
                'validation_rules': tool.validation_rules,
                'working_directory': tool.working_directory
            } for name, tool in config.tools.items()},
            'logging': {
                'level': config.logging.level,
                'format': config.logging.format,
                'file_path': config.logging.file_path,
                'max_file_size': config.logging.max_file_size,
                'backup_count': config.logging.backup_count,
                'json_format': config.logging.json_format,
                'remote_endpoint': config.logging.remote_endpoint
            },
            'profiles': config.profiles,
            'global_timeout': config.global_timeout,
            'max_concurrent_jobs': config.max_concurrent_jobs,
            'temp_directory': config.temp_directory,
            'monitoring_enabled': config.monitoring_enabled,
            'metrics_endpoint': config.metrics_endpoint
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)