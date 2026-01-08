"""
BVM Configuration Manager

Supports loading configuration from file, including:
- BVM authentication credentials
- Platform configuration
- File paths
- Default parameters
"""

import json
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class BvmConfig:
    """BVM Configuration Manager"""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_file: Path to config file (supports .json or .yaml/.yml)
                        If not specified, searches in order:
                        1. ./bvm_config.yaml
                        2. ./bvm_config.yml
                        3. ./bvm_config.json
                        4. ~/.bvm/config.yaml
        """
        self.config_file = config_file or self._find_config_file()
        self.config = self._load_config()

    def _find_config_file(self) -> str:
        """Automatically find configuration file"""
        search_paths = [
            "./bvm_config.yaml",
            "./bvm_config.yml",
            "./bvm_config.json",
            os.path.expanduser("~/.bvm/config.yaml"),
        ]

        for path in search_paths:
            if os.path.exists(path):
                return path

        # If not found, create default config file
        return self._create_default_config()

    def _create_default_config(self) -> str:
        """Create default configuration file"""
        default_config = {
            "bvm": {
                "username": "your_username",
                "password": "your_password",
                "base_url": "http://bvm/"
            },
            "paths": {
                "binary_dir": "D:\\BVM\\binaries",
                "download_dir": "D:\\BVM\\downloads",
                "token_dir": "D:\\BVM\\tokens"
            },
            "platform": {
                "processor_name": "Rembrandt - Family 19h",
                "platform_name": "Rev_RMB_Mayan_Insyde_EDKII",
                "psp_config": "RMB"
            },
            "defaults": {
                "base_bios_type": "PI BIOS",
                "purpose": "BVM API automation",
                "sign_type": "NOSIGN",
                "sign_hp": "0"
            }
        }

        config_path = "./bvm_config.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        print(f"Created default config file: {config_path}")
        print("Please edit the file and update your credentials.")
        return config_path

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        file_ext = os.path.splitext(self.config_file)[1].lower()

        with open(self.config_file, 'r', encoding='utf-8') as f:
            if file_ext == '.json':
                return json.load(f)
            elif file_ext in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config file format: {file_ext}")

    # ==================== BVM Authentication ==================== #

    @property
    def username(self) -> str:
        """BVM username"""
        return self.config['bvm']['username']

    @property
    def password(self) -> str:
        """BVM password"""
        return self.config['bvm']['password']

    @property
    def base_url(self) -> str:
        """BVM server URL"""
        return self.config['bvm'].get('base_url', 'http://bvm/')

    # ==================== File paths ==================== #

    @property
    def binary_dir(self) -> Path:
        """Binary files directory"""
        path = Path(self.config['paths']['binary_dir'])
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def download_dir(self) -> Path:
        """Download directory"""
        path = Path(self.config['paths']['download_dir'])
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def token_dir(self) -> Path:
        """Token files directory (For BIOS signing)"""
        path = Path(self.config['paths']['token_dir'])
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_binary_path(self, filename: str) -> str:
        """
        Get full path for binary file

        Args:
            filename: Filename

        Returns:
            Full path
        """
        return str(self.binary_dir / filename)

    def get_download_path(self, filename: str) -> str:
        """
        Get full path for download file

        Args:
            filename: Filename

        Returns:
            Full path
        """
        return str(self.download_dir / filename)

    def get_token_path(self, filename: str) -> str:
        """
        Get full path for token file

        Args:
            filename: Token filename

        Returns:
            Full path
        """
        return str(self.token_dir / filename)

    # ==================== Platform configuration ==================== #

    @property
    def processor_name(self) -> str:
        """Processor name"""
        return self.config['platform']['processor_name']

    @property
    def platform_name(self) -> str:
        """Platform name"""
        return self.config['platform']['platform_name']

    @property
    def psp_config(self) -> str:
        """PSP Configuration"""
        return self.config['platform']['psp_config']

    # ==================== Default values ==================== #

    @property
    def base_bios_type(self) -> str:
        """Default BIOS type"""
        return self.config['defaults'].get('base_bios_type', 'PI BIOS')

    @property
    def purpose(self) -> str:
        """Default purpose"""
        return self.config['defaults'].get('purpose', 'BVM API automation')

    @property
    def sign_type(self) -> str:
        """Default sign type"""
        return self.config['defaults'].get('sign_type', 'NOSIGN')

    @property
    def sign_hp(self) -> str:
        """Default sign_hp"""
        return self.config['defaults'].get('sign_hp', '0')

    # ==================== Utility methods ==================== #

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get arbitrary config value (Supports dot notation path)

        Args:
            key: Configuration key (For example: "bvm.username" or "paths.binary_dir")
            default: Default values

        Returns:
            Configuration value

        Example:
            >>> config.get("bvm.username")
            "lahan"
            >>> config.get("paths.binary_dir")
            "D:\\BVM\\binaries"
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value (Supports dot notation path)

        Args:
            key: Configuration key
            value: Configuration value

        Example:
            >>> config.set("bvm.username", "new_user")
        """
        keys = key.split('.')
        target = self.config

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value

    def save(self, filepath: Optional[str] = None) -> None:
        """
        Save configuration to file

        Args:
            filepath: Save path (If not specified, use original config file)
        """
        filepath = filepath or self.config_file
        file_ext = os.path.splitext(filepath)[1].lower()

        with open(filepath, 'w', encoding='utf-8') as f:
            if file_ext == '.json':
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            elif file_ext in ['.yaml', '.yml']:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

        print(f"Config saved to: {filepath}")

    def print_config(self) -> None:
        """Print current configuration (Hide password)"""
        config_copy = self.config.copy()
        if 'bvm' in config_copy and 'password' in config_copy['bvm']:
            config_copy['bvm']['password'] = '***'

        print(yaml.dump(config_copy, default_flow_style=False, allow_unicode=True))


# ==================== Usage example ==================== #
if __name__ == "__main__":
    # Load configuration
    config = BvmConfig()

    print("=== BVM Configuration ===")
    config.print_config()

    print("\n=== Path Examples ===")
    print(f"Binary path for SMU.bin: {config.get_binary_path('SMU.bin')}")
    print(f"Download path for output.FD: {config.get_download_path('output.FD')}")
    print(f"Token path for token.stkn: {config.get_token_path('token.stkn')}")

    print("\n=== Direct Access ===")
    print(f"Username: {config.username}")
    print(f"Platform: {config.platform_name}")
    print(f"Binary Dir: {config.binary_dir}")
