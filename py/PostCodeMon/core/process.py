"""Process management for executing Windows tools."""

import asyncio
import os
import signal
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import psutil

from .errors import ToolExecutionError, TimeoutError, ToolNotFoundError
from .logger import LogManager


class ProcessResult:
    """Container for process execution results."""
    
    def __init__(self, return_code: int, stdout: str, stderr: str, 
                 duration: float, command: str, tool_name: str):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration = duration
        self.command = command
        self.tool_name = tool_name
        self.success = return_code == 0
    
    def __str__(self) -> str:
        status = "SUCCESS" if self.success else f"FAILED (code: {self.return_code})"
        return f"ProcessResult({self.tool_name}: {status}, duration: {self.duration:.2f}s)"
    
    def raise_for_status(self) -> None:
        """Raise an exception if the process failed."""
        if not self.success:
            raise ToolExecutionError(
                f"Tool '{self.tool_name}' failed with return code {self.return_code}",
                self.return_code,
                self.stderr
            )


class ProcessMonitor:
    """Monitor process resource usage during execution."""
    
    def __init__(self, process: psutil.Process, log_manager: LogManager, 
                 tool_name: str, sample_interval: float = 1.0):
        self.process = process
        self.log_manager = log_manager
        self.tool_name = tool_name
        self.sample_interval = sample_interval
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics: List[Dict[str, Any]] = []
    
    def start_monitoring(self) -> None:
        """Start monitoring process resources."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return summary metrics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        if not self.metrics:
            return {}
        
        # Calculate summary statistics
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_mb'] for m in self.metrics]
        
        summary = {
            'samples': len(self.metrics),
            'duration_seconds': len(self.metrics) * self.sample_interval,
            'cpu_percent': {
                'min': min(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0
            },
            'memory_mb': {
                'min': min(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0,
                'avg': sum(memory_values) / len(memory_values) if memory_values else 0
            }
        }
        
        self.log_manager.log_performance_metric(
            f"{self.tool_name}_resource_usage",
            summary['cpu_percent']['avg'],
            unit="cpu_percent",
            memory_mb_avg=summary['memory_mb']['avg'],
            memory_mb_max=summary['memory_mb']['max']
        )
        
        return summary
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                if self.process.is_running():
                    cpu_percent = self.process.cpu_percent()
                    memory_info = self.process.memory_info()
                    
                    metric = {
                        'timestamp': time.time(),
                        'cpu_percent': cpu_percent,
                        'memory_mb': memory_info.rss / 1024 / 1024,
                        'num_threads': self.process.num_threads()
                    }
                    
                    self.metrics.append(metric)
                else:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            
            time.sleep(self.sample_interval)


class ProcessManager:
    """Manages execution of Windows tools with advanced features."""
    
    def __init__(self, log_manager: LogManager, max_concurrent: int = 10):
        self.log_manager = log_manager
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.process_lock = threading.Lock()
    
    def find_tool_executable(self, tool_path: str, search_paths: Optional[List[str]] = None) -> str:
        """Find the executable for a tool, searching common locations."""
        # If absolute path is provided and exists, use it
        if os.path.isabs(tool_path) and os.path.isfile(tool_path):
            return tool_path
        
        search_locations = search_paths or []
        
        # Add common Windows executable locations
        search_locations.extend([
            os.getcwd(),
            str(Path.home() / "bin"),
            "C:/Windows/System32",
            "C:/Program Files",
            "C:/Program Files (x86)"
        ])
        
        # Add PATH directories
        search_locations.extend(os.environ.get("PATH", "").split(os.pathsep))
        
        # Try each location
        for search_path in search_locations:
            if not search_path:
                continue
            
            candidate_path = Path(search_path) / tool_path
            
            # Try with and without .exe extension
            for path_to_try in [candidate_path, Path(str(candidate_path) + ".exe")]:
                if path_to_try.is_file():
                    return str(path_to_try.resolve())
        
        raise ToolNotFoundError(tool_path, search_locations)
    
    def execute_tool(self, tool_name: str, executable_path: str, args: List[str],
                    timeout: Optional[int] = None, cwd: Optional[str] = None,
                    env: Optional[Dict[str, str]] = None,
                    monitor_resources: bool = True,
                    progress_callback: Optional[Callable[[str], None]] = None) -> ProcessResult:
        """Execute a Windows tool with comprehensive monitoring and error handling."""
        
        # Validate executable exists
        if not os.path.isfile(executable_path):
            executable_path = self.find_tool_executable(executable_path)
        
        # Prepare command
        command_list = [executable_path] + args
        command_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in command_list)
        
        self.log_manager.log_audit_event(
            "tool_execution_start",
            details={
                "tool_name": tool_name,
                "command": command_str,
                "cwd": cwd,
                "timeout": timeout
            }
        )
        
        # Prepare environment
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        
        start_time = time.time()
        process = None
        monitor = None
        
        try:
            with self.log_manager.create_performance_logger(
                f"execute_{tool_name}",
                command=command_str
            ):
                # Start the process
                process = subprocess.Popen(
                    command_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    env=process_env,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Track active process
                process_id = f"{tool_name}_{process.pid}"
                with self.process_lock:
                    self.active_processes[process_id] = process
                
                try:
                    # Start resource monitoring
                    if monitor_resources:
                        try:
                            psutil_process = psutil.Process(process.pid)
                            monitor = ProcessMonitor(
                                psutil_process, self.log_manager, tool_name
                            )
                            monitor.start_monitoring()
                        except psutil.NoSuchProcess:
                            pass  # Process may have finished already
                    
                    # Handle streaming output
                    stdout_lines = []
                    stderr_lines = []
                    
                    def read_output(pipe, container, callback):
                        try:
                            for line in iter(pipe.readline, ''):
                                if line:
                                    container.append(line)
                                    if callback:
                                        callback(line.rstrip())
                        except Exception:
                            pass  # Handle broken pipe gracefully
                    
                    # Start output reading threads
                    stdout_thread = threading.Thread(
                        target=read_output,
                        args=(process.stdout, stdout_lines, progress_callback),
                        daemon=True
                    )
                    stderr_thread = threading.Thread(
                        target=read_output,
                        args=(process.stderr, stderr_lines, None),
                        daemon=True
                    )
                    
                    stdout_thread.start()
                    stderr_thread.start()
                    
                    # Wait for process completion with timeout
                    try:
                        return_code = process.wait(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        # Terminate process gracefully, then force kill if needed
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                        raise TimeoutError(timeout or 0)
                    
                    # Wait for output threads to complete
                    stdout_thread.join(timeout=1)
                    stderr_thread.join(timeout=1)
                    
                    duration = time.time() - start_time
                    stdout_str = "".join(stdout_lines)
                    stderr_str = "".join(stderr_lines)
                    
                    # Stop monitoring and get metrics
                    resource_metrics = {}
                    if monitor:
                        resource_metrics = monitor.stop_monitoring()
                    
                    # Create result
                    result = ProcessResult(
                        return_code=return_code,
                        stdout=stdout_str,
                        stderr=stderr_str,
                        duration=duration,
                        command=command_str,
                        tool_name=tool_name
                    )
                    
                    # Log execution details
                    self.log_manager.log_tool_execution(
                        tool_name=tool_name,
                        command=command_str,
                        return_code=return_code,
                        stdout=stdout_str,
                        stderr=stderr_str,
                        duration=duration,
                        resource_metrics=resource_metrics
                    )
                    
                    return result
                
                finally:
                    # Clean up active process tracking
                    with self.process_lock:
                        self.active_processes.pop(process_id, None)
        
        except Exception as e:
            duration = time.time() - start_time
            
            # Stop monitoring on error
            if monitor:
                monitor.stop_monitoring()
            
            self.log_manager.log_audit_event(
                "tool_execution_error",
                details={
                    "tool_name": tool_name,
                    "command": command_str,
                    "error": str(e),
                    "duration": duration
                }
            )
            
            if isinstance(e, (TimeoutError, ToolNotFoundError)):
                raise
            else:
                raise ToolExecutionError(
                    f"Failed to execute tool '{tool_name}': {e}",
                    -1,
                    str(e)
                )
    
    def execute_tool_async(self, tool_name: str, executable_path: str, args: List[str],
                          **kwargs) -> Future[ProcessResult]:
        """Execute a tool asynchronously."""
        return self.executor.submit(
            self.execute_tool, tool_name, executable_path, args, **kwargs
        )
    
    def kill_process(self, tool_name: str, process_id: Optional[int] = None) -> bool:
        """Kill a running process by tool name or PID."""
        with self.process_lock:
            processes_to_kill = []
            
            if process_id:
                # Kill specific process ID
                for key, process in self.active_processes.items():
                    if process.pid == process_id:
                        processes_to_kill.append((key, process))
            else:
                # Kill all processes for tool name
                for key, process in self.active_processes.items():
                    if key.startswith(f"{tool_name}_"):
                        processes_to_kill.append((key, process))
            
            killed_any = False
            for key, process in processes_to_kill:
                try:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    
                    self.active_processes.pop(key, None)
                    killed_any = True
                    
                    self.log_manager.log_audit_event(
                        "process_killed",
                        details={"tool_name": tool_name, "pid": process.pid}
                    )
                except Exception as e:
                    self.log_manager.get_logger("postcodemon.process").warning(
                        f"Failed to kill process {process.pid}: {e}"
                    )
            
            return killed_any
    
    def get_active_processes(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active processes."""
        with self.process_lock:
            active = {}
            for key, process in self.active_processes.items():
                try:
                    psutil_process = psutil.Process(process.pid)
                    active[key] = {
                        'pid': process.pid,
                        'tool_name': key.split('_')[0],
                        'status': psutil_process.status(),
                        'cpu_percent': psutil_process.cpu_percent(),
                        'memory_mb': psutil_process.memory_info().rss / 1024 / 1024,
                        'create_time': psutil_process.create_time()
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process no longer exists, clean it up
                    pass
            
            # Clean up stale processes
            stale_keys = [k for k in self.active_processes.keys() if k not in active]
            for key in stale_keys:
                self.active_processes.pop(key, None)
            
            return active
    
    def shutdown(self) -> None:
        """Shutdown the process manager and clean up resources."""
        # Kill all active processes
        with self.process_lock:
            for key, process in list(self.active_processes.items()):
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except (subprocess.TimeoutExpired, ProcessLookupError):
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True, timeout=10)