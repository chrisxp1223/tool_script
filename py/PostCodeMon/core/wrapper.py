"""Main wrapper class that orchestrates all PostCodeMon functionality."""

import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
import atexit

from .config import ConfigManager, ToolConfig, WrapperConfig
from .logger import LogManager
from .process import ProcessManager, ProcessResult
from .errors import (
    PostCodeMonError, ToolExecutionError, ConfigurationError,
    ToolNotFoundError, ValidationError
)


class ToolWrapper:
    """Main wrapper class for Windows CLI tools."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None,
                 tool_name: Optional[str] = None):
        """
        Initialize the tool wrapper.
        
        Args:
            config_path: Path to configuration file
            tool_name: Name of the specific tool to wrap (if wrapping a single tool)
        """
        self.config_manager = ConfigManager(config_path)
        self.config: WrapperConfig = self.config_manager.load_config()
        self.log_manager = LogManager(self.config.logging)
        self.process_manager = ProcessManager(
            self.log_manager, 
            self.config.max_concurrent_jobs
        )
        
        self.tool_name = tool_name
        self.logger = self.log_manager.get_logger("postcodemon.wrapper")
        
        # Register cleanup handlers
        atexit.register(self.shutdown)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("PostCodeMon wrapper initialized", extra={
            'tool_name': tool_name,
            'config_tools': list(self.config.tools.keys()),
            'max_concurrent': self.config.max_concurrent_jobs
        })
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle system signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully")
        
        # Kill all active processes first
        active_processes = self.process_manager.get_active_processes()
        if active_processes:
            self.logger.info(f"Terminating {len(active_processes)} active processes")
            for process_id, process_info in active_processes.items():
                tool_name = process_info.get('tool_name', 'unknown')
                pid = process_info.get('pid')
                if pid:
                    self.process_manager.kill_process(tool_name, pid)
        
        # Then shutdown normally
        self.shutdown()
        
        # Exit with appropriate code
        if signum == signal.SIGINT:
            sys.exit(130)  # Standard exit code for Ctrl+C
        else:
            sys.exit(0)
    
    def validate_tool_config(self, tool_name: str) -> ToolConfig:
        """Validate that a tool is properly configured."""
        tool_config = self.config_manager.get_tool_config(tool_name)
        if not tool_config:
            raise ConfigurationError(
                f"Tool '{tool_name}' is not configured. "
                f"Available tools: {list(self.config.tools.keys())}"
            )
        
        if not tool_config.executable_path:
            raise ConfigurationError(
                f"Tool '{tool_name}' has no executable_path configured"
            )
        
        return tool_config
    
    def validate_arguments(self, tool_name: str, args: List[str]) -> List[str]:
        """Validate and transform arguments according to tool configuration."""
        tool_config = self.validate_tool_config(tool_name)
        
        # Apply validation rules if configured
        validation_rules = tool_config.validation_rules
        if validation_rules:
            for rule_name, rule_config in validation_rules.items():
                if rule_name == "required_args":
                    required_args = rule_config.get("args", [])
                    for required_arg in required_args:
                        if required_arg not in args:
                            raise ValidationError(
                                f"Required argument '{required_arg}' missing for tool '{tool_name}'",
                                field="args",
                                value=str(args)
                            )
                
                elif rule_name == "file_exists":
                    file_arg_indices = rule_config.get("indices", [])
                    for idx in file_arg_indices:
                        if idx < len(args) and not os.path.exists(args[idx]):
                            raise ValidationError(
                                f"File does not exist: {args[idx]}",
                                field="file_path",
                                value=args[idx]
                            )
        
        # Merge with default arguments
        final_args = tool_config.default_args.copy()
        final_args.extend(args)
        
        return final_args
    
    def execute_tool(self, tool_name: Optional[str] = None, args: Optional[List[str]] = None,
                    cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None,
                    timeout: Optional[int] = None, dry_run: bool = False,
                    progress_callback: Optional[Callable[[str], None]] = None,
                    **kwargs) -> ProcessResult:
        """
        Execute a Windows tool with full wrapper capabilities.
        
        Args:
            tool_name: Name of the tool to execute (uses default if not provided)
            args: Command line arguments
            cwd: Working directory
            env: Environment variables
            timeout: Execution timeout in seconds
            dry_run: If True, preview command without executing
            progress_callback: Function to call with streaming output
            **kwargs: Additional process manager options
            
        Returns:
            ProcessResult: Execution results
            
        Raises:
            ConfigurationError: If tool is not configured properly
            ValidationError: If arguments fail validation
            ToolExecutionError: If tool execution fails
        """
        # Use default tool name if not provided
        effective_tool_name = tool_name or self.tool_name
        if not effective_tool_name:
            raise ConfigurationError("No tool name provided and no default tool configured")
        
        # Validate configuration
        tool_config = self.validate_tool_config(effective_tool_name)
        
        # Validate and prepare arguments
        final_args = self.validate_arguments(effective_tool_name, args or [])
        
        # Determine timeout
        effective_timeout = timeout or tool_config.timeout_seconds or self.config.global_timeout
        
        # Determine working directory
        effective_cwd = cwd or tool_config.working_directory
        
        # Prepare environment
        final_env = os.environ.copy()
        if tool_config.environment_vars:
            final_env.update(tool_config.environment_vars)
        if env:
            final_env.update(env)
        
        # Prepare command for logging
        command_preview = f"{tool_config.executable_path} {' '.join(final_args)}"
        
        if dry_run:
            self.logger.info(f"DRY RUN - Would execute: {command_preview}", extra={
                'tool_name': effective_tool_name,
                'args': final_args,
                'cwd': cwd,
                'timeout': effective_timeout,
                'dry_run': True
            })
            
            # Return a mock result for dry run
            return ProcessResult(
                return_code=0,
                stdout=f"DRY RUN: {command_preview}",
                stderr="",
                duration=0.0,
                command=command_preview,
                tool_name=effective_tool_name
            )
        
        # Execute with retry logic
        last_exception = None
        for attempt in range(tool_config.retry_attempts):
            try:
                self.logger.info(f"Executing tool (attempt {attempt + 1}/{tool_config.retry_attempts}): {effective_tool_name}", extra={
                    'tool_name': effective_tool_name,
                    'command': command_preview,
                    'attempt': attempt + 1,
                    'max_attempts': tool_config.retry_attempts
                })
                
                # Print retry information to console
                if attempt > 0:
                    print(f"\n[RETRY {attempt + 1}/{tool_config.retry_attempts}] Retrying tool: {effective_tool_name}")
                    print(f"Command: {command_preview}")
                    print("-" * 50)
                
                result = self.process_manager.execute_tool(
                    tool_name=effective_tool_name,
                    executable_path=tool_config.executable_path,
                    args=final_args,
                    timeout=effective_timeout,
                    cwd=effective_cwd,
                    env=final_env,
                    progress_callback=progress_callback,
                    **kwargs
                )
                
                # Check if tool execution was successful
                if not result.success:
                    # Tool failed, raise exception to trigger retry
                    result.raise_for_status()
                
                # Log success
                self.log_manager.log_audit_event(
                    "tool_execution_success",
                    details={
                        "tool_name": effective_tool_name,
                        "duration": result.duration,
                        "return_code": result.return_code,
                        "attempt": attempt + 1
                    }
                )
                
                # Print success message if retried
                if attempt > 0:
                    print(f"\n[SUCCESS] Tool executed successfully after {attempt + 1} retries!")
                
                return result
                
            except (ToolExecutionError, ToolNotFoundError) as e:
                last_exception = e
                
                if attempt < tool_config.retry_attempts - 1:
                    # Wait before retry (fixed wait time)
                    wait_time = tool_config.retry_wait_seconds
                    self.logger.warning(f"Tool execution failed, retrying in {wait_time}s: {e}", extra={
                        'tool_name': effective_tool_name,
                        'attempt': attempt + 1,
                        'wait_time': wait_time,
                        'error': str(e)
                    })
                    
                    # Print retry information to console
                    print(f"\n[ERROR] Attempt {attempt + 1} failed")
                    print(f"Error: {e}")
                    print(f"[WAIT] Waiting {wait_time} seconds...")
                    
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Tool execution failed after {tool_config.retry_attempts} attempts: {e}", extra={
                        'tool_name': effective_tool_name,
                        'total_attempts': tool_config.retry_attempts,
                        'final_error': str(e)
                    })
                    
                    # Print final failure message
                    print(f"\n[FAILED] Tool failed after {tool_config.retry_attempts} attempts")
                    print(f"Final error: {e}")
                    
                    raise
        
        # If we get here, all retries failed
        raise last_exception or ToolExecutionError(
            f"Tool '{effective_tool_name}' failed after {tool_config.retry_attempts} attempts",
            -1,
            "Unknown error"
        )
    
    def execute_batch(self, tool_name: str, batch_args: List[List[str]],
                     max_concurrent: Optional[int] = None,
                     fail_fast: bool = False,
                     progress_callback: Optional[Callable[[int, int, str], None]] = None,
                     **kwargs) -> List[ProcessResult]:
        """
        Execute a tool multiple times with different argument sets.
        
        Args:
            tool_name: Name of the tool to execute
            batch_args: List of argument lists to execute
            max_concurrent: Maximum concurrent executions (uses config default if None)
            fail_fast: If True, stop on first failure
            progress_callback: Function called with (completed, total, current_command)
            **kwargs: Additional arguments passed to execute_tool
            
        Returns:
            List[ProcessResult]: Results for each execution
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        effective_concurrent = max_concurrent or self.config.max_concurrent_jobs
        results = [None] * len(batch_args)
        
        self.logger.info(f"Starting batch execution of {len(batch_args)} commands", extra={
            'tool_name': tool_name,
            'batch_size': len(batch_args),
            'max_concurrent': effective_concurrent
        })
        
        def execute_single(index_args_pair):
            index, args = index_args_pair
            try:
                result = self.execute_tool(tool_name, args, **kwargs)
                if progress_callback:
                    progress_callback(index + 1, len(batch_args), result.command)
                return index, result
            except Exception as e:
                error_result = ProcessResult(
                    return_code=-1,
                    stdout="",
                    stderr=str(e),
                    duration=0.0,
                    command=f"{tool_name} {' '.join(args)}",
                    tool_name=tool_name
                )
                return index, error_result
        
        with ThreadPoolExecutor(max_workers=effective_concurrent) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(execute_single, (i, args)): i 
                for i, args in enumerate(batch_args)
            }
            
            completed = 0
            for future in as_completed(future_to_index):
                try:
                    index, result = future.result()
                    results[index] = result
                    completed += 1
                    
                    if fail_fast and not result.success:
                        # Cancel remaining futures
                        for remaining_future in future_to_index:
                            if not remaining_future.done():
                                remaining_future.cancel()
                        
                        self.logger.error(f"Batch execution failed fast at item {index + 1}", extra={
                            'tool_name': tool_name,
                            'failed_index': index,
                            'completed': completed,
                            'total': len(batch_args)
                        })
                        break
                        
                except Exception as e:
                    self.logger.error(f"Unexpected error in batch execution: {e}")
        
        # Filter out None results (from cancelled futures)
        final_results = [r for r in results if r is not None]
        
        success_count = sum(1 for r in final_results if r.success)
        self.logger.info(f"Batch execution completed: {success_count}/{len(final_results)} successful", extra={
            'tool_name': tool_name,
            'successful': success_count,
            'total': len(final_results),
            'success_rate': success_count / len(final_results) if final_results else 0
        })
        
        return final_results
    
    def get_tool_info(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a configured tool."""
        effective_tool_name = tool_name or self.tool_name
        if not effective_tool_name:
            raise ConfigurationError("No tool name provided")
        
        tool_config = self.validate_tool_config(effective_tool_name)
        
        # Try to get version info by running the tool
        version_info = None
        try:
            # Common version flags
            for version_flag in ["--version", "-v", "/version", "/?", "--help"]:
                try:
                    result = self.execute_tool(
                        effective_tool_name, 
                        [version_flag], 
                        timeout=10
                    )
                    if result.success and (result.stdout or result.stderr):
                        version_info = (result.stdout or result.stderr).strip()[:200]
                        break
                except:
                    continue
        except:
            pass
        
        return {
            'name': effective_tool_name,
            'executable_path': tool_config.executable_path,
            'executable_exists': os.path.isfile(tool_config.executable_path),
            'default_args': tool_config.default_args,
            'timeout_seconds': tool_config.timeout_seconds,
            'retry_attempts': tool_config.retry_attempts,
            'environment_vars': tool_config.environment_vars,
            'validation_rules': tool_config.validation_rules,
            'version_info': version_info
        }
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all configured tools with their information."""
        tools_info = {}
        for tool_name in self.config.tools.keys():
            try:
                tools_info[tool_name] = self.get_tool_info(tool_name)
            except Exception as e:
                tools_info[tool_name] = {
                    'name': tool_name,
                    'error': str(e)
                }
        
        return tools_info
    
    def get_active_processes(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently running processes."""
        return self.process_manager.get_active_processes()
    
    def kill_process(self, tool_name: str, process_id: Optional[int] = None) -> bool:
        """Kill a running process."""
        return self.process_manager.kill_process(tool_name, process_id)
    
    def reload_config(self) -> None:
        """Reload configuration from files."""
        self.config_manager._config = None  # Clear cached config
        self.config = self.config_manager.load_config()
        self.log_manager.update_config(self.config.logging)
        
        self.logger.info("Configuration reloaded", extra={
            'tools_count': len(self.config.tools),
            'log_level': self.config.logging.level
        })
    
    def shutdown(self) -> None:
        """Shutdown the wrapper and clean up resources."""
        self.logger.info("Shutting down PostCodeMon wrapper")
        
        try:
            # Shutdown process manager
            self.process_manager.shutdown()
            
            # Shutdown logging
            self.log_manager.shutdown()
            
        except Exception as e:
            print(f"Error during shutdown: {e}", file=sys.stderr)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()