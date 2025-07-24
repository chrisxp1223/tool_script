"""Tests for configuration management."""

import os
import tempfile
import pytest
from pathlib import Path
import yaml

from PostCodeMon.core.config import ConfigManager, ToolConfig, LoggingConfig, WrapperConfig
from PostCodeMon.core.errors import ConfigurationError


class TestConfigManager:
    """Test configuration management functionality."""
    
    def test_default_config_creation(self):
        """Test that default configuration is created properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            config = config_manager.load_config()
            
            assert isinstance(config, WrapperConfig)
            assert isinstance(config.logging, LoggingConfig)
            assert config.global_timeout == 600
            assert config.max_concurrent_jobs == 10
    
    def test_yaml_config_loading(self):
        """Test loading configuration from YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            
            test_config = {
                'tools': {
                    'test_tool': {
                        'executable_path': '/path/to/tool.exe',
                        'default_args': ['--verbose'],
                        'timeout_seconds': 120,
                        'retry_attempts': 2
                    }
                },
                'logging': {
                    'level': 'DEBUG',
                    'json_format': True
                },
                'global_timeout': 300,
                'max_concurrent_jobs': 5
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(test_config, f)
            
            config_manager = ConfigManager(config_path)
            config = config_manager.load_config()
            
            assert len(config.tools) == 1
            assert 'test_tool' in config.tools
            
            tool_config = config.tools['test_tool']
            assert tool_config.executable_path == '/path/to/tool.exe'
            assert tool_config.default_args == ['--verbose']
            assert tool_config.timeout_seconds == 120
            assert tool_config.retry_attempts == 2
            
            assert config.logging.level == 'DEBUG'
            assert config.logging.json_format is True
            assert config.global_timeout == 300
            assert config.max_concurrent_jobs == 5
    
    def test_environment_variable_overrides(self):
        """Test that environment variables override configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variables
            os.environ['POSTCODEMON_LOG_LEVEL'] = 'ERROR'
            os.environ['POSTCODEMON_TIMEOUT'] = '1200'
            os.environ['POSTCODEMON_MAX_JOBS'] = '20'
            
            try:
                config_manager = ConfigManager()
                config = config_manager.load_config()
                
                assert config.logging.level == 'ERROR'
                assert config.global_timeout == 1200
                assert config.max_concurrent_jobs == 20
            finally:
                # Clean up environment variables
                for var in ['POSTCODEMON_LOG_LEVEL', 'POSTCODEMON_TIMEOUT', 'POSTCODEMON_MAX_JOBS']:
                    os.environ.pop(var, None)
    
    def test_hierarchical_config_merging(self):
        """Test that configurations are merged hierarchically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create base config
            base_config_path = Path(temp_dir) / "base_config.yaml"
            base_config = {
                'tools': {
                    'base_tool': {
                        'executable_path': '/base/tool.exe',
                        'timeout_seconds': 100
                    }
                },
                'global_timeout': 500,
                'logging': {
                    'level': 'INFO'
                }
            }
            
            with open(base_config_path, 'w') as f:
                yaml.dump(base_config, f)
            
            # Create override config
            override_config_path = Path(temp_dir) / "override_config.yaml"
            override_config = {
                'tools': {
                    'base_tool': {
                        'timeout_seconds': 200  # Override this value
                    },
                    'new_tool': {
                        'executable_path': '/new/tool.exe'
                    }
                },
                'global_timeout': 1000,  # Override this value
                'logging': {
                    'json_format': True  # Add new value
                }
            }
            
            with open(override_config_path, 'w') as f:
                yaml.dump(override_config, f)
            
            # Test merging by manually calling the merge function
            config_manager = ConfigManager()
            merged = config_manager._merge_configs(base_config, override_config)
            
            # Check that values were merged correctly
            assert merged['global_timeout'] == 1000  # Override value
            assert merged['logging']['level'] == 'INFO'  # Base value
            assert merged['logging']['json_format'] is True  # New value
            assert merged['tools']['base_tool']['executable_path'] == '/base/tool.exe'  # Base value
            assert merged['tools']['base_tool']['timeout_seconds'] == 200  # Override value
            assert 'new_tool' in merged['tools']  # New tool
    
    def test_invalid_config_file(self):
        """Test handling of invalid configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid YAML file
            config_path = Path(temp_dir) / "invalid.yaml"
            with open(config_path, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            config_manager = ConfigManager(config_path)
            
            with pytest.raises(ConfigurationError) as exc_info:
                config_manager.load_config()
            
            assert "Failed to load configuration" in str(exc_info.value)
    
    def test_get_tool_config(self):
        """Test retrieving specific tool configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            
            test_config = {
                'tools': {
                    'tool1': {
                        'executable_path': '/path/to/tool1.exe',
                        'default_args': ['--arg1']
                    },
                    'tool2': {
                        'executable_path': '/path/to/tool2.exe',
                        'default_args': ['--arg2']
                    }
                }
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(test_config, f)
            
            config_manager = ConfigManager(config_path)
            
            tool1_config = config_manager.get_tool_config('tool1')
            assert tool1_config is not None
            assert tool1_config.executable_path == '/path/to/tool1.exe'
            assert tool1_config.default_args == ['--arg1']
            
            tool2_config = config_manager.get_tool_config('tool2')
            assert tool2_config is not None
            assert tool2_config.executable_path == '/path/to/tool2.exe'
            
            nonexistent_config = config_manager.get_tool_config('nonexistent')
            assert nonexistent_config is None
    
    def test_save_config(self):
        """Test saving configuration to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "saved_config.yaml"
            
            # Create a configuration to save
            tool_config = ToolConfig(
                name='test_tool',
                executable_path='/path/to/tool.exe',
                default_args=['--verbose'],
                timeout_seconds=300,
                retry_attempts=3
            )
            
            logging_config = LoggingConfig(
                level='DEBUG',
                json_format=True
            )
            
            wrapper_config = WrapperConfig(
                tools={'test_tool': tool_config},
                logging=logging_config,
                global_timeout=600,
                max_concurrent_jobs=10
            )
            
            # Save the configuration
            config_manager = ConfigManager()
            config_manager.save_config(wrapper_config, config_path)
            
            # Verify the file was created and contains expected content
            assert config_path.exists()
            
            with open(config_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data['global_timeout'] == 600
            assert saved_data['max_concurrent_jobs'] == 10
            assert saved_data['logging']['level'] == 'DEBUG'
            assert saved_data['logging']['json_format'] is True
            assert 'test_tool' in saved_data['tools']
            assert saved_data['tools']['test_tool']['executable_path'] == '/path/to/tool.exe'


class TestToolConfig:
    """Test ToolConfig dataclass functionality."""
    
    def test_tool_config_creation(self):
        """Test creating ToolConfig instances."""
        config = ToolConfig(
            name='test_tool',
            executable_path='/path/to/tool.exe',
            default_args=['--verbose', '--output=json'],
            timeout_seconds=300,
            retry_attempts=3,
            environment_vars={'TOOL_HOME': '/tool'},
            validation_rules={'required_args': {'args': ['--input']}}
        )
        
        assert config.name == 'test_tool'
        assert config.executable_path == '/path/to/tool.exe'
        assert config.default_args == ['--verbose', '--output=json']
        assert config.timeout_seconds == 300
        assert config.retry_attempts == 3
        assert config.environment_vars == {'TOOL_HOME': '/tool'}
        assert config.validation_rules == {'required_args': {'args': ['--input']}}
    
    def test_tool_config_defaults(self):
        """Test ToolConfig default values."""
        config = ToolConfig(
            name='minimal_tool',
            executable_path='/path/to/tool.exe'
        )
        
        assert config.default_args == []
        assert config.timeout_seconds == 300
        assert config.retry_attempts == 3
        assert config.environment_vars == {}
        assert config.validation_rules == {}


class TestLoggingConfig:
    """Test LoggingConfig dataclass functionality."""
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert "%(asctime)s" in config.format
        assert config.file_path is None
        assert config.max_file_size == 10485760  # 10MB
        assert config.backup_count == 5
        assert config.json_format is False
        assert config.remote_endpoint is None
    
    def test_logging_config_custom_values(self):
        """Test LoggingConfig with custom values."""
        config = LoggingConfig(
            level="DEBUG",
            format="%(name)s - %(message)s",
            file_path="/custom/path/log.txt",
            max_file_size=5242880,  # 5MB
            backup_count=3,
            json_format=True,
            remote_endpoint="https://logs.example.com/api"
        )
        
        assert config.level == "DEBUG"
        assert config.format == "%(name)s - %(message)s"
        assert config.file_path == "/custom/path/log.txt"
        assert config.max_file_size == 5242880
        assert config.backup_count == 3
        assert config.json_format is True
        assert config.remote_endpoint == "https://logs.example.com/api"