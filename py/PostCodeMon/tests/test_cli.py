"""Tests for CLI interface."""

import json
import tempfile
import pytest
from pathlib import Path
from click.testing import CliRunner
import yaml

from PostCodeMon.cli.main import cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config():
    """Create a temporary configuration file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.yaml"
        
        test_config = {
            'tools': {
                'test_tool': {
                    'executable_path': 'echo',  # Use echo for cross-platform testing
                    'default_args': [],
                    'timeout_seconds': 30,
                    'retry_attempts': 1
                }
            },
            'logging': {
                'level': 'WARNING'  # Reduce log noise in tests
            },
            'global_timeout': 60
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        yield str(config_path)


@pytest.fixture
def batch_file():
    """Create a temporary batch file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("# Test batch file\n")
        f.write("Hello World\n")
        f.write("--help\n")
        f.write('["--version"]\n')
        
        batch_path = f.name
    
    yield batch_path
    
    # Cleanup
    Path(batch_path).unlink(missing_ok=True)


class TestCLIBasics:
    """Test basic CLI functionality."""
    
    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'PostCodeMon' in result.output
        assert 'Modern Python wrapper for Windows CLI tools' in result.output
        assert 'execute' in result.output
        assert 'batch' in result.output
        assert 'info' in result.output
        assert 'config' in result.output
        assert 'monitor' in result.output
    
    def test_cli_version(self, runner):
        """Test version command."""
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert '0.1.0' in result.output
    
    def test_cli_no_command_shows_help(self, runner):
        """Test that running CLI without command shows help."""
        result = runner.invoke(cli, [])
        
        assert result.exit_code == 0
        assert 'Usage:' in result.output


class TestExecuteCommand:
    """Test the execute command."""
    
    def test_execute_help(self, runner):
        """Test execute command help."""
        result = runner.invoke(cli, ['execute', '--help'])
        
        assert result.exit_code == 0
        assert 'Execute a Windows tool' in result.output
        assert '--tool' in result.output
        assert '--dry-run' in result.output
        assert '--timeout' in result.output
    
    def test_execute_dry_run(self, runner, temp_config):
        """Test execute command in dry-run mode."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'execute',
            '--tool', 'test_tool',
            '--dry-run',
            'hello', 'world'
        ])
        
        # Dry run should succeed even with non-existent executable
        assert result.exit_code == 0
        assert 'DRY RUN' in result.output
    
    def test_execute_with_environment_vars(self, runner, temp_config):
        """Test execute command with environment variables."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'execute',
            '--tool', 'test_tool',
            '--env', 'TEST_VAR=test_value',
            '--env', 'ANOTHER_VAR=another_value',
            '--dry-run',
            'test'
        ])
        
        assert result.exit_code == 0
        assert 'DRY RUN' in result.output
    
    def test_execute_json_output(self, runner, temp_config):
        """Test execute command with JSON output format."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'execute',
            '--tool', 'test_tool',
            '--output-format', 'json',
            '--dry-run',
            'test'
        ])
        
        assert result.exit_code == 0
        
        # Output should be valid JSON
        try:
            output_data = json.loads(result.output)
            assert 'return_code' in output_data
            assert 'success' in output_data
            assert 'command' in output_data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    def test_execute_yaml_output(self, runner, temp_config):
        """Test execute command with YAML output format."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'execute',
            '--tool', 'test_tool',
            '--output-format', 'yaml',
            '--dry-run',
            'test'
        ])
        
        assert result.exit_code == 0
        
        # Output should contain YAML-like content
        assert 'return_code:' in result.output
        assert 'success:' in result.output
        assert 'command:' in result.output
    
    def test_execute_save_output(self, runner, temp_config):
        """Test execute command with output saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.txt"
            
            result = runner.invoke(cli, [
                '--config', temp_config,
                'execute',
                '--tool', 'test_tool',
                '--save-output', str(output_file),
                '--dry-run',
                'test'
            ])
            
            assert result.exit_code == 0
            assert output_file.exists()
            
            # Check that output was saved
            saved_content = output_file.read_text()
            assert 'DRY RUN' in saved_content


class TestBatchCommand:
    """Test the batch command."""
    
    def test_batch_help(self, runner):
        """Test batch command help."""
        result = runner.invoke(cli, ['batch', '--help'])
        
        assert result.exit_code == 0
        assert 'Execute a tool multiple times' in result.output
        assert '--max-concurrent' in result.output
        assert '--fail-fast' in result.output
    
    def test_batch_execution_dry_run(self, runner, temp_config, batch_file):
        """Test batch execution with dry run."""
        # Create a config that works with echo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {
                'tools': {
                    'echo_tool': {
                        'executable_path': 'echo',
                        'default_args': [],
                        'timeout_seconds': 10
                    }
                },
                'logging': {'level': 'ERROR'}
            }
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            # Note: This test might fail if 'echo' is not available or behaves differently
            # The batch file contains various argument formats to test parsing
            result = runner.invoke(cli, [
                '--config', config_path,
                'batch',
                batch_file,
                '--tool', 'echo_tool',
                '--max-concurrent', '2'
            ])
            
            # The command should execute, though individual commands might fail
            # depending on system availability of echo command
            assert result.exit_code in [0, 1]  # Allow for partial failures
            
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    def test_batch_json_output(self, runner, temp_config, batch_file):
        """Test batch command with JSON output."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'batch',
            batch_file,
            '--tool', 'test_tool',
            '--output-format', 'json'
        ])
        
        # Command will likely fail due to missing executable, but should still produce output
        assert result.exit_code in [0, 1]
    
    def test_batch_nonexistent_file(self, runner, temp_config):
        """Test batch command with non-existent file."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'batch',
            '/nonexistent/file.txt',
            '--tool', 'test_tool'
        ])
        
        assert result.exit_code == 2  # Click error for invalid file


class TestInfoCommand:
    """Test the info command."""
    
    def test_info_help(self, runner):
        """Test info command help."""
        result = runner.invoke(cli, ['info', '--help'])
        
        assert result.exit_code == 0
        assert 'Show information about configured tools' in result.output
        assert '--list-all' in result.output
        assert '--tool' in result.output
    
    def test_info_list_all(self, runner, temp_config):
        """Test listing all tools."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'info',
            '--list-all'
        ])
        
        assert result.exit_code == 0
        assert 'test_tool' in result.output
    
    def test_info_specific_tool(self, runner, temp_config):
        """Test showing info for specific tool."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'info',
            '--tool', 'test_tool'
        ])
        
        assert result.exit_code == 0
        assert 'test_tool' in result.output
        assert 'echo' in result.output  # executable path
    
    def test_info_json_output(self, runner, temp_config):
        """Test info command with JSON output."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'info',
            '--tool', 'test_tool',
            '--output-format', 'json'
        ])
        
        assert result.exit_code == 0
        
        # Output should be valid JSON
        try:
            output_data = json.loads(result.output)
            assert 'name' in output_data
            assert 'executable_path' in output_data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    def test_info_nonexistent_tool(self, runner, temp_config):
        """Test info for non-existent tool."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'info',
            '--tool', 'nonexistent_tool'
        ])
        
        assert result.exit_code == 1
        assert 'Error:' in result.output


class TestConfigCommand:
    """Test the config command."""
    
    def test_config_help(self, runner):
        """Test config command help."""
        result = runner.invoke(cli, ['config', '--help'])
        
        assert result.exit_code == 0
        assert 'Manage PostCodeMon configuration' in result.output
        assert '--show' in result.output
        assert '--validate' in result.output
        assert '--create-example' in result.output
    
    def test_config_show(self, runner, temp_config):
        """Test showing current configuration."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'config',
            '--show'
        ])
        
        assert result.exit_code == 0
        assert 'test_tool' in result.output
        assert 'echo' in result.output
    
    def test_config_validate(self, runner, temp_config):
        """Test configuration validation."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'config',
            '--validate'
        ])
        
        assert result.exit_code == 0
        assert 'Configuration is valid' in result.output
    
    def test_config_create_example(self, runner):
        """Test creating example configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            example_path = Path(temp_dir) / "example_config.yaml"
            
            result = runner.invoke(cli, [
                'config',
                '--create-example', str(example_path)
            ])
            
            assert result.exit_code == 0
            assert example_path.exists()
            assert 'Example configuration created' in result.output
            
            # Verify the example file contains expected content
            with open(example_path) as f:
                example_config = yaml.safe_load(f)
            
            assert 'tools' in example_config
            assert 'logging' in example_config
            assert 'global_timeout' in example_config


class TestMonitorCommand:
    """Test the monitor command."""
    
    def test_monitor_help(self, runner):
        """Test monitor command help."""
        result = runner.invoke(cli, ['monitor', '--help'])
        
        assert result.exit_code == 0
        assert 'Monitor and manage running tool processes' in result.output
        assert '--list-processes' in result.output
        assert '--kill-tool' in result.output
        assert '--kill-pid' in result.output
    
    def test_monitor_list_processes(self, runner, temp_config):
        """Test listing processes (should be empty)."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'monitor',
            '--list-processes'
        ])
        
        assert result.exit_code == 0
        assert 'No active processes' in result.output
    
    def test_monitor_kill_nonexistent_tool(self, runner, temp_config):
        """Test killing processes for non-existent tool."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'monitor',
            '--kill-tool', 'nonexistent_tool'
        ])
        
        assert result.exit_code == 0
        assert 'No processes found' in result.output
    
    def test_monitor_kill_nonexistent_pid(self, runner, temp_config):
        """Test killing non-existent PID."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            'monitor',
            '--kill-pid', '999999'
        ])
        
        assert result.exit_code == 0
        assert 'Process not found' in result.output


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_invalid_config_file(self, runner):
        """Test CLI with invalid configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            invalid_config = f.name
        
        try:
            result = runner.invoke(cli, [
                '--config', invalid_config,
                'info',
                '--list-all'
            ])
            
            assert result.exit_code == 1
            assert 'Error:' in result.output
            
        finally:
            Path(invalid_config).unlink(missing_ok=True)
    
    def test_nonexistent_config_file(self, runner):
        """Test CLI with non-existent configuration file."""
        result = runner.invoke(cli, [
            '--config', '/nonexistent/config.yaml',
            'info',
            '--list-all'
        ])
        
        assert result.exit_code == 2  # Click error for invalid file
    
    def test_quiet_mode(self, runner, temp_config):
        """Test quiet mode suppresses output."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            '--quiet',
            'info',
            '--list-all'
        ])
        
        # Should still work but with less output
        assert result.exit_code == 0
    
    def test_verbose_mode(self, runner, temp_config):
        """Test verbose mode increases output."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            '--verbose',
            'info',
            '--list-all'
        ])
        
        assert result.exit_code == 0
    
    def test_very_verbose_mode(self, runner, temp_config):
        """Test very verbose mode (debug level)."""
        result = runner.invoke(cli, [
            '--config', temp_config,
            '-vv',  # Very verbose
            'info',
            '--list-all'
        ])
        
        assert result.exit_code == 0