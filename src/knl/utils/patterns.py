"""Pattern matching utilities for KNL."""

import re
from re import Pattern

# Task ID patterns
JIRA_PATTERN: Pattern[str] = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
GITHUB_PATTERN: Pattern[str] = re.compile(r"^#\d+$")

# Branch name patterns for auto-detection
BRANCH_JIRA_PATTERN: Pattern[str] = re.compile(r"([A-Z][A-Z0-9]+-\d+)")
BRANCH_GITHUB_PATTERN: Pattern[str] = re.compile(r"(?:^|/)(\d+)(?:-|$)")


def is_jira_id(task_id: str) -> bool:
    """Check if task ID matches JIRA format."""
    return bool(JIRA_PATTERN.match(task_id))


def is_github_id(task_id: str) -> bool:
    """Check if task ID matches GitHub format."""
    return bool(GITHUB_PATTERN.match(task_id))


def extract_task_id_from_branch(branch_name: str, id_format: str = "auto") -> str | None:
    """
    Extract task ID from branch name.

    Args:
        branch_name: Git branch name
        id_format: Expected format ('jira', 'github', or 'auto')

    Returns:
        Extracted task ID or None
    """
    if id_format == "jira" or id_format == "auto":
        match = BRANCH_JIRA_PATTERN.search(branch_name)
        if match:
            return match.group(1)

    if id_format == "github" or id_format == "auto":
        match = BRANCH_GITHUB_PATTERN.search(branch_name)
        if match:
            return f"#{match.group(1)}"

    return None
