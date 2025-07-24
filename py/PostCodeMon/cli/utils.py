"""Utility functions for CLI commands."""

import sys
from pathlib import Path
import click
from rich.console import Console

# Handle both direct execution and package imports
try:
    from ..core.wrapper import ToolWrapper
    from ..core.errors import PostCodeMonError
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.wrapper import ToolWrapper
    from core.errors import PostCodeMonError

console = Console()


def create_wrapper(ctx: click.Context) -> ToolWrapper:
    """Create a ToolWrapper instance from CLI context."""
    return ToolWrapper(
        config_path=ctx.obj.get('config_path'),
        tool_name=ctx.obj.get('default_tool')
    )


def handle_error(error: Exception, quiet: bool = False) -> None:
    """Handle and display errors appropriately."""
    if isinstance(error, PostCodeMonError):
        if not quiet:
            console.print(f"[red]Error:[/red] {error.message}")
            if hasattr(error, 'error_code') and error.error_code:
                console.print(f"[dim]Error Code:[/dim] {error.error_code}")
        sys.exit(1)
    else:
        if not quiet:
            console.print(f"[red]Unexpected Error:[/red] {str(error)}")
            console.print_exception()
        sys.exit(2)