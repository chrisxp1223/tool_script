"""Tests for the main ToolWrapper class."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml

from PostCodeMon.core.wrapper import ToolWrapper
from PostCodeMon.core.config import ToolConfig
from PostCodeMon.core.errors import (
    ConfigurationError, 
    ValidationError, 
    ToolNotFoundError,
    ToolExecutionError
)
from PostCodeMon.core.process import ProcessResult


class TestToolWrapper:
    """Test ToolWrapper functionality."""
    
    @pytest.fixture
    def temp_config(self):
        """Create a temporary configuration for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            
            test_config = {
                'tools': {
                    'test_tool': {
                        'executable_path': 'test_tool.exe',
                        'default_args': ['--verbose'],
                        'timeout_seconds': 30,
                        'retry_attempts': 2,
                        'environment_vars': {
                            'TEST_VAR': 'test_value'
                        },
                        'validation_rules': {
                            'required_args': {
                                'args': ['--input']
                            }
                        }
                    },
                    'simple_tool': {
                        'executable_path': 'simple.exe',
                        'default_args': [],
                        'timeout_seconds': 60
                    }
                },
                'logging': {
                    'level': 'DEBUG'
                },
                'global_timeout': 300,
                'max_concurrent_jobs': 5
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(test_config, f)
            
            yield config_path
    
    def test_wrapper_initialization(self, temp_config):
        """Test wrapper initialization with configuration."""
        wrapper = ToolWrapper(config_path=temp_config, tool_name='test_tool')
        
        assert wrapper.tool_name == 'test_tool'
        assert len(wrapper.config.tools) == 2
        assert 'test_tool' in wrapper.config.tools
        assert wrapper.config.max_concurrent_jobs == 5
        
        wrapper.shutdown()
    
    def test_validate_tool_config_success(self, temp_config):
        """Test successful tool configuration validation."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        tool_config = wrapper.validate_tool_config('test_tool')
        
        assert isinstance(tool_config, ToolConfig)
        assert tool_config.name == 'test_tool'
        assert tool_config.executable_path == 'test_tool.exe'
        assert tool_config.timeout_seconds == 30
        
        wrapper.shutdown()
    
    def test_validate_tool_config_not_found(self, temp_config):
        """Test validation failure for non-existent tool."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        with pytest.raises(ConfigurationError) as exc_info:
            wrapper.validate_tool_config('nonexistent_tool')
        
        assert "not configured" in str(exc_info.value)
        assert "Available tools" in str(exc_info.value)
        
        wrapper.shutdown()
    
    def test_validate_arguments_with_defaults(self, temp_config):
        """Test argument validation with default args merging."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        result_args = wrapper.validate_arguments('test_tool', ['--input', 'file.txt'])
        
        # Should merge default args with provided args
        assert '--verbose' in result_args
        assert '--input' in result_args
        assert 'file.txt' in result_args
        
        wrapper.shutdown()
    
    def test_validate_arguments_missing_required(self, temp_config):
        """Test validation failure for missing required arguments."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        with pytest.raises(ValidationError) as exc_info:
            wrapper.validate_arguments('test_tool', ['--other-arg'])
        
        assert "Required argument '--input' missing" in str(exc_info.value)
        
        wrapper.shutdown()
    
    @patch('PostCodeMon.core.process.ProcessManager.execute_tool')
    def test_execute_tool_success(self, mock_execute, temp_config):
        """Test successful tool execution."""
        # Mock successful execution
        mock_result = ProcessResult(
            return_code=0,
            stdout="Success output",
            stderr="",
            duration=1.5,
            command="test_tool.exe --verbose --input file.txt",
            tool_name="test_tool"
        )
        mock_execute.return_value = mock_result
        
        wrapper = ToolWrapper(config_path=temp_config)
        
        result = wrapper.execute_tool(
            tool_name='test_tool',
            args=['--input', 'file.txt']
        )
        
        assert result.success
        assert result.return_code == 0
        assert result.stdout == "Success output"
        assert result.duration == 1.5
        
        # Verify the process manager was called with correct parameters
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]['tool_name'] == 'test_tool'
        assert '--verbose' in call_args[1]['args']  # Default arg
        assert '--input' in call_args[1]['args']   # Provided arg
        
        wrapper.shutdown()
    
    @patch('PostCodeMon.core.process.ProcessManager.execute_tool')
    def test_execute_tool_with_retry(self, mock_execute, temp_config):
        """Test tool execution with retry logic."""
        # Mock first call fails, second succeeds
        mock_execute.side_effect = [
            ToolExecutionError("First attempt failed", 1, "Error message"),
            ProcessResult(
                return_code=0,
                stdout="Success on retry",
                stderr="",
                duration=2.0,
                command="test_tool.exe --verbose --input file.txt",
                tool_name="test_tool"
            )
        ]
        
        wrapper = ToolWrapper(config_path=temp_config)
        
        result = wrapper.execute_tool(
            tool_name='test_tool',
            args=['--input', 'file.txt']
        )
        
        assert result.success
        assert result.stdout == "Success on retry"
        assert mock_execute.call_count == 2  # Should have retried once
        
        wrapper.shutdown()
    
    @patch('PostCodeMon.core.process.ProcessManager.execute_tool')
    def test_execute_tool_all_retries_fail(self, mock_execute, temp_config):
        """Test tool execution when all retries fail."""
        # Mock all attempts fail
        mock_execute.side_effect = ToolExecutionError("All attempts failed", 1, "Error")
        
        wrapper = ToolWrapper(config_path=temp_config)
        
        with pytest.raises(ToolExecutionError) as exc_info:
            wrapper.execute_tool(
                tool_name='test_tool',
                args=['--input', 'file.txt']
            )
        
        assert "All attempts failed" in str(exc_info.value)
        # Should have tried the configured number of times (2 for test_tool)
        assert mock_execute.call_count == 2
        
        wrapper.shutdown()
    
    def test_execute_tool_dry_run(self, temp_config):
        """Test dry run mode."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        result = wrapper.execute_tool(
            tool_name='test_tool',
            args=['--input', 'file.txt'],
            dry_run=True
        )
        
        assert result.success
        assert "DRY RUN" in result.stdout
        assert result.duration == 0.0
        assert result.return_code == 0
        
        wrapper.shutdown()
    
    @patch('PostCodeMon.core.process.ProcessManager.execute_tool')
    def test_execute_batch(self, mock_execute, temp_config):
        """Test batch execution."""
        # Mock successful executions
        mock_execute.side_effect = [
            ProcessResult(0, "Output 1", "", 1.0, "cmd1", "simple_tool"),
            ProcessResult(0, "Output 2", "", 1.5, "cmd2", "simple_tool"),
            ProcessResult(1, "", "Error 3", 0.5, "cmd3", "simple_tool")  # One failure
        ]
        
        wrapper = ToolWrapper(config_path=temp_config)
        
        batch_args = [
            ['--arg1', 'value1'],
            ['--arg2', 'value2'],
            ['--arg3', 'value3']
        ]
        
        results = wrapper.execute_batch(
            tool_name='simple_tool',
            batch_args=batch_args,
            max_concurrent=2
        )
        
        assert len(results) == 3
        assert results[0].success
        assert results[1].success
        assert not results[2].success
        
        # Should have called execute_tool for each batch item
        assert mock_execute.call_count == 3
        
        wrapper.shutdown()
    
    def test_get_tool_info(self, temp_config):
        """Test getting tool information."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        tool_info = wrapper.get_tool_info('test_tool')
        
        assert tool_info['name'] == 'test_tool'
        assert tool_info['executable_path'] == 'test_tool.exe'
        assert tool_info['default_args'] == ['--verbose']
        assert tool_info['timeout_seconds'] == 30
        assert tool_info['retry_attempts'] == 2
        assert tool_info['environment_vars'] == {'TEST_VAR': 'test_value'}
        assert not tool_info['executable_exists']  # File doesn't actually exist
        
        wrapper.shutdown()
    
    def test_list_tools(self, temp_config):
        """Test listing all configured tools."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        tools_info = wrapper.list_tools()
        
        assert len(tools_info) == 2
        assert 'test_tool' in tools_info
        assert 'simple_tool' in tools_info
        
        assert tools_info['test_tool']['name'] == 'test_tool'
        assert tools_info['simple_tool']['name'] == 'simple_tool'
        
        wrapper.shutdown()
    
    @patch('PostCodeMon.core.process.ProcessManager.get_active_processes')
    def test_get_active_processes(self, mock_get_processes, temp_config):
        """Test getting active processes."""
        mock_processes = {
            'test_tool_123': {
                'pid': 123,
                'tool_name': 'test_tool',
                'status': 'running',
                'cpu_percent': 15.5,
                'memory_mb': 64.2
            }
        }
        mock_get_processes.return_value = mock_processes
        
        wrapper = ToolWrapper(config_path=temp_config)
        
        processes = wrapper.get_active_processes()
        
        assert processes == mock_processes
        mock_get_processes.assert_called_once()
        
        wrapper.shutdown()
    
    @patch('PostCodeMon.core.process.ProcessManager.kill_process')
    def test_kill_process(self, mock_kill, temp_config):
        """Test killing a process."""
        mock_kill.return_value = True
        
        wrapper = ToolWrapper(config_path=temp_config)
        
        result = wrapper.kill_process('test_tool', 123)
        
        assert result is True
        mock_kill.assert_called_once_with('test_tool', 123)
        
        wrapper.shutdown()
    
    def test_context_manager(self, temp_config):
        """Test using wrapper as context manager."""
        with ToolWrapper(config_path=temp_config) as wrapper:
            assert wrapper.tool_name is None
            assert len(wrapper.config.tools) == 2
        
        # Should have automatically called shutdown
        # (We can't easily test this without mocking, but the context manager should work)
    
    def test_reload_config(self, temp_config):
        """Test reloading configuration."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        # Verify initial configuration
        assert wrapper.config.max_concurrent_jobs == 5
        
        # Modify the config file
        updated_config = {
            'tools': {
                'test_tool': {
                    'executable_path': 'updated_tool.exe',
                    'timeout_seconds': 120
                }
            },
            'max_concurrent_jobs': 15
        }
        
        with open(temp_config, 'w') as f:
            yaml.dump(updated_config, f)
        
        # Reload configuration
        wrapper.reload_config()
        
        # Verify configuration was reloaded
        assert wrapper.config.max_concurrent_jobs == 15
        assert wrapper.config.tools['test_tool'].executable_path == 'updated_tool.exe'
        assert wrapper.config.tools['test_tool'].timeout_seconds == 120
        
        wrapper.shutdown()


class TestToolWrapperEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_wrapper_with_no_tools_configured(self):
        """Test wrapper behavior with empty configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "empty_config.yaml"
            
            empty_config = {
                'tools': {},
                'logging': {'level': 'INFO'}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(empty_config, f)
            
            wrapper = ToolWrapper(config_path=config_path)
            
            # Should raise error when trying to execute non-existent tool
            with pytest.raises(ConfigurationError):
                wrapper.execute_tool(tool_name='nonexistent')
            
            # List tools should return empty dict
            tools = wrapper.list_tools()
            assert tools == {}
            
            wrapper.shutdown()
    
    def test_execute_tool_no_tool_name(self):
        """Test execution without tool name and no default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            
            config = {
                'tools': {'test_tool': {'executable_path': 'test.exe'}},
                'logging': {'level': 'INFO'}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            
            wrapper = ToolWrapper(config_path=config_path)  # No default tool
            
            with pytest.raises(ConfigurationError) as exc_info:
                wrapper.execute_tool(args=['test'])  # No tool_name provided
            
            assert "No tool name provided" in str(exc_info.value)
            
            wrapper.shutdown()
    
    def test_shutdown_multiple_times(self, temp_config):
        """Test that shutdown can be called multiple times safely."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        # Should not raise exception on multiple shutdowns
        wrapper.shutdown()
        wrapper.shutdown()
        wrapper.shutdown()
    
    @patch('signal.signal')
    def test_signal_handler_registration(self, mock_signal, temp_config):
        """Test that signal handlers are registered properly."""
        wrapper = ToolWrapper(config_path=temp_config)
        
        # Should have registered signal handlers
        assert mock_signal.call_count >= 2  # At least SIGINT and SIGTERM
        
        wrapper.shutdown()