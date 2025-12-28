"""Initialize KNL in a repository."""

import typer
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm, Prompt
from typing_extensions import Annotated

from ..core.config import ConfigManager
from ..core.paths import KnlPaths
from ..models.config import LocalConfig, TaskConfig, TaskIDFormat

app = typer.Typer(no_args_is_help=False)
console = Console()


@app.command()
def main(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Reinitialize even if already initialized"),
    ] = False,
    task_format: Annotated[
        str | None,
        typer.Option("--format", help="Task ID format: jira or github"),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option("--project", "-p", help="Project identifier (JIRA project or GitHub repo)"),
    ] = None,
) -> None:
    """
    Initialize KNL in the current repository.

    Sets up the .knowledge directory structure and configuration.
    """
    # Check if already initialized
    if KnlPaths.is_knl_repo() and not force:
        console.print(
            "[yellow]KNL already initialized in this repository.[/yellow]",
            style="bold"
        )
        console.print("Use [cyan]--force[/cyan] to reinitialize.")
        raise typer.Exit(1)

    console.print("\n[bold blue]Initializing Knowledge Retention Library[/bold blue]\n")

    # Interactive setup if options not provided
    if not task_format:
        task_format = Prompt.ask(
            "Task ID format",
            choices=["jira", "github"],
            default="jira",
        )

    id_format = TaskIDFormat(task_format.lower())

    if not project:
        if id_format == TaskIDFormat.JIRA:
            project = Prompt.ask(
                "JIRA project code (e.g., PROJ)",
                default="PROJ",
            )
        else:
            project = Prompt.ask(
                "GitHub repository (e.g., owner/repo)",
                default="",
            )

    # Create directory structure
    console.print("\n[cyan]Creating directory structure...[/cyan]")
    KnlPaths.ensure_local_dirs()

    # Create .gitignore for .knowledge
    gitignore_path = Path(".knowledge") / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write("# Ignore everything in .knowledge by default\n")
            f.write("*\n")
            f.write("!.gitignore\n")
            f.write("\n# Optionally include specific items:\n")
            f.write("# !templates/\n")
            f.write("# !standards/\n")

    # Add .knowledge to root .gitignore
    root_gitignore = Path(".gitignore")
    knowledge_entry = ".knowledge/"

    if root_gitignore.exists():
        content = root_gitignore.read_text()
        if knowledge_entry not in content:
            with open(root_gitignore, "a") as f:
                f.write(f"\n# KNL Knowledge Base\n{knowledge_entry}\n")
    else:
        with open(root_gitignore, "w") as f:
            f.write(f"# KNL Knowledge Base\n{knowledge_entry}\n")

    # Create local configuration
    task_config = TaskConfig(
        id_format=id_format,
        jira_project=project if id_format == TaskIDFormat.JIRA else "",
        github_repo=project if id_format == TaskIDFormat.GITHUB else "",
    )

    local_config = LocalConfig(task=task_config)
    ConfigManager.save_local_config(local_config)

    # Create initial templates and standards
    _create_initial_templates()
    _create_initial_standards(id_format)

    console.print("\n[bold green]✓[/bold green] KNL initialized successfully!\n")
    console.print(f"  Task format: [cyan]{id_format.value}[/cyan]")
    console.print(f"  Project: [cyan]{project}[/cyan]")
    console.print(f"  Knowledge directory: [cyan].knowledge/[/cyan]\n")
    console.print("Next steps:")
    console.print("  • Create a task: [cyan]knl create {TASK-ID}[/cyan]")
    console.print("  • List tasks: [cyan]knl list[/cyan]")
    console.print("  • Get help: [cyan]knl --help[/cyan]\n")


def _create_initial_templates() -> None:
    """Create initial template files."""
    templates_dir = Path(".knowledge") / "templates"

    # Task context template
    context_template = templates_dir / "context.md"
    if not context_template.exists():
        context_template.write_text("""# {task_id}: {title}

## Description

{description}

## Context

<!-- Add relevant context about this task -->

## Approach

<!-- Describe your implementation approach -->

## Progress

<!-- Track your progress here -->

## Notes

<!-- Any additional notes or learnings -->
""")

    # Test template
    test_template = templates_dir / "test_template.py"
    if not test_template.exists():
        test_template.write_text("""\"\"\"Tests for {task_id}.\"\"\"

import pytest


class Test{normalized_id}:
    \"\"\"Test suite for {task_id}.\"\"\"

    def test_placeholder(self) -> None:
        \"\"\"Placeholder test.\"\"\"
        assert True
""")


def _create_initial_standards(id_format: TaskIDFormat) -> None:
    """Create initial development standards document."""
    standards_dir = Path(".knowledge") / "standards"
    dev_standards = standards_dir / "development.md"

    if not dev_standards.exists():
        dev_standards.write_text(f"""# Development Standards

## Task Management

- Task ID format: **{id_format.value}**
- All development work should be tracked in tasks
- Keep task context updated as work progresses

## Code Quality

- Write clean, readable code
- Add type hints to all functions
- Follow PEP 8 style guidelines
- Document complex logic

## Testing

- Write tests for new functionality
- Maintain test coverage
- Run tests before committing

## Documentation

- Update relevant documentation
- Keep inline comments meaningful
- Document breaking changes

## Git Workflow

- One task per branch
- Clear commit messages
- Reference task ID in commits
- Review code before merging

---

*This document will evolve as the project develops patterns and best practices.*
""")
