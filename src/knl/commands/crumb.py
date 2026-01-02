"""Crumb management commands."""

from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from knl.core.crumbs import CrumbManager
from knl.models.crumb import Crumb

app = typer.Typer(help="Browse and manage knowledge crumbs")
console = Console()


@app.command(name="list")
def list_crumbs(
    category: Annotated[
        str | None,
        typer.Option("--category", "-c", help="Filter by category"),
    ] = None,
    tag: Annotated[
        list[str] | None,
        typer.Option("--tag", "-t", help="Filter by tag (can specify multiple)"),
    ] = None,
    difficulty: Annotated[
        str | None,
        typer.Option("--difficulty", "-d", help="Filter by difficulty"),
    ] = None,
    sort: Annotated[
        str,
        typer.Option(help="Sort by: title, created, updated, difficulty, category"),
    ] = "category",
    format: Annotated[
        str,
        typer.Option(help="Output format: table, compact, json"),
    ] = "table",
):
    """List all available crumbs with optional filtering."""
    manager = CrumbManager()

    if not manager.crumbs_dir:
        console.print(
            "[yellow]No crumbs directory found.[/yellow]\n"
            "Crumbs should be in .knl/know-how/crumbs/ or ~/.local/knl/know-how/crumbs/",
            style="yellow",
        )
        raise typer.Exit(1)

    # Get crumbs with filters
    crumbs = manager.list_crumbs(category=category, tags=tag, difficulty=difficulty)

    if not crumbs:
        console.print("[yellow]No crumbs found matching your filters.[/yellow]")
        raise typer.Exit(0)

    # Sort crumbs
    crumbs = _sort_crumbs(crumbs, sort)

    # Display based on format
    if format == "table":
        _display_table(crumbs)
    elif format == "compact":
        _display_compact(crumbs)
    elif format == "json":
        _display_json(crumbs)
    else:
        console.print(f"[red]Unknown format: {format}[/red]")
        raise typer.Exit(1)


@app.command()
def show(
    crumb_path: Annotated[str, typer.Argument(help="Crumb path (e.g., devops/github-pages-setup)")],
    line_numbers: Annotated[
        bool,
        typer.Option("--line-numbers", "-n", help="Show line numbers"),
    ] = False,
    raw: Annotated[
        bool,
        typer.Option("--raw", help="Show raw markdown without rendering"),
    ] = False,
):
    """Show the full content of a crumb."""
    manager = CrumbManager()

    crumb = manager.get_crumb(crumb_path)
    if not crumb:
        console.print(f"[red]Crumb not found: {crumb_path}[/red]")
        console.print("\nUse 'knl crumb list' to see available crumbs")
        raise typer.Exit(1)

    # Display header
    console.print(f"\n[bold cyan]📄 {crumb.metadata.title}[/bold cyan]")
    console.print(f"[dim]{crumb.category_path}[/dim]\n")

    # Display content
    if raw:
        console.print(crumb.content)
    else:
        md = Markdown(crumb.content)
        console.print(md)

    # Display footer
    console.print(f"\n[dim]Location: {crumb.file_path}[/dim]")


@app.command()
def info(
    crumb_path: Annotated[str, typer.Argument(help="Crumb path")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON"),
    ] = False,
):
    """Display metadata about a crumb."""
    manager = CrumbManager()

    crumb = manager.get_crumb(crumb_path)
    if not crumb:
        console.print(f"[red]Crumb not found: {crumb_path}[/red]")
        raise typer.Exit(1)

    if json_output:
        import json

        output = {
            "path": str(crumb.path),
            "title": crumb.metadata.title,
            "description": crumb.metadata.description,
            "category": crumb.metadata.category,
            "tags": crumb.metadata.tags,
            "difficulty": crumb.metadata.difficulty,
            "created": str(crumb.metadata.created),
            "updated": str(crumb.metadata.updated),
            "author": crumb.metadata.author,
            "prerequisites": crumb.metadata.prerequisites,
            "applies_to": crumb.metadata.applies_to,
            "related": crumb.metadata.related,
            "file_path": str(crumb.file_path),
        }
        console.print(json.dumps(output, indent=2))
    else:
        _display_info(crumb)


@app.command()
def find(
    query: Annotated[str, typer.Argument(help="Search query")],
    in_field: Annotated[
        str | None,
        typer.Option("--in", help="Search in: title, description, tags, content"),
    ] = None,
    case_sensitive: Annotated[
        bool,
        typer.Option("--case-sensitive", "-s", help="Case-sensitive search"),
    ] = False,
):
    """Find crumbs by searching content and metadata."""
    manager = CrumbManager()

    if not manager.crumbs_dir:
        console.print("[yellow]No crumbs directory found.[/yellow]")
        raise typer.Exit(1)

    crumbs = manager.find_crumbs(query, in_field=in_field, case_sensitive=case_sensitive)

    if not crumbs:
        console.print(f"[yellow]No crumbs found matching '{query}'[/yellow]")
        raise typer.Exit(0)

    # Display results
    console.print(f"\n[bold]🔍 Found {len(crumbs)} crumb(s) matching '{query}'[/bold]\n")
    _display_table(crumbs)


@app.command()
def categories(
    describe: Annotated[
        bool,
        typer.Option("--describe", "-d", help="Show category descriptions"),
    ] = False,
):
    """List all available categories."""
    manager = CrumbManager()

    if not manager.crumbs_dir:
        console.print("[yellow]No crumbs directory found.[/yellow]")
        raise typer.Exit(1)

    categories_dict = manager.get_categories()

    if not categories_dict:
        console.print("[yellow]No categories found.[/yellow]")
        raise typer.Exit(0)

    # Category descriptions
    descriptions = {
        "devops": "DevOps, CI/CD, deployment, infrastructure",
        "development": "Development practices, patterns, workflows",
        "testing": "Testing strategies, frameworks, debugging",
        "security": "Security best practices, vulnerability fixes",
        "tooling": "Tool configuration, usage, optimization",
    }

    console.print("\n[bold cyan]📁 Crumb Categories[/bold cyan]\n")

    if describe:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Category")
        table.add_column("Count", justify="right")
        table.add_column("Description")

        for cat, count in categories_dict.items():
            desc = descriptions.get(cat, "")
            table.add_row(cat, str(count), desc)

        console.print(table)
    else:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Category")
        table.add_column("Count", justify="right")

        for cat, count in categories_dict.items():
            table.add_row(cat, str(count))

        console.print(table)

    total = sum(categories_dict.values())
    console.print(f"\n[dim]Total: {total} crumb(s) across {len(categories_dict)} categories[/dim]")


@app.command()
def tags(
    sort_by: Annotated[
        str,
        typer.Option("--sort", help="Sort by: name, count"),
    ] = "name",
    filter_tag: Annotated[
        str | None,
        typer.Option("--filter", help="Filter tags containing text"),
    ] = None,
):
    """List all available tags."""
    manager = CrumbManager()

    if not manager.crumbs_dir:
        console.print("[yellow]No crumbs directory found.[/yellow]")
        raise typer.Exit(1)

    tags_dict = manager.get_tags()

    if not tags_dict:
        console.print("[yellow]No tags found.[/yellow]")
        raise typer.Exit(0)

    # Filter tags if requested
    if filter_tag:
        tags_dict = {t: c for t, c in tags_dict.items() if filter_tag.lower() in t.lower()}

    # Sort tags
    if sort_by == "count":
        tags_dict = dict(sorted(tags_dict.items(), key=lambda x: x[1], reverse=True))

    console.print("\n[bold cyan]🏷️  Available Tags[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Tag")
    table.add_column("Count", justify="right")

    for tag, count in tags_dict.items():
        table.add_row(tag, str(count))

    console.print(table)

    total = len(tags_dict)
    console.print(f"\n[dim]Total: {total} unique tag(s)[/dim]")


# Helper functions


def _sort_crumbs(crumbs: list[Crumb], sort_by: str) -> list[Crumb]:
    """Sort crumbs by specified field."""
    if sort_by == "title":
        return sorted(crumbs, key=lambda c: c.metadata.title)
    elif sort_by == "created":
        return sorted(crumbs, key=lambda c: c.metadata.created, reverse=True)
    elif sort_by == "updated":
        return sorted(crumbs, key=lambda c: c.metadata.updated, reverse=True)
    elif sort_by == "difficulty":
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        return sorted(crumbs, key=lambda c: difficulty_order.get(c.metadata.difficulty, 99))
    elif sort_by == "category":
        return sorted(crumbs, key=lambda c: (c.metadata.category, c.metadata.title))
    else:
        return crumbs


def _display_table(crumbs: list[Crumb]):
    """Display crumbs as a table."""
    console.print(f"\n[bold]📚 Available Crumbs ({len(crumbs)} found)[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("Difficulty")
    table.add_column("Updated")
    table.add_column("Tags")

    for crumb in crumbs:
        tags_str = ", ".join(crumb.metadata.tags[:3])
        if len(crumb.metadata.tags) > 3:
            tags_str += "..."

        table.add_row(
            crumb.metadata.category,
            crumb.metadata.title,
            crumb.metadata.difficulty,
            str(crumb.metadata.updated),
            tags_str,
        )

    console.print(table)
    console.print("\n[dim]Use 'knl crumb show <category>/<filename>' to view a crumb[/dim]")


def _display_compact(crumbs: list[Crumb]):
    """Display crumbs in compact format."""
    for crumb in crumbs:
        console.print(f"{crumb.slug}")


def _display_json(crumbs: list[Crumb]):
    """Display crumbs as JSON."""
    import json

    output = []
    for crumb in crumbs:
        output.append(
            {
                "path": str(crumb.path),
                "title": crumb.metadata.title,
                "description": crumb.metadata.description,
                "category": crumb.metadata.category,
                "tags": crumb.metadata.tags,
                "difficulty": crumb.metadata.difficulty,
                "updated": str(crumb.metadata.updated),
            }
        )

    console.print(json.dumps(output, indent=2))


def _display_info(crumb: Crumb):
    """Display crumb info in a nice format."""
    meta = crumb.metadata

    console.print(f"\n[bold cyan]📄 {crumb.category_path}[/bold cyan]\n")

    console.print(f"[bold]Title:[/bold]        {meta.title}")
    console.print(f"[bold]Description:[/bold]  {meta.description}")
    console.print(f"[bold]Category:[/bold]     {meta.category}")
    console.print(f"[bold]Difficulty:[/bold]   {meta.difficulty}")
    console.print(f"[bold]Created:[/bold]      {meta.created}")
    console.print(f"[bold]Updated:[/bold]      {meta.updated}")
    console.print(f"[bold]Author:[/bold]       {meta.author}")

    if meta.tags:
        console.print(f"\n[bold]Tags:[/bold]         {', '.join(meta.tags)}")

    if meta.prerequisites:
        console.print("\n[bold]Prerequisites:[/bold]")
        for prereq in meta.prerequisites:
            console.print(f"  • {prereq}")

    if meta.applies_to:
        console.print("\n[bold]Applies To:[/bold]")
        for item in meta.applies_to:
            console.print(f"  • {item}")

    if meta.related:
        console.print("\n[bold]Related:[/bold]")
        for rel in meta.related:
            console.print(f"  • {rel}")

    console.print(f"\n[dim]Location: {crumb.file_path}[/dim]")
