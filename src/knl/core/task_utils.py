"""Task integration utilities for documentation automation."""

import json
from datetime import datetime
from pathlib import Path

from ..core.paths import KnlPaths
from ..models.task import Task, TaskMetadata
from ..utils import dt
from ..utils.git import Commit


def get_task_creation_time(task_id: str, repo_root: Path | None = None) -> datetime | None:
    """
    Get the creation time of a task.

    Args:
        task_id: Task identifier (will be normalized)
        repo_root: Repository root (auto-detected if None)

    Returns:
        Task creation datetime or None if task doesn't exist
    """
    if repo_root is None:
        repo_root = KnlPaths.find_repo_root()
        if not repo_root:
            return None

    normalized_id = Task.normalize_id(task_id)
    task_dir = KnlPaths.get_task_dir(normalized_id, repo_root)
    metadata_file = task_dir / "metadata.json"

    if not metadata_file.exists():
        return None

    try:
        with open(metadata_file) as f:
            data = json.load(f)
            created_str = data.get("created_at")
            if created_str:
                return dt.parse(created_str)
    except (json.JSONDecodeError, ValueError, KeyError):
        pass

    return None


def get_task_context(task_id: str, repo_root: Path | None = None) -> str | None:
    """
    Read task context markdown content.

    Args:
        task_id: Task identifier (will be normalized)
        repo_root: Repository root (auto-detected if None)

    Returns:
        Context markdown content or None if doesn't exist
    """
    if repo_root is None:
        repo_root = KnlPaths.find_repo_root()
        if not repo_root:
            return None

    normalized_id = Task.normalize_id(task_id)
    task_dir = KnlPaths.get_task_dir(normalized_id, repo_root)
    context_file = task_dir / "context.md"

    if not context_file.exists():
        return None

    try:
        return context_file.read_text()
    except (OSError, UnicodeDecodeError):
        return None


def get_task_metadata(task_id: str, repo_root: Path | None = None) -> TaskMetadata | None:
    """
    Load task metadata from metadata.json.

    Args:
        task_id: Task identifier (will be normalized)
        repo_root: Repository root (auto-detected if None)

    Returns:
        TaskMetadata object or None if doesn't exist
    """
    if repo_root is None:
        repo_root = KnlPaths.find_repo_root()
        if not repo_root:
            return None

    normalized_id = Task.normalize_id(task_id)
    task_dir = KnlPaths.get_task_dir(normalized_id, repo_root)
    metadata_file = task_dir / "metadata.json"

    if not metadata_file.exists():
        return None

    try:
        with open(metadata_file) as f:
            data = json.load(f)
            return TaskMetadata.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        return None


def get_task_commits(
    task_id: str, repo_root: Path | None = None, paths: list[str] | None = None
) -> list[Commit]:
    """
    Get commits made since task was created.

    Args:
        task_id: Task identifier
        repo_root: Repository root (auto-detected if None)
        paths: Optional list of file paths to filter commits

    Returns:
        List of commits since task creation (empty if task doesn't exist)
    """
    import subprocess

    creation_time = get_task_creation_time(task_id, repo_root)
    if not creation_time:
        return []

    # Get all commits and filter by date
    # Using git log with --all to get all commits
    log_format = "%H|%h|%an|%ae|%aI|%s|%b"
    cmd = ["git", "log", "--all", f"--format={log_format}"]
    if paths:
        cmd.extend(["--"] + paths)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        commit_blocks = result.stdout.strip().split("\n\n")

        for block in commit_blocks:
            if not block.strip():
                continue

            lines = block.split("\n")
            if not lines:
                continue

            parts = lines[0].split("|", 6)
            if len(parts) < 6:
                continue

            hash_val, short_hash, author, email, date_str, subject = parts[:6]
            body = parts[6] if len(parts) > 6 else ""

            if len(lines) > 1:
                body = "\n".join(lines[1:])

            try:
                commit_date = dt.parse(date_str)
            except ValueError:
                continue

            # Only include commits after task creation
            if commit_date >= creation_time:
                commits.append(
                    Commit(
                        hash=hash_val.strip(),
                        short_hash=short_hash.strip(),
                        author=author.strip(),
                        email=email.strip(),
                        date=commit_date,
                        subject=subject.strip(),
                        body=body.strip(),
                    )
                )

        # Sort by date (newest first)
        commits.sort(key=lambda c: c.date, reverse=True)
        return commits

    except subprocess.CalledProcessError:
        return []


def get_task_dir(task_id: str, repo_root: Path | None = None) -> Path | None:
    """
    Get the directory path for a task.

    Args:
        task_id: Task identifier (will be normalized)
        repo_root: Repository root (auto-detected if None)

    Returns:
        Path to task directory or None if repo not found
    """
    if repo_root is None:
        repo_root = KnlPaths.find_repo_root()
        if not repo_root:
            return None

    normalized_id = Task.normalize_id(task_id)
    return KnlPaths.get_task_dir(normalized_id, repo_root)


def task_exists(task_id: str, repo_root: Path | None = None) -> bool:
    """
    Check if a task exists.

    Args:
        task_id: Task identifier
        repo_root: Repository root (auto-detected if None)

    Returns:
        True if task exists, False otherwise
    """
    task_dir = get_task_dir(task_id, repo_root)
    if not task_dir:
        return False

    metadata_file = task_dir / "metadata.json"
    return metadata_file.exists()
