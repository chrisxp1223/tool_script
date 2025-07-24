#!/usr/bin/env python3
"""
Basic usage examples for PostCodeMon.

This script demonstrates how to use PostCodeMon as a Python library
rather than through the CLI interface.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import PostCodeMon
sys.path.insert(0, str(Path(__file__).parent.parent))

from PostCodeMon import ToolWrapper, ConfigManager, LogManager
from PostCodeMon.core.errors import PostCodeMonError


def example_basic_execution():
    """Example of basic tool execution."""
    print("=== Basic Tool Execution ===")
    
    try:
        # Create a wrapper with default configuration
        with ToolWrapper() as wrapper:
            # Execute a simple Windows command (assuming 'echo' or similar tool is configured)
            result = wrapper.execute_tool(
                tool_name="example_tool",  # This would need to be configured
                args=["Hello", "World"],
                timeout=30
            )
            
            print(f"Command: {result.command}")
            print(f"Return Code: {result.return_code}")
            print(f"Duration: {result.duration:.2f}s")
            print(f"Success: {result.success}")
            
            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
                
    except PostCodeMonError as e:
        print(f"PostCodeMon Error: {e.message}")
        if hasattr(e, 'error_code'):
            print(f"Error Code: {e.error_code}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


def example_batch_execution():
    """Example of batch tool execution."""
    print("\n=== Batch Tool Execution ===")
    
    try:
        with ToolWrapper() as wrapper:
            # Define multiple sets of arguments
            batch_args = [
                ["--input", "file1.txt", "--output", "result1.txt"],
                ["--input", "file2.txt", "--output", "result2.txt"],
                ["--input", "file3.txt", "--output", "result3.txt"],
            ]
            
            def progress_callback(completed, total, current_command):
                print(f"Progress: {completed}/{total} - {current_command}")
            
            # Execute all commands
            results = wrapper.execute_batch(
                tool_name="batch_tool",
                batch_args=batch_args,
                max_concurrent=2,
                progress_callback=progress_callback
            )
            
            # Analyze results
            successful = sum(1 for r in results if r.success)
            total_time = sum(r.duration for r in results)
            
            print(f"\nBatch Results:")
            print(f"Successful: {successful}/{len(results)}")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Average Time: {total_time/len(results):.2f}s")
            
            # Show details for failed executions
            for i, result in enumerate(results):
                if not result.success:
                    print(f"\nFailed execution {i+1}:")
                    print(f"  Command: {result.command}")
                    print(f"  Error: {result.stderr}")
                    
    except PostCodeMonError as e:
        print(f"PostCodeMon Error: {e.message}")


def example_configuration():
    """Example of working with configuration."""
    print("\n=== Configuration Management ===")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print(f"Available tools: {list(config.tools.keys())}")
        print(f"Global timeout: {config.global_timeout}s")
        print(f"Max concurrent jobs: {config.max_concurrent_jobs}")
        print(f"Log level: {config.logging.level}")
        
        # Get specific tool configuration
        for tool_name in config.tools.keys():
            tool_config = config_manager.get_tool_config(tool_name)
            if tool_config:
                print(f"\nTool '{tool_name}':")
                print(f"  Executable: {tool_config.executable_path}")
                print(f"  Default args: {tool_config.default_args}")
                print(f"  Timeout: {tool_config.timeout_seconds}s")
                print(f"  Retry attempts: {tool_config.retry_attempts}")
                
    except PostCodeMonError as e:
        print(f"Configuration Error: {e.message}")


def example_custom_logging():
    """Example of custom logging setup."""
    print("\n=== Custom Logging ===")
    
    from PostCodeMon.core.config import LoggingConfig
    
    # Create custom logging configuration
    custom_log_config = LoggingConfig(
        level="DEBUG",
        json_format=True,
        file_path="custom_postcodemon.log"
    )
    
    # Create log manager with custom config
    log_manager = LogManager(custom_log_config)
    
    # Get a logger and use it
    logger = log_manager.get_logger("example")
    logger.info("This is a custom log message")
    
    # Log performance metrics
    log_manager.log_performance_metric(
        "execution_time", 
        1.234, 
        unit="seconds",
        tool_name="example_tool"
    )
    
    # Log audit events
    log_manager.log_audit_event(
        "tool_execution",
        user="example_user",
        details={"tool": "example_tool", "action": "execute"}
    )
    
    print("Custom logging examples completed. Check 'custom_postcodemon.log' file.")


def example_error_handling():
    """Example of comprehensive error handling."""
    print("\n=== Error Handling ===")
    
    try:
        with ToolWrapper() as wrapper:
            # Try to execute a non-existent tool
            result = wrapper.execute_tool(
                tool_name="nonexistent_tool",
                args=["test"]
            )
            
    except PostCodeMonError as e:
        print(f"Caught PostCodeMon error: {e.message}")
        print(f"Error type: {type(e).__name__}")
        
        # Handle specific error types
        from PostCodeMon.core.errors import (
            ToolNotFoundError, 
            ConfigurationError, 
            ValidationError,
            ToolExecutionError
        )
        
        if isinstance(e, ToolNotFoundError):
            print(f"Tool path: {e.tool_path}")
            print(f"Search paths: {e.search_paths}")
        elif isinstance(e, ConfigurationError):
            print(f"Config path: {getattr(e, 'config_path', 'Unknown')}")
        elif isinstance(e, ValidationError):
            print(f"Field: {getattr(e, 'field', 'Unknown')}")
            print(f"Value: {getattr(e, 'value', 'Unknown')}")
        elif isinstance(e, ToolExecutionError):
            print(f"Return code: {e.return_code}")
            print(f"Stderr: {e.stderr}")


def example_process_monitoring():
    """Example of process monitoring capabilities."""
    print("\n=== Process Monitoring ===")
    
    try:
        with ToolWrapper() as wrapper:
            # Get active processes
            active_processes = wrapper.get_active_processes()
            
            if active_processes:
                print("Active processes:")
                for process_id, info in active_processes.items():
                    print(f"  {process_id}: PID {info['pid']}, Tool: {info['tool_name']}")
            else:
                print("No active processes")
            
            # Example of starting a long-running process and monitoring it
            # (This would require a configured long-running tool)
            print("\nProcess monitoring features available:")
            print("- Real-time resource usage tracking")
            print("- Process killing by tool name or PID")
            print("- CPU and memory usage monitoring")
            print("- Process lifecycle management")
            
    except PostCodeMonError as e:
        print(f"Monitoring Error: {e.message}")


def main():
    """Run all examples."""
    print("PostCodeMon Python Library Usage Examples")
    print("=" * 50)
    
    # Note: Most examples will fail without proper configuration
    # This is intentional to demonstrate error handling
    
    example_configuration()
    example_custom_logging()
    example_error_handling()
    example_process_monitoring()
    
    # These would require actual tool configuration to work
    print("\nNote: Tool execution examples require proper configuration.")
    print("Create a 'postcodemon.yaml' file with your tool definitions to run:")
    print("- example_basic_execution()")
    print("- example_batch_execution()")
    
    print("\nFor complete examples, see the config/example.yaml file")


if __name__ == "__main__":
    main()