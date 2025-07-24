# PostCodeMon

A modern Python wrapper for Windows CLI tools with enhanced automation, monitoring, and error handling capabilities.

## Overview

PostCodeMon transforms legacy Windows executables into modern, Python-integrated tools with comprehensive features including:

- **Advanced CLI Interface**: Smart argument mapping, validation, and interactive prompts
- **Configuration Management**: Hierarchical YAML-based configuration with environment overrides
- **Process Management**: Resource monitoring, timeout handling, and parallel execution
- **Comprehensive Logging**: Structured JSON logging with performance metrics and audit trails
- **Error Handling**: Intelligent error translation and retry mechanisms
- **Batch Operations**: Concurrent processing of multiple command sets

## Quick Start

### Installation

```bash
# Install from PyPI (when available)
pip install postcodemon

# Or install from source
git clone https://github.com/example/postcodemon.git
cd postcodemon
pip install -e .
```

### Basic Configuration

Create a `postcodemon.yaml` configuration file:

```yaml
tools:
  my_tool:
    executable_path: "C:/Path/To/Tool.exe"
    default_args: ["--verbose"]
    timeout_seconds: 300
    retry_attempts: 3

logging:
  level: "INFO"
  file_path: "postcodemon.log"
```

### Command Line Usage

```bash
# Execute a tool with arguments
postcodemon execute my_tool --input data.txt --output results.json

# Run multiple commands from a batch file
postcodemon batch commands.txt --tool my_tool --max-concurrent 5

# Show tool information
postcodemon info --tool my_tool

# Monitor running processes
postcodemon monitor --list-processes
```

### Python Library Usage

```python
from PostCodeMon import ToolWrapper

# Execute a tool
with ToolWrapper() as wrapper:
    result = wrapper.execute_tool(
        tool_name="my_tool",
        args=["--input", "data.txt"],
        timeout=300
    )
    
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
```

## Features

### Advanced Command-Line Interface

- **Smart Argument Mapping**: Automatically translate common patterns
- **Command Validation**: Pre-validate arguments before execution
- **Interactive Mode**: Prompt for missing required arguments
- **Dry-Run Mode**: Preview commands without execution
- **Multiple Output Formats**: Text, JSON, and YAML output options

### Configuration Management

- **Hierarchical Configuration**: System, user, and project-level configs
- **Environment Variable Overrides**: Runtime configuration changes
- **Profile Management**: Named profiles for different environments
- **Validation Rules**: Custom argument and file validation
- **Hot Reload**: Dynamic configuration updates

### Process Management

- **Resource Monitoring**: Track CPU, memory, and disk usage
- **Streaming Output**: Real-time output display with progress tracking
- **Timeout Management**: Configurable timeouts with graceful termination
- **Parallel Execution**: Concurrent tool instances with job control
- **Signal Handling**: Proper cleanup on interrupt signals

### Logging and Monitoring

- **Structured Logging**: JSON-formatted logs for analysis
- **Performance Metrics**: Execution time and resource usage tracking
- **Audit Trail**: Complete history of tool invocations
- **Remote Logging**: Integration with centralized logging systems
- **Monitoring Endpoints**: Prometheus metrics support

### Error Handling

- **Intelligent Error Translation**: Convert cryptic errors to actionable messages
- **Retry Logic**: Configurable retry strategies for transient failures
- **Error Categorization**: Classify errors by type and severity
- **Recovery Suggestions**: Specific recommendations for error resolution

## Configuration Reference

### Tool Configuration

```yaml
tools:
  tool_name:
    executable_path: "C:/path/to/tool.exe"  # Required
    default_args: ["--verbose", "--json"]   # Optional default arguments
    timeout_seconds: 300                    # Execution timeout
    retry_attempts: 3                       # Number of retry attempts
    environment_vars:                       # Environment variables
      TOOL_HOME: "C:/tool"
      LOG_LEVEL: "INFO"
    validation_rules:                       # Argument validation
      required_args:
        args: ["--input"]
      file_exists:
        indices: [1]  # Validate file at index 1 exists
```

### Logging Configuration

```yaml
logging:
  level: "INFO"                            # Log level
  format: "%(asctime)s - %(message)s"     # Log format
  file_path: "logs/postcodemon.log"       # Log file path
  max_file_size: 10485760                 # Max log file size (10MB)
  backup_count: 5                         # Number of backup files
  json_format: false                      # Use JSON formatting
  remote_endpoint: null                   # Remote logging endpoint
```

### Global Settings

```yaml
global_timeout: 600                       # Default timeout (seconds)
max_concurrent_jobs: 10                   # Max parallel executions
temp_directory: null                      # Temporary directory
monitoring_enabled: false                # Enable resource monitoring
metrics_endpoint: null                    # Prometheus endpoint
```

## Command Reference

### Execute Command

Execute a Windows tool with specified arguments:

```bash
postcodemon execute [OPTIONS] [ARGS]...

Options:
  -t, --tool TEXT           Tool name to execute
  -d, --cwd PATH           Working directory
  -e, --env TEXT           Environment variables (KEY=VALUE)
  --timeout INTEGER        Execution timeout in seconds
  --dry-run               Preview command without executing
  --output-format TEXT    Output format (text/json/yaml)
  --save-output PATH      Save output to file
```

### Batch Command

Execute multiple commands from a batch file:

```bash
postcodemon batch [OPTIONS] BATCH_FILE

Options:
  -t, --tool TEXT           Tool name to execute
  -j, --max-concurrent INT  Maximum concurrent executions
  --fail-fast              Stop on first failure
  --output-format TEXT     Output format (text/json/yaml)
  --save-results PATH      Save results to file
```

### Info Command

Show information about configured tools:

```bash
postcodemon info [OPTIONS]

Options:
  -t, --tool TEXT          Show info for specific tool
  -a, --list-all          List all configured tools
  --output-format TEXT    Output format (text/json/yaml)
```

### Config Command

Manage PostCodeMon configuration:

```bash
postcodemon config [OPTIONS]

Options:
  --show                  Show current configuration
  --validate             Validate configuration file
  --create-example PATH  Create example configuration
```

### Monitor Command

Monitor and manage running processes:

```bash
postcodemon monitor [OPTIONS]

Options:
  --list-processes       List currently running processes
  --kill-tool TEXT       Kill all processes for specified tool
  --kill-pid INTEGER     Kill process with specific PID
```

## Examples

### Batch File Format

Create a `batch_commands.txt` file:

```
# Simple space-separated arguments
--input file1.txt --output result1.txt
--input file2.txt --output result2.txt --verbose

# Arguments with spaces (use quotes)
--input "C:/My Documents/input.txt" --output "C:/Results/output.txt"

# JSON array format for complex arguments
["--config", "config.json", "--mode", "batch", "--threads", "4"]
```

### Python Library Examples

```python
from PostCodeMon import ToolWrapper
from PostCodeMon.core.errors import ToolExecutionError

# Basic execution with error handling
try:
    with ToolWrapper() as wrapper:
        result = wrapper.execute_tool(
            tool_name="my_tool",
            args=["--input", "data.txt"],
            timeout=300
        )
        
        if result.success:
            print("Tool executed successfully!")
            print(f"Output: {result.stdout}")
        else:
            print(f"Tool failed with code: {result.return_code}")
            print(f"Error: {result.stderr}")
            
except ToolExecutionError as e:
    print(f"Execution error: {e.message}")
    print(f"Return code: {e.return_code}")

# Batch execution with progress tracking
def progress_callback(completed, total, current_command):
    print(f"Progress: {completed}/{total} - {current_command}")

batch_args = [
    ["--input", "file1.txt"],
    ["--input", "file2.txt"],
    ["--input", "file3.txt"]
]

with ToolWrapper() as wrapper:
    results = wrapper.execute_batch(
        tool_name="batch_processor",
        batch_args=batch_args,
        max_concurrent=3,
        progress_callback=progress_callback
    )
    
    successful = sum(1 for r in results if r.success)
    print(f"Completed: {successful}/{len(results)} successful")
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/example/postcodemon.git
cd postcodemon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=PostCodeMon --cov-report=html

# Run specific test file
pytest tests/test_config.py
```

### Code Quality

```bash
# Format code
black PostCodeMon/

# Lint code
flake8 PostCodeMon/

# Type checking
mypy PostCodeMon/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass and code meets quality standards
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://postcodemon.readthedocs.io/](https://postcodemon.readthedocs.io/)
- Issues: [https://github.com/example/postcodemon/issues](https://github.com/example/postcodemon/issues)
- Discussions: [https://github.com/example/postcodemon/discussions](https://github.com/example/postcodemon/discussions)

## Changelog

### Version 0.1.0 (Initial Release)

- Core wrapper functionality
- Advanced CLI interface with multiple output formats
- Hierarchical configuration management
- Comprehensive logging and monitoring
- Process management with resource tracking
- Batch execution capabilities
- Extensive error handling and recovery
- Complete test suite and documentation