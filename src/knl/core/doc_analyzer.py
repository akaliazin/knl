"""Documentation analysis and context gathering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..core.task_utils import (
    get_task_commits,
    get_task_context,
    get_task_creation_time,
    get_task_metadata,
)
from ..utils.git import (
    Commit,
    get_changed_files,
    get_commits_since,
    get_diff_since,
    get_last_release_tag,
)


@dataclass
class DocumentationContext:
    """
    Context bundle for documentation analysis.

    Contains all information needed for AI to analyze and suggest documentation updates.
    """

    # Task information
    task_id: str
    task_title: str
    task_description: str
    task_context: str

    # Code changes
    commits: list[Commit]
    diff: str
    changed_files: list[str]

    # Scope information
    scope: Literal["task", "release"]
    since_ref: str  # Git ref we're comparing from

    # Current documentation
    readme: str | None = None
    changelog: str | None = None
    docs_files: dict[str, str] | None = None  # path -> content

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "task": {
                "id": self.task_id,
                "title": self.task_title,
                "description": self.task_description,
                "context": self.task_context,
            },
            "changes": {
                "scope": self.scope,
                "since": self.since_ref,
                "commits": [
                    {
                        "hash": c.hash,
                        "author": c.author,
                        "date": c.date.isoformat(),
                        "subject": c.subject,
                        "body": c.body,
                    }
                    for c in self.commits
                ],
                "diff": self.diff,
                "files": self.changed_files,
            },
            "documentation": {
                "readme": self.readme,
                "changelog": self.changelog,
                "docs": self.docs_files or {},
            },
        }


class DocAnalyzer:
    """
    Analyzes code changes and gathers context for documentation updates.

    This class is responsible for:
    1. Gathering task information
    2. Collecting code changes (commits, diffs)
    3. Reading current documentation
    4. Preparing context for AI analysis
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        """
        Initialize DocAnalyzer.

        Args:
            repo_root: Repository root directory (defaults to current directory)
        """
        self.repo_root = repo_root or Path.cwd()

    def gather_context(
        self,
        task_id: str,
        scope: Literal["task", "release"] = "task",
    ) -> DocumentationContext:
        """
        Gather all context for documentation analysis.

        Args:
            task_id: Task ID to analyze
            scope: Analysis scope - "task" (changes since task creation) or
                   "release" (changes since last release)

        Returns:
            Complete documentation context

        Raises:
            ValueError: If task doesn't exist or scope is invalid
        """
        # Get task information
        metadata = get_task_metadata(task_id)
        task_context = get_task_context(task_id)

        # Determine git ref to compare from
        if scope == "task":
            # Get commits since task creation
            task_created_at = get_task_creation_time(task_id)
            commits = get_task_commits(task_id)
            since_ref = f"created at {task_created_at.isoformat()}"

        elif scope == "release":
            # Get commits since last release tag
            try:
                last_tag = get_last_release_tag()
                commits = get_commits_since(last_tag)
                since_ref = last_tag
            except Exception:
                # No release tags, use all commits
                commits = get_commits_since("HEAD~10")  # Last 10 commits
                since_ref = "HEAD~10"
        else:
            msg = f"Invalid scope: {scope}. Must be 'task' or 'release'"
            raise ValueError(msg)

        # Get diff and changed files
        if scope == "task":
            # For task scope, we need to find the first commit of the task
            if commits:
                # Diff from parent of first commit to HEAD
                first_commit_hash = commits[-1].hash
                diff = get_diff_since(f"{first_commit_hash}~1")
                changed_files = get_changed_files(f"{first_commit_hash}~1")
            else:
                diff = ""
                changed_files = []
        else:
            # For release scope, diff from last tag
            diff = get_diff_since(since_ref)
            changed_files = get_changed_files(since_ref)

        # Read current documentation
        readme = self._read_file(self.repo_root / "README.md")
        changelog = self._read_file(self.repo_root / "CHANGELOG.md")

        # Read docs directory
        docs_files = self._read_docs_directory()

        return DocumentationContext(
            task_id=task_id,
            task_title=metadata.title,
            task_description=metadata.description or "",
            task_context=task_context,
            commits=commits,
            diff=diff,
            changed_files=changed_files,
            scope=scope,
            since_ref=since_ref,
            readme=readme,
            changelog=changelog,
            docs_files=docs_files,
        )

    def _read_file(self, path: Path) -> str | None:
        """
        Read a file if it exists.

        Args:
            path: File path

        Returns:
            File content or None if file doesn't exist
        """
        try:
            return path.read_text()
        except (FileNotFoundError, OSError):
            return None

    def _read_docs_directory(self) -> dict[str, str]:
        """
        Read all markdown files from docs directory.

        Returns:
            Dictionary mapping relative path to content
        """
        docs_dir = self.repo_root / "docs"
        if not docs_dir.exists():
            return {}

        docs_files = {}
        for md_file in docs_dir.rglob("*.md"):
            try:
                relative_path = md_file.relative_to(self.repo_root)
                content = md_file.read_text()
                docs_files[str(relative_path)] = content
            except (OSError, ValueError):
                # Skip files that can't be read
                continue

        return docs_files

    def identify_documentation_gaps(
        self, context: DocumentationContext
    ) -> list[str]:
        """
        Identify potential documentation gaps based on code changes.

        This is a simple heuristic-based analysis. The MCP server will do
        more sophisticated AI-powered analysis.

        Args:
            context: Documentation context

        Returns:
            List of gap descriptions
        """
        gaps = []

        # Check if new files were added
        new_files = [f for f in context.changed_files if not f.startswith("tests/")]
        if new_files:
            gaps.append(f"New files added: {len(new_files)} files. May need documentation.")

        # Check if CLI commands were modified
        cli_files = [f for f in context.changed_files if "commands" in f and f.endswith(".py")]
        if cli_files:
            gaps.append(
                f"CLI commands modified: {len(cli_files)} files. CLI reference may need update."
            )

        # Check if README exists
        if not context.readme:
            gaps.append("README.md not found. Consider creating one.")

        # Check if CHANGELOG exists
        if not context.changelog:
            gaps.append("CHANGELOG.md not found. Consider creating one.")

        # Check if there are commits but no changelog update
        if context.changelog and context.commits:
            # Simple check: does changelog mention any of the commit subjects?
            recent_subjects = [c.subject.lower() for c in context.commits[:5]]
            changelog_lower = context.changelog.lower()

            mentioned = sum(1 for subject in recent_subjects if subject in changelog_lower)
            if mentioned == 0:
                gaps.append(
                    f"CHANGELOG.md may be missing entries for {len(context.commits)} recent commits."
                )

        return gaps
