"""Documentation checking and synchronization commands."""

import json
import re
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table

from ..core.doc_analyzer import DocAnalyzer
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
    # Matches: ### `knl`, ### `knl init`, `knl create`, ```bash\nknl list\n```
    patterns = [
        r"###?\s+`(knl(?:\s+[a-z]+)*)`",  # Markdown headers with commands (including just 'knl')
        r"^(knl(?:\s+[a-z]+(?:\s+[a-z]+)*)?)",  # Commands in code blocks
        r"`(knl(?:\s+[a-z]+(?:\s+[a-z]+)*)?)`",  # Inline code with commands
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


def _format_command_markdown(info, prefix: str = "knl", include_group_header: bool = False) -> str:
    """
    Format command info as markdown documentation.

    Args:
        info: CommandInfo to format
        prefix: Command prefix for full path
        include_group_header: Whether to include header for command groups

    Returns:
        Markdown formatted documentation
    """

    lines = []
    current_path = f"{prefix} {info.name}".strip() if info.name else prefix

    # Handle command groups (like 'knl task', 'knl config', etc.)
    if info.name and info.is_group and include_group_header:
        lines.append(f"#### `{current_path}` - Command Group\n")
        if info.help_text:
            help_text = " ".join(info.help_text.split())
            lines.append(f"{help_text}\n")
        lines.append("See subcommands below.\n")

    # Handle individual commands
    if info.name and not info.is_group:
        # Command header
        lines.append(f"### `{current_path}`\n")

        # Description
        if info.help_text:
            # Clean up help text (remove extra whitespace)
            help_text = " ".join(info.help_text.split())
            lines.append(f"{help_text}\n")

        # Usage example
        lines.append("```bash")
        lines.append(current_path)
        lines.append("```\n")

        # Options
        if info.options:
            # Filter out automatic options
            user_options = [
                opt
                for opt in info.options
                if opt.name
                not in ["--help", "--install-completion", "--show-completion"]
            ]

            if user_options:
                lines.append("**Options:**\n")
                for opt in user_options:
                    # Format option line
                    opt_line = f"- `{opt.name}`"
                    if opt.help_text:
                        opt_line += f" - {opt.help_text}"
                    if not opt.required and opt.default:
                        opt_line += f" (default: `{opt.default}`)"
                    lines.append(opt_line)
                lines.append("")

    # Process subcommands recursively
    if info.subcommands:
        for _subcmd_name, subcmd_info in sorted(info.subcommands.items()):
            subcmd_md = _format_command_markdown(subcmd_info, current_path, include_group_header=True)
            if subcmd_md:
                lines.append(subcmd_md)

    return "\n".join(lines)


@app.command()
def sync(
    verify_only: Annotated[
        bool,
        typer.Option("--verify-only", help="Check sync without updating files"),
    ] = False,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file (default: docs/cli/commands.md)"),
    ] = None,
) -> None:
    """Extract CLI help and sync to documentation."""
    # Import here to avoid circular dependency
    from ..cli import app as main_app

    # Find docs directory
    docs_dir = _find_docs_dir()
    if not docs_dir:
        console.print("[red]Error:[/red] Could not find docs/ directory")
        raise typer.Exit(1)

    # Determine output file
    if output is None:
        output = docs_dir / "cli" / "commands.md"

    # Extract CLI structure
    console.print("[dim]Extracting CLI help information...[/dim]")
    info = extract_typer_app_info(main_app, "knl")

    # Generate markdown
    console.print("[dim]Generating markdown documentation...[/dim]")

    # Build the documentation content
    markdown_lines = [
        "# CLI Commands Reference\n",
        "This documentation is auto-generated from CLI help text.\n",
        "**Do not edit manually** - run `knl docs sync` to update.\n",
    ]

    # Add main KNL overview
    if info.help_text:
        markdown_lines.append("\n## Overview\n")
        markdown_lines.append(f"{info.help_text}\n")

    # Document the root knl command
    markdown_lines.append("\n## Main Command\n")
    markdown_lines.append("### `knl`\n")
    if info.help_text:
        markdown_lines.append(f"{info.help_text}\n")
    markdown_lines.append("```bash")
    markdown_lines.append("knl [COMMAND] [OPTIONS]")
    markdown_lines.append("```\n")
    markdown_lines.append("**Global Options:**\n")
    markdown_lines.append("- `--version`, `-v` - Show version and exit")
    markdown_lines.append("- `--help` - Show help message and exit\n")
    markdown_lines.append("Run `knl COMMAND --help` for detailed help on any command.\n")

    # Add commands organized by category
    if info.subcommands:
        # Group commands by category
        categories = {
            "Core Commands": ["init"],
            "Task Management": ["create", "list", "show", "delete", "task"],
            "Configuration": ["config"],
            "Knowledge Management": ["crumb"],
            "Documentation": ["docs"],
        }

        for category, cmd_names in categories.items():
            category_cmds = [
                (name, info.subcommands[name])
                for name in cmd_names
                if name in info.subcommands
            ]

            if category_cmds:
                markdown_lines.append(f"\n## {category}\n")
                for _cmd_name, cmd_info in category_cmds:
                    # Include group headers for command groups
                    cmd_md = _format_command_markdown(cmd_info, "knl", include_group_header=True)
                    if cmd_md:
                        markdown_lines.append(cmd_md)

    markdown_content = "\n".join(markdown_lines)

    # Check if content changed
    content_changed = True
    if output.exists():
        existing_content = output.read_text()
        content_changed = existing_content != markdown_content

    if verify_only:
        if content_changed:
            console.print(
                "[yellow]Warning:[/yellow] Documentation is out of sync with CLI"
            )
            console.print(f"  Run [cyan]knl docs sync[/cyan] to update {output}")
            raise typer.Exit(1)
        else:
            console.print("[green]✓[/green] Documentation is in sync with CLI")
        return

    if not content_changed:
        console.print(f"[dim]No changes needed - {output} is already up to date[/dim]")
        return

    # Write the file
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown_content)

    console.print("\n[green]✓[/green] Updated CLI documentation")
    console.print(f"  File: [cyan]{output}[/cyan]")
    console.print(f"  Commands documented: [cyan]{len(info.subcommands)}[/cyan]\n")


@app.command()
def update(
    task_id: Annotated[str, typer.Argument(help="Task ID to analyze")],
    scope: Annotated[
        Literal["task", "release"],
        typer.Option("--scope", "-s", help="Analysis scope"),
    ] = "task",
    auto_approve: Annotated[
        bool,
        typer.Option("--auto-approve", help="Auto-approve all changes without review"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show proposed changes without applying them"),
    ] = False,
) -> None:
    """
    AI-assisted documentation updates based on code changes.

    Analyzes code changes for a task and suggests documentation updates.
    Uses MCP server for AI-powered analysis and presents changes for approval.

    Examples:
        # Analyze task changes and suggest updates
        knl docs update gh-1

        # Analyze all changes since last release
        knl docs update gh-1 --scope release

        # Auto-approve all suggested changes
        knl docs update gh-1 --auto-approve

        # Preview changes without applying
        knl docs update gh-1 --dry-run
    """
    from ..core.task_utils import task_exists

    # Validate task exists
    if not task_exists(task_id):
        console.print(f"[red]Error:[/red] Task {task_id} not found")
        console.print("  Run [cyan]knl list[/cyan] to see available tasks")
        raise typer.Exit(1)

    console.print("\n[bold]Documentation Update Analysis[/bold]")
    console.print(f"Task: [cyan]{task_id}[/cyan]")
    console.print(f"Scope: [cyan]{scope}[/cyan]\n")

    # Step 1: Gather context
    console.print("[dim]Gathering context...[/dim]")
    analyzer = DocAnalyzer()

    try:
        context = analyzer.gather_context(task_id, scope=scope)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to gather context: {e}")
        raise typer.Exit(1) from None

    # Display analysis summary
    console.print(f"  Commits analyzed: [cyan]{len(context.commits)}[/cyan]")
    console.print(f"  Files changed: [cyan]{len(context.changed_files)}[/cyan]")
    console.print(f"  Diff size: [cyan]{len(context.diff)} chars[/cyan]\n")

    # Step 2: Identify gaps (heuristic analysis)
    console.print("[dim]Identifying documentation gaps...[/dim]")
    gaps = analyzer.identify_documentation_gaps(context)

    if not gaps:
        console.print("[green]✓[/green] No documentation gaps found!")
        console.print("  Documentation appears to be up to date.\n")
        return

    console.print(f"[yellow]Found {len(gaps)} potential gaps:[/yellow]")
    for i, gap in enumerate(gaps, 1):
        console.print(f"  {i}. {gap}")
    console.print()

    # Step 3: Call MCP server for AI analysis (TODO)
    console.print("[dim]AI-powered analysis...[/dim]")
    console.print(
        "[yellow]Note:[/yellow] MCP server integration not yet implemented"
    )
    console.print(
        "  This would call the knl-docs-analyzer MCP server to generate"
    )
    console.print("  specific documentation update proposals using AI.\n")

    # Step 4: Present proposals for approval (TODO)
    if dry_run:
        console.print("[dim]Dry run mode - no changes will be applied[/dim]\n")
        console.print("Next steps:")
        console.print("  1. Implement MCP server integration")
        console.print("  2. Build approval UI for reviewing changes")
        console.print("  3. Apply approved changes to documentation\n")
    else:
        console.print("[yellow]Warning:[/yellow] Approval UI not yet implemented")
        console.print("  Use --dry-run to preview the workflow\n")

    # Summary
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Task: {task_id}")
    console.print(f"  Scope: {scope}")
    console.print(f"  Gaps found: {len(gaps)}")
    console.print("  Status: [yellow]Analysis complete, pending implementation[/yellow]\n")
