"""Task management commands."""

import json
import typer
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from typing_extensions import Annotated

from ..core.config import ConfigManager
from ..core.paths import KnlPaths
from ..models.task import Task, TaskIDType, TaskMetadata, TaskStatus

app = typer.Typer()
console = Console()


def _require_knl_repo() -> Path:
    """Ensure we're in a KNL repository."""
    repo_root = KnlPaths.find_repo_root()
    if not repo_root:
        console.print(
            "[red]Error:[/red] Not in a KNL repository. "
            "Run [cyan]knl init[/cyan] first.",
            style="bold"
        )
        raise typer.Exit(1)
    return repo_root


@app.command()
def create(
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
    """Create a new task."""
    repo_root = _require_knl_repo()

    # Normalize and validate task ID
    normalized_id = Task.normalize_id(task_id)
    id_type = Task.detect_id_type(task_id)

    # Check if task already exists
    task_dir = KnlPaths.get_task_dir(normalized_id, repo_root)
    if task_dir.exists():
        console.print(f"[yellow]Task {task_id} already exists.[/yellow]")
        if not Confirm.ask("Overwrite existing task?"):
            raise typer.Exit(0)

    console.print(f"\n[bold blue]Creating task {task_id}[/bold blue]\n")

    # Create task metadata
    metadata = TaskMetadata(
        task_id=task_id,
        task_id_type=id_type,
        normalized_id=normalized_id,
        title=title,
        status=TaskStatus.TODO,
    )

    # TODO: Fetch metadata from JIRA/GitHub if enabled
    if fetch and not title:
        console.print("[dim]Metadata fetching not yet implemented[/dim]")

    # Create task structure
    task = Task(metadata=metadata, task_dir=task_dir)
    task.create_structure()

    # Save metadata
    with open(task.metadata_file, "w") as f:
        json.dump(
            metadata.model_dump(mode="json"),
            f,
            indent=2,
            default=str,
        )

    # Create context file from template
    _create_context_from_template(task, repo_root)

    console.print(f"[bold green]✓[/bold green] Task created: {task_id}")
    console.print(f"  Location: [cyan]{task_dir.relative_to(repo_root)}[/cyan]")
    console.print(f"  Context: [cyan]{task.context_file.relative_to(repo_root)}[/cyan]\n")


@app.command(name="list")
def list_tasks(
    status: Annotated[
        str | None,
        typer.Option("--status", "-s", help="Filter by status"),
    ] = None,
    all_tasks: Annotated[
        bool,
        typer.Option("--all", "-a", help="Include archived tasks"),
    ] = False,
) -> None:
    """List all tasks."""
    repo_root = _require_knl_repo()
    tasks_dir = repo_root / KnlPaths.LOCAL_TASKS_DIR

    if not tasks_dir.exists() or not list(tasks_dir.iterdir()):
        console.print("[yellow]No tasks found.[/yellow]")
        console.print("Create a task with: [cyan]knl create {TASK-ID}[/cyan]")
        raise typer.Exit(0)

    # Load all tasks
    tasks = []
    for task_dir in tasks_dir.iterdir():
        if not task_dir.is_dir():
            continue

        metadata_file = task_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        with open(metadata_file) as f:
            metadata = TaskMetadata(**json.load(f))

        # Filter by status
        if status and metadata.status.value != status:
            continue

        # Filter archived
        if not all_tasks and metadata.status == TaskStatus.ARCHIVED:
            continue

        tasks.append(metadata)

    if not tasks:
        console.print(f"[yellow]No tasks found with status: {status}[/yellow]")
        raise typer.Exit(0)

    # Sort by created_at
    tasks.sort(key=lambda t: t.created_at, reverse=True)

    # Display table
    table = Table(title="Tasks", show_header=True, header_style="bold cyan")
    table.add_column("Task ID", style="bold")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Created")
    table.add_column("Updated")

    for task in tasks:
        status_color = {
            TaskStatus.TODO: "yellow",
            TaskStatus.IN_PROGRESS: "blue",
            TaskStatus.IN_REVIEW: "magenta",
            TaskStatus.DONE: "green",
            TaskStatus.BLOCKED: "red",
            TaskStatus.ARCHIVED: "dim",
        }.get(task.status, "white")

        table.add_row(
            task.task_id,
            task.title or "[dim]No title[/dim]",
            f"[{status_color}]{task.status.value}[/{status_color}]",
            task.created_at.strftime("%Y-%m-%d"),
            task.updated_at.strftime("%Y-%m-%d"),
        )

    console.print(table)
    console.print(f"\nTotal: {len(tasks)} task(s)")


@app.command()
def show(
    task_id: Annotated[
        str,
        typer.Argument(help="Task ID to show"),
    ],
) -> None:
    """Show task details."""
    repo_root = _require_knl_repo()
    normalized_id = Task.normalize_id(task_id)
    task_dir = KnlPaths.get_task_dir(normalized_id, repo_root)

    if not task_dir.exists():
        console.print(f"[red]Error:[/red] Task {task_id} not found.")
        raise typer.Exit(1)

    metadata_file = task_dir / "metadata.json"
    with open(metadata_file) as f:
        metadata = TaskMetadata(**json.load(f))

    # Display task details
    console.print(f"\n[bold blue]{metadata.task_id}[/bold blue]: {metadata.title}\n")

    if metadata.description:
        console.print(f"[bold]Description:[/bold]\n{metadata.description}\n")

    console.print(f"[bold]Status:[/bold] {metadata.status.value}")
    console.print(f"[bold]Type:[/bold] {metadata.task_id_type.value}")
    console.print(f"[bold]Created:[/bold] {metadata.created_at}")
    console.print(f"[bold]Updated:[/bold] {metadata.updated_at}")

    if metadata.completed_at:
        console.print(f"[bold]Completed:[/bold] {metadata.completed_at}")

    if metadata.external_url:
        console.print(f"[bold]URL:[/bold] {metadata.external_url}")

    if metadata.branch_name:
        console.print(f"[bold]Branch:[/bold] {metadata.branch_name}")

    if metadata.tags:
        console.print(f"[bold]Tags:[/bold] {', '.join(metadata.tags)}")

    if metadata.labels:
        console.print(f"[bold]Labels:[/bold] {', '.join(metadata.labels)}")

    console.print(f"\n[bold]Location:[/bold] {task_dir.relative_to(repo_root)}")
    console.print(f"[bold]Context file:[/bold] {(task_dir / 'context.md').relative_to(repo_root)}\n")


@app.command()
def delete(
    task_id: Annotated[
        str,
        typer.Argument(help="Task ID to delete"),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation"),
    ] = False,
) -> None:
    """Delete a task."""
    repo_root = _require_knl_repo()
    normalized_id = Task.normalize_id(task_id)
    task_dir = KnlPaths.get_task_dir(normalized_id, repo_root)

    if not task_dir.exists():
        console.print(f"[red]Error:[/red] Task {task_id} not found.")
        raise typer.Exit(1)

    if not force:
        if not Confirm.ask(f"Delete task {task_id} and all its data?"):
            console.print("Cancelled.")
            raise typer.Exit(0)

    # Delete task directory
    import shutil
    shutil.rmtree(task_dir)

    console.print(f"[bold green]✓[/bold green] Task {task_id} deleted.")


@app.command()
def update(
    task_id: Annotated[
        str,
        typer.Argument(help="Task ID to update"),
    ],
    status: Annotated[
        str | None,
        typer.Option("--status", "-s", help="Update status"),
    ] = None,
    title: Annotated[
        str | None,
        typer.Option("--title", "-t", help="Update title"),
    ] = None,
) -> None:
    """Update task metadata."""
    repo_root = _require_knl_repo()
    normalized_id = Task.normalize_id(task_id)
    task_dir = KnlPaths.get_task_dir(normalized_id, repo_root)

    if not task_dir.exists():
        console.print(f"[red]Error:[/red] Task {task_id} not found.")
        raise typer.Exit(1)

    metadata_file = task_dir / "metadata.json"
    with open(metadata_file) as f:
        metadata = TaskMetadata(**json.load(f))

    # Update fields
    if status:
        try:
            metadata.status = TaskStatus(status)
            if metadata.status == TaskStatus.DONE and not metadata.completed_at:
                metadata.completed_at = datetime.now()
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid status: {status}")
            raise typer.Exit(1)

    if title:
        metadata.title = title

    metadata.updated_at = datetime.now()

    # Save updated metadata
    with open(metadata_file, "w") as f:
        json.dump(
            metadata.model_dump(mode="json"),
            f,
            indent=2,
            default=str,
        )

    console.print(f"[bold green]✓[/bold green] Task {task_id} updated.")


def _create_context_from_template(task: Task, repo_root: Path) -> None:
    """Create context file from template."""
    template_file = repo_root / KnlPaths.LOCAL_TEMPLATES_DIR / "context.md"

    if template_file.exists():
        template_content = template_file.read_text()
    else:
        # Fallback template
        template_content = """# {task_id}: {title}

## Description

{description}

## Context

<!-- Add relevant context -->

## Progress

<!-- Track progress -->
"""

    # Fill template
    content = template_content.format(
        task_id=task.metadata.task_id,
        title=task.metadata.title or "No title",
        description=task.metadata.description or "No description",
        normalized_id=task.metadata.normalized_id,
    )

    task.context_file.write_text(content)
