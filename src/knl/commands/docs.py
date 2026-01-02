"""Documentation checking and synchronization commands."""

import json
import re
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ..utils.cli_help import (
    extract_typer_app_info,
    format_help_as_dict,
    get_all_command_paths,
)

app = typer.Typer(help="Documentation commands")
console = Console()


def _find_docs_dir() -> Path | None:
    """Find the docs directory in the project."""
    # Start from current directory and search upward
    current = Path.cwd()
    for parent in [current, *current.parents]:
        docs_dir = parent / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            return docs_dir

    return None


def _extract_cli_commands(typer_app: typer.Typer) -> set[str]:
    """
    Extract all CLI command paths from the Typer app.

    Args:
        typer_app: Typer application to extract from

    Returns:
        Set of command paths (e.g., {'knl', 'knl init', 'knl task update'})
    """
    info = extract_typer_app_info(typer_app, "knl")
    paths = get_all_command_paths(info)
    return set(paths)


def _extract_documented_commands(docs_dir: Path) -> set[str]:
    """
    Extract command references from documentation files.

    Args:
        docs_dir: Path to documentation directory

    Returns:
        Set of documented command paths
    """
    documented = set()

    # Pattern to match command references in markdown
    # Matches: ### `knl init`, `knl create`, ```bash\nknl list\n```
    patterns = [
        r"###?\s+`(knl[^`]+)`",  # Markdown headers with commands
        r"^(knl\s+[a-z]+(?:\s+[a-z]+)*)",  # Commands in code blocks
        r"`(knl\s+[a-z]+(?:\s+[a-z]+)*)`",  # Inline code with commands
    ]

    # Search all markdown files
    for md_file in docs_dir.rglob("*.md"):
        try:
            content = md_file.read_text()

            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    cmd = match.group(1).strip()

                    # Clean up command (remove options/arguments)
                    # "knl create PROJ-123" -> "knl create"
                    parts = cmd.split()
                    clean_parts = []
                    for part in parts:
                        # Stop at options (--flag) or arguments (UPPER_CASE, #123)
                        if (
                            part.startswith("-")
                            or part.isupper()
                            or part.startswith("#")
                            or part.startswith('"')
                        ):
                            break
                        clean_parts.append(part)

                    if clean_parts:
                        clean_cmd = " ".join(clean_parts)
                        documented.add(clean_cmd)

        except (OSError, UnicodeDecodeError):
            # Skip files that can't be read
            continue

    return documented


@app.command()
def check(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed information"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output results as JSON"),
    ] = False,
) -> None:
    """Check documentation coverage for CLI commands."""
    # Import main app here (after cli.py has finished initializing)
    from ..cli import app as main_app

    # Find docs directory
    docs_dir = _find_docs_dir()
    if not docs_dir:
        console.print("[red]Error:[/red] Could not find docs/ directory")
        raise typer.Exit(1)

    # Extract commands from CLI and docs
    cli_commands = _extract_cli_commands(main_app)
    documented_commands = _extract_documented_commands(docs_dir)

    # Find discrepancies
    undocumented = cli_commands - documented_commands
    potentially_stale = documented_commands - cli_commands

    # Calculate coverage
    total_commands = len(cli_commands)
    documented_count = len(cli_commands & documented_commands)
    coverage_pct = (
        (documented_count / total_commands * 100) if total_commands > 0 else 0
    )

    if json_output:
        # Output as JSON
        result = {
            "total_commands": total_commands,
            "documented_commands": documented_count,
            "coverage_percentage": round(coverage_pct, 2),
            "undocumented": sorted(undocumented),
            "potentially_stale": sorted(potentially_stale),
        }
        console.print(json.dumps(result, indent=2))
        return

    # Display results
    console.print("\n[bold]Documentation Coverage Report[/bold]\n")
    console.print(f"Documentation directory: [cyan]{docs_dir}[/cyan]")
    console.print(
        f"Coverage: [{'green' if coverage_pct >= 80 else 'yellow' if coverage_pct >= 50 else 'red'}]"
        f"{documented_count}/{total_commands} commands ({coverage_pct:.1f}%)"
        f"[/{'green' if coverage_pct >= 80 else 'yellow' if coverage_pct >= 50 else 'red'}]\n"
    )

    # Show undocumented commands
    if undocumented:
        console.print(
            f"[yellow]Undocumented commands ({len(undocumented)}):[/yellow]"
        )
        for cmd in sorted(undocumented):
            console.print(f"  - [yellow]{cmd}[/yellow]")
        console.print()

    # Show potentially stale documentation
    if potentially_stale:
        console.print(
            f"[dim]Potentially stale documentation ({len(potentially_stale)}):[/dim]"
        )
        for cmd in sorted(potentially_stale):
            console.print(f"  - [dim]{cmd}[/dim]")
        console.print()

    # Show all commands if verbose
    if verbose:
        table = Table(title="All Commands", show_header=True, header_style="bold cyan")
        table.add_column("Command")
        table.add_column("Status")

        all_commands = cli_commands | documented_commands
        for cmd in sorted(all_commands):
            if cmd in cli_commands and cmd in documented_commands:
                status = "[green]Documented[/green]"
            elif cmd in cli_commands:
                status = "[yellow]Missing docs[/yellow]"
            else:
                status = "[dim]Potentially stale[/dim]"

            table.add_row(cmd, status)

        console.print(table)

    # Exit with error if coverage is low
    if coverage_pct < 80:
        console.print(
            "[yellow]Warning:[/yellow] Documentation coverage is below 80%\n"
        )
        raise typer.Exit(1)

    console.print("[green]✓[/green] Documentation coverage looks good!\n")


@app.command()
def dump(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file (default: stdout)"),
    ] = None,
) -> None:
    """Dump CLI help information as JSON."""
    # Import here to avoid circular dependency
    from ..cli import app as main_app

    # Extract CLI structure
    info = extract_typer_app_info(main_app, "knl")
    data = format_help_as_dict(info)

    # Format as JSON
    json_str = json.dumps(data, indent=2)

    if output:
        output.write_text(json_str)
        console.print(f"[green]✓[/green] Wrote CLI help to {output}")
    else:
        console.print(json_str)
