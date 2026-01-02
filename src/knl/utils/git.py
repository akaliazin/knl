"""Git integration utilities."""

import subprocess
from dataclasses import dataclass
from datetime import datetime
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


@dataclass
class Commit:
    """Represents a git commit."""

    hash: str
    short_hash: str
    author: str
    email: str
    date: datetime
    subject: str
    body: str

    @property
    def message(self) -> str:
        """Full commit message (subject + body)."""
        if self.body:
            return f"{self.subject}\n\n{self.body}"
        return self.subject


def get_commits_since(ref: str, paths: Optional[list[str]] = None) -> list[Commit]:
    """
    Get commits since a git ref.

    Args:
        ref: Git reference (tag, branch, commit hash)
        paths: Optional list of file paths to filter commits

    Returns:
        List of commits since the ref

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    # Format: hash|short_hash|author|email|date|subject|body
    log_format = "%H|%h|%an|%ae|%aI|%s|%b"

    cmd = ["git", "log", f"{ref}..HEAD", f"--format={log_format}"]
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
        # Split by commit separator (empty line between body and next commit)
        commit_blocks = result.stdout.strip().split("\n\n")

        for block in commit_blocks:
            if not block.strip():
                continue

            lines = block.split("\n")
            if not lines:
                continue

            # First line has the formatted commit info
            parts = lines[0].split("|", 6)
            if len(parts) < 6:
                continue

            hash_val, short_hash, author, email, date_str, subject = parts[:6]
            body = parts[6] if len(parts) > 6 else ""

            # If there are more lines, they're part of the body
            if len(lines) > 1:
                body = "\n".join(lines[1:])

            try:
                date = datetime.fromisoformat(date_str)
            except ValueError:
                # Skip commits with invalid dates
                continue

            commits.append(
                Commit(
                    hash=hash_val.strip(),
                    short_hash=short_hash.strip(),
                    author=author.strip(),
                    email=email.strip(),
                    date=date,
                    subject=subject.strip(),
                    body=body.strip(),
                )
            )

        return commits

    except subprocess.CalledProcessError as e:
        # Check if ref doesn't exist
        if "unknown revision" in e.stderr.lower() or "bad revision" in e.stderr.lower():
            return []
        raise


def get_diff_since(ref: str, paths: Optional[list[str]] = None) -> str:
    """
    Get unified diff since a git ref.

    Args:
        ref: Git reference (tag, branch, commit hash)
        paths: Optional list of file paths to filter diff

    Returns:
        Unified diff as string

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    cmd = ["git", "diff", f"{ref}..HEAD"]
    if paths:
        cmd.extend(["--"] + paths)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Check if ref doesn't exist
        if "unknown revision" in e.stderr.lower() or "bad revision" in e.stderr.lower():
            return ""
        raise


def get_last_release_tag() -> Optional[str]:
    """
    Get the most recent release tag.

    Looks for tags matching semantic versioning pattern (vX.Y.Z or X.Y.Z).

    Returns:
        Most recent tag or None if no tags exist
    """
    try:
        # Get all tags sorted by version
        result = subprocess.run(
            ["git", "tag", "--sort=-version:refname"],
            capture_output=True,
            text=True,
            check=True,
        )

        tags = result.stdout.strip().split("\n")
        if not tags or not tags[0]:
            return None

        # Return the first tag (most recent)
        return tags[0]

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_changed_files(ref: str, paths: Optional[list[str]] = None) -> list[Path]:
    """
    Get list of files changed since a git ref.

    Args:
        ref: Git reference (tag, branch, commit hash)
        paths: Optional list of file paths to filter

    Returns:
        List of changed file paths

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    cmd = ["git", "diff", "--name-only", f"{ref}..HEAD"]
    if paths:
        cmd.extend(["--"] + paths)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        files = [
            Path(line.strip())
            for line in result.stdout.strip().split("\n")
            if line.strip()
        ]
        return files

    except subprocess.CalledProcessError as e:
        # Check if ref doesn't exist
        if "unknown revision" in e.stderr.lower() or "bad revision" in e.stderr.lower():
            return []
        raise
