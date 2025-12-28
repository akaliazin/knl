"""Git integration utilities."""

import subprocess
from pathlib import Path
from typing import Optional


def get_current_branch() -> Optional[str]:
    """
    Get current git branch name.

    Returns:
        Branch name or None if not in a git repo
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_repo_root() -> Optional[Path]:
    """
    Get git repository root directory.

    Returns:
        Path to repo root or None
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_git_repo() -> bool:
    """Check if current directory is in a git repository."""
    return get_repo_root() is not None


def get_remote_url(remote: str = "origin") -> Optional[str]:
    """
    Get git remote URL.

    Args:
        remote: Remote name (default: origin)

    Returns:
        Remote URL or None
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def extract_github_repo_from_url(url: str) -> Optional[str]:
    """
    Extract GitHub repo (owner/repo) from git URL.

    Args:
        url: Git remote URL

    Returns:
        Repository in format 'owner/repo' or None
    """
    import re

    # Match GitHub URLs (both HTTPS and SSH)
    patterns = [
        r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner, repo = match.groups()
            return f"{owner}/{repo}"

    return None
