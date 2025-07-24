"""CLI command implementations for PostCodeMon."""

import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.syntax import Syntax
import yaml

# Handle both direct execution and package imports
try:
    from ..core.wrapper import ToolWrapper
    from ..core.errors import PostCodeMonError
    from .utils import create_wrapper, handle_error
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.wrapper import ToolWrapper
    from core.errors import PostCodeMonError
    from cli.utils import create_wrapper, handle_error

console = Console()


@click.command('execute')
@click.argument('args', nargs=-1)
@click.option(
    '--tool', '-t',
    help='Tool name to execute (overrides default)'
)
@click.option(
    '--cwd', '-d',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help='Working directory for execution'
)
@click.option(
    '--env', '-e',
    multiple=True,
    help='Environment variables in KEY=VALUE format'
)
@click.option(
    '--timeout',
    type=int,
    help='Execution timeout in seconds'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Preview command without executing'
)
@click.option(
    '--output-format', 
    type=click.Choice(['text', 'json', 'yaml']),
    default='text',
    help='Output format for results'
)
@click.option(
    '--save-output',
    type=click.Path(path_type=Path),
    help='Save output to file'
)
@click.pass_context
def execute_command(ctx: click.Context, args: Tuple[str, ...], tool: Optional[str],
                   cwd: Optional[Path], env: Tuple[str, ...], timeout: Optional[int],
                   dry_run: bool, output_format: str, save_output: Optional[Path]):
    """Execute a Windows tool with the specified arguments."""
    try:
        wrapper = create_wrapper(ctx)
        
        # Parse environment variables
        env_dict = {}
        for env_var in env:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                env_dict[key] = value
            else:
                click.echo(f"Warning: Invalid environment variable format: {env_var}", err=True)
        
        # Progress callback for streaming output
        def progress_callback(line: str):
            if not ctx.obj.get('quiet', False) and output_format == 'text':
                console.print(f"[dim]{line}[/dim]")
        
        # Execute the tool
        result = wrapper.execute_tool(
            tool_name=tool,
            args=list(args),
            cwd=str(cwd) if cwd else None,
            env=env_dict if env_dict else None,
            timeout=timeout,
            dry_run=dry_run,
            progress_callback=progress_callback if not dry_run else None
        )
        
        # Format and display results
        output_data = _format_result(result, output_format)
        
        if save_output:
            save_output.parent.mkdir(parents=True, exist_ok=True)
            with open(save_output, 'w', encoding='utf-8') as f:
                f.write(output_data)
            if not ctx.obj.get('quiet', False):
                console.print(f"[green]Output saved to:[/green] {save_output}")
        else:
            if not ctx.obj.get('quiet', False) or not result.success:
                console.print(output_data)
        
        # Exit with tool's return code
        sys.exit(result.return_code)
        
    except Exception as e:
        handle_error(e, ctx.obj.get('quiet', False))


@click.command('batch')
@click.argument('batch_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--tool', '-t',
    help='Tool name to execute (overrides default)'
)
@click.option(
    '--max-concurrent', '-j',
    type=int,
    help='Maximum concurrent executions'
)
@click.option(
    '--fail-fast',
    is_flag=True,
    help='Stop execution on first failure'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json', 'yaml']),
    default='text',
    help='Output format for results'
)
@click.option(
    '--save-results',
    type=click.Path(path_type=Path),
    help='Save batch results to file'
)
@click.pass_context
def batch_command(ctx: click.Context, batch_file: Path, tool: Optional[str],
                 max_concurrent: Optional[int], fail_fast: bool,
                 output_format: str, save_results: Optional[Path]):
    """Execute a tool multiple times with arguments from a batch file."""
    try:
        wrapper = create_wrapper(ctx)
        
        # Load batch arguments from file
        batch_args = _load_batch_file(batch_file)
        
        if not ctx.obj.get('quiet', False):
            console.print(f"[blue]Executing {len(batch_args)} commands from {batch_file}[/blue]")
        
        # Progress tracking
        completed_count = 0
        
        def batch_progress_callback(completed: int, total: int, current_command: str):
            nonlocal completed_count
            completed_count = completed
            if not ctx.obj.get('quiet', False):
                console.print(f"[{completed}/{total}] {current_command[:100]}...")
        
        # Execute batch
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            disable=ctx.obj.get('quiet', False)
        ) as progress:
            
            task = progress.add_task("Processing batch...", total=len(batch_args))
            
            results = wrapper.execute_batch(
                tool_name=tool or ctx.obj.get('default_tool'),
                batch_args=batch_args,
                max_concurrent=max_concurrent,
                fail_fast=fail_fast,
                progress_callback=batch_progress_callback
            )
            
            progress.update(task, completed=len(results))
        
        # Format and display results
        output_data = _format_batch_results(results, output_format)
        
        if save_results:
            save_results.parent.mkdir(parents=True, exist_ok=True)
            with open(save_results, 'w', encoding='utf-8') as f:
                f.write(output_data)
            if not ctx.obj.get('quiet', False):
                console.print(f"[green]Results saved to:[/green] {save_results}")
        else:
            if not ctx.obj.get('quiet', False):
                console.print(output_data)
        
        # Calculate exit code based on results
        failed_count = sum(1 for r in results if not r.success)
        if failed_count > 0:
            console.print(f"[red]{failed_count}/{len(results)} executions failed[/red]", err=True)
            sys.exit(1)
        else:
            if not ctx.obj.get('quiet', False):
                console.print(f"[green]All {len(results)} executions successful[/green]")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('quiet', False))


@click.command('info')
@click.option(
    '--tool', '-t',
    help='Show info for specific tool'
)
@click.option(
    '--list-all', '-a',
    is_flag=True,
    help='List all configured tools'
)
@click.option(
    '--output-format',
    type=click.Choice(['text', 'json', 'yaml']),
    default='text',
    help='Output format'
)
@click.pass_context
def info_command(ctx: click.Context, tool: Optional[str], list_all: bool, output_format: str):
    """Show information about configured tools."""
    try:
        wrapper = create_wrapper(ctx)
        
        if list_all:
            tools_info = wrapper.list_tools()
            output_data = _format_tools_info(tools_info, output_format)
        elif tool:
            tool_info = wrapper.get_tool_info(tool)
            output_data = _format_tool_info(tool_info, output_format)
        else:
            # Show default tool info if available
            default_tool = ctx.obj.get('default_tool')
            if default_tool:
                tool_info = wrapper.get_tool_info(default_tool)
                output_data = _format_tool_info(tool_info, output_format)
            else:
                tools_info = wrapper.list_tools()
                output_data = _format_tools_info(tools_info, output_format)
        
        console.print(output_data)
        
    except Exception as e:
        handle_error(e, ctx.obj.get('quiet', False))


@click.command('config')
@click.option(
    '--show',
    is_flag=True,
    help='Show current configuration'
)
@click.option(
    '--validate',
    is_flag=True,
    help='Validate configuration file'
)
@click.option(
    '--create-example',
    type=click.Path(path_type=Path),
    help='Create example configuration file'
)
@click.pass_context
def config_command(ctx: click.Context, show: bool, validate: bool, create_example: Optional[Path]):
    """Manage PostCodeMon configuration."""
    try:
        if create_example:
            _create_example_config(create_example)
            console.print(f"[green]Example configuration created:[/green] {create_example}")
            return
        
        wrapper = create_wrapper(ctx)
        
        if show:
            config_dict = {
                'tools': {name: {
                    'executable_path': tool.executable_path,
                    'default_args': tool.default_args,
                    'timeout_seconds': tool.timeout_seconds,
                    'retry_attempts': tool.retry_attempts,
                    'environment_vars': tool.environment_vars,
                    'validation_rules': tool.validation_rules
                } for name, tool in wrapper.config.tools.items()},
                'logging': {
                    'level': wrapper.config.logging.level,
                    'format': wrapper.config.logging.format,
                    'file_path': wrapper.config.logging.file_path,
                    'json_format': wrapper.config.logging.json_format
                },
                'global_timeout': wrapper.config.global_timeout,
                'max_concurrent_jobs': wrapper.config.max_concurrent_jobs
            }
            
            syntax = Syntax(
                yaml.dump(config_dict, default_flow_style=False, indent=2),
                "yaml",
                theme="monokai",
                line_numbers=True
            )
            console.print(Panel(syntax, title="Current Configuration"))
        
        if validate:
            # Configuration is validated during wrapper creation
            console.print("[green]✓ Configuration is valid[/green]")
        
        if not show and not validate:
            console.print("Use --show to display configuration or --validate to check it")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('quiet', False))


@click.command('monitor')
@click.option(
    '--list-processes',
    is_flag=True,
    help='List currently running processes'
)
@click.option(
    '--kill-tool',
    help='Kill all processes for specified tool'
)
@click.option(
    '--kill-pid',
    type=int,
    help='Kill process with specific PID'
)
@click.pass_context
def monitor_command(ctx: click.Context, list_processes: bool, kill_tool: Optional[str], kill_pid: Optional[int]):
    """Monitor and manage running tool processes."""
    try:
        wrapper = create_wrapper(ctx)
        
        if list_processes:
            processes = wrapper.get_active_processes()
            if not processes:
                console.print("[yellow]No active processes[/yellow]")
            else:
                _display_active_processes(processes)
        
        if kill_tool:
            killed = wrapper.kill_process(kill_tool)
            if killed:
                console.print(f"[green]Killed processes for tool:[/green] {kill_tool}")
            else:
                console.print(f"[yellow]No processes found for tool:[/yellow] {kill_tool}")
        
        if kill_pid:
            killed = wrapper.kill_process("", kill_pid)
            if killed:
                console.print(f"[green]Killed process:[/green] {kill_pid}")
            else:
                console.print(f"[yellow]Process not found:[/yellow] {kill_pid}")
        
        if not any([list_processes, kill_tool, kill_pid]):
            console.print("Use --list-processes to show running processes")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('quiet', False))


# Helper functions

def _format_result(result, output_format: str) -> str:
    """Format a ProcessResult for display."""
    if output_format == 'json':
        return json.dumps({
            'return_code': result.return_code,
            'success': result.success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': result.duration,
            'command': result.command,
            'tool_name': result.tool_name
        }, indent=2)
    
    elif output_format == 'yaml':
        return yaml.dump({
            'return_code': result.return_code,
            'success': result.success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': result.duration,  
            'command': result.command,
            'tool_name': result.tool_name
        }, default_flow_style=False)
    
    else:  # text format
        status_color = "green" if result.success else "red"
        status_text = "SUCCESS" if result.success else f"FAILED (code: {result.return_code})"
        
        output = f"[{status_color}]{status_text}[/{status_color}] ({result.duration:.2f}s)\n"
        output += f"[dim]Command:[/dim] {result.command}\n"
        
        if result.stdout:
            output += f"\n[bold]STDOUT:[/bold]\n{result.stdout}"
        
        if result.stderr:
            output += f"\n[bold red]STDERR:[/bold red]\n{result.stderr}"
        
        return output


def _format_batch_results(results, output_format: str) -> str:
    """Format batch results for display."""
    if output_format == 'json':
        return json.dumps([{
            'return_code': r.return_code,
            'success': r.success,
            'stdout': r.stdout,
            'stderr': r.stderr,
            'duration': r.duration,
            'command': r.command,
            'tool_name': r.tool_name
        } for r in results], indent=2)
    
    elif output_format == 'yaml':
        return yaml.dump([{
            'return_code': r.return_code,
            'success': r.success,
            'stdout': r.stdout,
            'stderr': r.stderr,
            'duration': r.duration,
            'command': r.command,
            'tool_name': r.tool_name
        } for r in results], default_flow_style=False)
    
    else:  # text format
        success_count = sum(1 for r in results if r.success)
        total_duration = sum(r.duration for r in results)
        
        output = f"[bold]Batch Results:[/bold] {success_count}/{len(results)} successful\n"
        output += f"[dim]Total Duration:[/dim] {total_duration:.2f}s\n\n"
        
        for i, result in enumerate(results, 1):
            status_color = "green" if result.success else "red"
            status_text = "✓" if result.success else "✗"
            output += f"[{status_color}]{status_text}[/{status_color}] [{i:3d}] {result.command} ({result.duration:.2f}s)\n"
            
            if not result.success and result.stderr:
                output += f"    [red]{result.stderr[:100]}[/red]\n"
        
        return output


def _format_tool_info(tool_info: Dict[str, Any], output_format: str) -> str:
    """Format tool information for display."""
    if output_format == 'json':
        return json.dumps(tool_info, indent=2)
    
    elif output_format == 'yaml':
        return yaml.dump(tool_info, default_flow_style=False)
    
    else:  # text format
        table = Table(title=f"Tool Information: {tool_info['name']}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in tool_info.items():
            if key == 'name':
                continue
            
            if isinstance(value, (list, dict)):
                value_str = json.dumps(value, indent=2) if value else "None"
            else:
                value_str = str(value)
            
            table.add_row(key.replace('_', ' ').title(), value_str)
        
        return str(table)


def _format_tools_info(tools_info: Dict[str, Dict[str, Any]], output_format: str) -> str:
    """Format multiple tools information for display."""
    if output_format == 'json':
        return json.dumps(tools_info, indent=2)
    
    elif output_format == 'yaml':
        return yaml.dump(tools_info, default_flow_style=False)
    
    else:  # text format
        table = Table(title="Configured Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Executable Path", style="white")
        table.add_column("Status", style="white")
        table.add_column("Version", style="dim")
        
        for name, info in tools_info.items():
            if 'error' in info:
                status = f"[red]Error: {info['error']}[/red]"
                path = "N/A"
                version = "N/A"
            else:
                exists = info.get('executable_exists', False)
                status = "[green]✓ Available[/green]" if exists else "[red]✗ Not Found[/red]"
                path = info.get('executable_path', 'N/A')
                version = info.get('version_info', 'Unknown')[:50] + "..." if len(info.get('version_info', '')) > 50 else info.get('version_info', 'Unknown')
            
            table.add_row(name, path, status, version)
        
        return str(table)


def _load_batch_file(batch_file: Path) -> List[List[str]]:
    """Load batch arguments from file."""
    batch_args = []
    
    with open(batch_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                # Parse as JSON array or simple space-separated args
                if line.startswith('['):
                    args = json.loads(line)
                else:
                    # Simple space-separated (with basic quote handling)
                    args = []
                    current_arg = ""
                    in_quotes = False
                    quote_char = None
                    
                    for char in line:
                        if not in_quotes and char in ['"', "'"]:
                            in_quotes = True
                            quote_char = char
                        elif in_quotes and char == quote_char:
                            in_quotes = False
                            quote_char = None
                        elif not in_quotes and char == ' ':
                            if current_arg:
                                args.append(current_arg)
                                current_arg = ""
                        else:
                            current_arg += char
                    
                    if current_arg:
                        args.append(current_arg)
                
                batch_args.append(args)
                
            except Exception as e:
                raise click.ClickException(f"Error parsing line {line_num} in {batch_file}: {e}")
    
    return batch_args


def _create_example_config(config_path: Path) -> None:
    """Create an example configuration file."""
    example_config = {
        'tools': {
            'example_tool': {
                'executable_path': 'C:/path/to/tool.exe',
                'default_args': ['--verbose'],
                'timeout_seconds': 300,
                'retry_attempts': 3,
                'environment_vars': {
                    'TOOL_HOME': 'C:/tool',
                    'TOOL_LOG_LEVEL': 'INFO'
                },
                'validation_rules': {
                    'required_args': {
                        'args': ['--input']
                    },
                    'file_exists': {
                        'indices': [1]  # Check that second argument is existing file
                    }
                }
            }
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_path': 'postcodemon.log',
            'max_file_size': 10485760,
            'backup_count': 5,
            'json_format': False,
            'remote_endpoint': None
        },
        'profiles': {
            'development': {
                'logging': {'level': 'DEBUG'},
                'global_timeout': 1200
            },
            'production': {
                'logging': {'level': 'WARNING'},
                'global_timeout': 300
            }
        },
        'global_timeout': 600,
        'max_concurrent_jobs': 10,
        'temp_directory': None,
        'monitoring_enabled': False,
        'metrics_endpoint': None
    }
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(example_config, f, default_flow_style=False, indent=2)


def _display_active_processes(processes: Dict[str, Dict[str, Any]]) -> None:
    """Display active processes in a table."""
    table = Table(title="Active Processes")
    table.add_column("Process ID", style="cyan")
    table.add_column("Tool Name", style="white")
    table.add_column("PID", style="white")
    table.add_column("Status", style="white")
    table.add_column("CPU %", style="yellow")
    table.add_column("Memory (MB)", style="green")
    
    for process_id, info in processes.items():
        table.add_row(
            process_id,
            info.get('tool_name', 'Unknown'),
            str(info.get('pid', 'N/A')),
            info.get('status', 'Unknown'),
            f"{info.get('cpu_percent', 0):.1f}",
            f"{info.get('memory_mb', 0):.1f}"
        )
    
    console.print(table)