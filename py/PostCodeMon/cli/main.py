"""Main CLI entry point for PostCodeMon."""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.traceback import install

# Handle both direct execution and package imports
try:
    from .commands import (
        execute_command,
        batch_command,
        info_command,
        config_command,
        monitor_command,
        clean_command
    )
    from .utils import handle_error
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from cli.commands import (
        execute_command,
        batch_command,
        info_command,
        config_command,
        monitor_command,
        clean_command
    )
    from cli.utils import handle_error

# Install rich traceback handler for better error display
install(show_locals=True)
console = Console()


@click.group(invoke_without_command=True)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, path_type=Path),
    help='Path to configuration file'
)
@click.option(
    '--tool', '-t',
    help='Default tool name to use'
)
@click.option(
    '--verbose', '-v',
    count=True,
    help='Increase verbosity (use -vv for debug)'
)
@click.option(
    '--quiet', '-q',
    is_flag=True,
    help='Suppress output except errors'
)
@click.version_option(version='0.1.0', prog_name='PostCodeMon')
@click.pass_context
def cli(ctx: click.Context, config: Optional[Path], tool: Optional[str], 
        verbose: int, quiet: bool):
    """
    PostCodeMon - Modern Python wrapper for Windows CLI tools.
    
    A comprehensive framework for wrapping legacy Windows executables with
    modern Python interfaces, enhanced error handling, logging, and automation.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set up logging level based on verbosity
    if quiet:
        log_level = 'ERROR'
    elif verbose >= 2:
        log_level = 'DEBUG'
    elif verbose >= 1:
        log_level = 'INFO'
    else:
        log_level = 'WARNING'
    
    # Store configuration in context
    ctx.obj['config_path'] = config
    ctx.obj['default_tool'] = tool
    ctx.obj['log_level'] = log_level
    ctx.obj['quiet'] = quiet
    
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


# Add subcommands
cli.add_command(execute_command)
cli.add_command(batch_command)
cli.add_command(info_command)
cli.add_command(config_command)
cli.add_command(monitor_command)
cli.add_command(clean_command)




def main():
    """Main entry point for the CLI application."""
    try:
        cli()
    except Exception as e:
        handle_error(e)


if __name__ == '__main__':
    main()