"""Configuration management commands."""

from typing import Annotated

import typer
from rich.console import Console

from ..core.config import ConfigManager
from ..core.paths import KnlPaths

app = typer.Typer()
console = Console()


@app.command(name="get")
def get_config(
    key: Annotated[
        str,
        typer.Argument(help="Configuration key (dot notation, e.g., 'task.id_format')"),
    ],
    local: Annotated[
        bool,
        typer.Option("--local", "-l", help="Get local config only"),
    ] = False,
) -> None:
    """Get a configuration value."""
    value = ConfigManager.get_config_value(key)

    if value is None:
        console.print(f"[yellow]Configuration key '{key}' not found.[/yellow]")
        raise typer.Exit(1)

    console.print(f"[cyan]{key}[/cyan] = {value}")


@app.command(name="set")
def set_config(
    key: Annotated[
        str,
        typer.Argument(help="Configuration key (dot notation)"),
    ],
    value: Annotated[
        str,
        typer.Argument(help="Value to set"),
    ],
    local: Annotated[
        bool,
        typer.Option("--local", "-l", help="Set in local config"),
    ] = False,
) -> None:
    """Set a configuration value."""
    ConfigManager.set_config_value(key, value, local=local)

    scope = "local" if local else "global"
    console.print(f"[bold green]✓[/bold green] Set {scope} config: [cyan]{key}[/cyan] = {value}")


@app.command(name="list")
def list_config(
    local: Annotated[
        bool,
        typer.Option("--local", "-l", help="Show local config only"),
    ] = False,
    global_only: Annotated[
        bool,
        typer.Option("--global", "-g", help="Show global config only"),
    ] = False,
) -> None:
    """List all configuration values."""
    if not global_only:
        # Try to load local config
        local_config = ConfigManager.load_local_config()
        if local_config:
            console.print("\n[bold blue]Local Configuration[/bold blue] (.knowledge/config.toml)\n")
            _print_config_dict(local_config.model_dump(mode="json", exclude_none=True))

    if not local or global_only:
        # Load global config
        global_config = ConfigManager.load_global_config()
        console.print("\n[bold blue]Global Configuration[/bold blue] (~/.config/knl/config.toml)\n")
        _print_config_dict(global_config.model_dump(mode="json", exclude_none=True))


def _print_config_dict(config: dict, prefix: str = "") -> None:
    """Recursively print configuration dictionary."""
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            _print_config_dict(value, full_key)
        else:
            console.print(f"  [cyan]{full_key}[/cyan] = {value}")


@app.command(name="edit")
def edit_config(
    local: Annotated[
        bool,
        typer.Option("--local", "-l", help="Edit local config"),
    ] = False,
) -> None:
    """Open configuration file in editor."""
    import os
    import subprocess

    if local:
        if not KnlPaths.is_knl_repo():
            console.print(
                "[red]Error:[/red] Not in a KNL repository. "
                "Use [cyan]--global[/cyan] or run [cyan]knl init[/cyan] first."
            )
            raise typer.Exit(1)

        config_file = KnlPaths.LOCAL_CONFIG_FILE
    else:
        KnlPaths.ensure_global_dirs()
        config_file = KnlPaths.GLOBAL_CONFIG_FILE

        # Create default config if it doesn't exist
        if not config_file.exists():
            ConfigManager.save_global_config(ConfigManager.load_global_config())

    editor = os.environ.get("EDITOR", "vim")
    subprocess.run([editor, str(config_file)])

    console.print(f"[bold green]✓[/bold green] Configuration file edited: {config_file}")
