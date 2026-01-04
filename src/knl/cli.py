"""Main CLI entry point for KNL."""

from typing import Annotated

import typer
from rich.console import Console

from . import __version__
from .commands import config as config_cmd
from .commands import crumb as crumb_cmd
from .commands import docs as docs_cmd
from .commands import init as init_cmd
from .commands import task as task_cmd

# Create main app
app = typer.Typer(
    name="knl",
    help="Knowledge Retention Library - AI-powered task management and development assistant",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Console for rich output
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold blue]knl[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = False,
) -> None:
    """Knowledge Retention Library - AI-powered development assistant."""
    pass


# Register command groups
app.command(name="init", help="Initialize KNL in a repository")(init_cmd.main)
app.add_typer(task_cmd.app, name="task", help="Manage development tasks")
app.add_typer(config_cmd.app, name="config", help="Manage configuration")
app.add_typer(crumb_cmd.app, name="crumb", help="Browse and manage knowledge crumbs")
app.add_typer(docs_cmd.app, name="docs", help="Documentation checking and synchronization")


# Convenience commands at root level
@app.command(name="create")
def create_task(
    task_id: Annotated[
        str,
        typer.Argument(help="Task ID (e.g., PROJ-123 or #456)"),
    ],
    title: Annotated[
        str,
        typer.Option("--title", "-t", help="Task title"),
    ] = "",
    fetch: Annotated[
        bool,
        typer.Option("--fetch/--no-fetch", "-f/-F", help="Fetch metadata from remote"),
    ] = True,
) -> None:
    """Create a new task (shortcut for 'knl task create')."""
    task_cmd.create(task_id=task_id, title=title, fetch=fetch)


@app.command(name="list")
def list_tasks(
    status: Annotated[
        str | None,
        typer.Option("--status", "-s", help="Filter by status"),
    ] = None,
    all: Annotated[
        bool,
        typer.Option("--all", "-a", help="Include archived tasks"),
    ] = False,
) -> None:
    """List all tasks (shortcut for 'knl task list')."""
    task_cmd.list_tasks(status=status, all_tasks=all)


@app.command(name="show")
def show_task(
    task_id: Annotated[
        str,
        typer.Argument(help="Task ID to show"),
    ],
) -> None:
    """Show task details (shortcut for 'knl task show')."""
    task_cmd.show(task_id=task_id)


@app.command(name="delete")
def delete_task(
    task_id: Annotated[
        str,
        typer.Argument(help="Task ID to delete"),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation"),
    ] = False,
) -> None:
    """Delete a task (shortcut for 'knl task delete')."""
    task_cmd.delete(task_id=task_id, force=force)


@app.command(name="help")
def help_command(ctx: typer.Context) -> None:
    """Show help information (equivalent to --help)."""
    # Get the parent context (main app) and print its help
    parent_ctx = ctx.parent
    if parent_ctx:
        console.print(parent_ctx.get_help())
    else:
        console.print(ctx.get_help())
    raise typer.Exit()


@app.command(name="version")
def version_command() -> None:
    """Show detailed version information."""
    import subprocess
    import sys
    from pathlib import Path

    console.print("\n[bold blue]KNL[/bold blue] - Knowledge Retention Library\n")
    console.print(f"Version: [green]{__version__}[/green]")

    # Get Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"Python: [cyan]{python_version}[/cyan]")

    # Check if there's a pinned Python version
    try:
        # Find KNL installation directory
        knl_module_path = Path(__file__).parent.parent.parent
        python_version_file = knl_module_path / ".knl" / ".python-version"
        if python_version_file.exists():
            pinned_version = python_version_file.read_text().strip()
            console.print(f"Pinned Python: [cyan]{pinned_version}[/cyan]")
    except Exception:
        pass

    # Get last commit timestamp if in a git repo
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            timestamp = result.stdout.strip()
            console.print(f"Last commit: [yellow]{timestamp}[/yellow]")
    except Exception:
        pass

    # Count crumbs if available
    try:
        # Look for crumbs in KNL installation
        knl_module_path = Path(__file__).parent.parent.parent
        crumbs_dir = knl_module_path / ".knl" / "know-how" / "crumbs"
        if not crumbs_dir.exists():
            # Try local know-how directory
            crumbs_dir = knl_module_path / "know-how" / "crumbs"

        if crumbs_dir.exists():
            crumb_count = sum(1 for _ in crumbs_dir.rglob("*.md"))
            console.print(f"Knowledge crumbs: [magenta]{crumb_count}[/magenta] available")
        else:
            console.print("Knowledge crumbs: [dim]none installed[/dim]")
    except Exception:
        pass

    console.print()
    raise typer.Exit()


if __name__ == "__main__":
    app()
