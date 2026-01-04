"""Path utilities for KNL."""

import os
from pathlib import Path


class KnlPaths:
    """Central path management for KNL."""

    # Global paths (XDG-compliant)
    # Use $XDG_CONFIG_HOME/knl or ~/.config/knl
    _xdg_config = os.environ.get('XDG_CONFIG_HOME')
    GLOBAL_CONFIG_DIR = Path(_xdg_config) / "knl" if _xdg_config else Path.home() / ".config" / "knl"
    GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.toml"
    GLOBAL_CACHE_DIR = GLOBAL_CONFIG_DIR / "cache"
    GLOBAL_TEMPLATES_DIR = GLOBAL_CONFIG_DIR / "templates"

    # Local paths (relative to repo root)
    LOCAL_KNOWLEDGE_DIR = Path(".knowledge")
    LOCAL_CONFIG_FILE = LOCAL_KNOWLEDGE_DIR / "config.toml"
    LOCAL_CACHE_DIR = LOCAL_KNOWLEDGE_DIR / "cache"
    LOCAL_TASKS_DIR = LOCAL_KNOWLEDGE_DIR / "tasks"
    LOCAL_SCRIPTS_DIR = LOCAL_KNOWLEDGE_DIR / "scripts"
    LOCAL_TEMPLATES_DIR = LOCAL_KNOWLEDGE_DIR / "templates"
    LOCAL_STANDARDS_DIR = LOCAL_KNOWLEDGE_DIR / "standards"

    @classmethod
    def ensure_global_dirs(cls) -> None:
        """Ensure global directories exist."""
        cls.GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cls.GLOBAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.GLOBAL_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def ensure_local_dirs(cls, repo_root: Path | None = None) -> None:
        """
        Ensure local knowledge directories exist.

        Args:
            repo_root: Repository root path (defaults to current directory)
        """
        root = repo_root or Path.cwd()
        knowledge_dir = root / cls.LOCAL_KNOWLEDGE_DIR

        knowledge_dir.mkdir(parents=True, exist_ok=True)
        (knowledge_dir / "cache").mkdir(exist_ok=True)
        (knowledge_dir / "tasks").mkdir(exist_ok=True)
        (knowledge_dir / "scripts").mkdir(exist_ok=True)
        (knowledge_dir / "templates").mkdir(exist_ok=True)
        (knowledge_dir / "standards").mkdir(exist_ok=True)

    @classmethod
    def find_repo_root(cls, start_path: Path | None = None) -> Path | None:
        """
        Find repository root by looking for .knowledge directory.

        Args:
            start_path: Starting path for search (defaults to current directory)

        Returns:
            Path to repository root or None if not found
        """
        current = start_path or Path.cwd()

        # Traverse up to find .knowledge directory
        for parent in [current, *current.parents]:
            knowledge_dir = parent / cls.LOCAL_KNOWLEDGE_DIR
            if knowledge_dir.exists() and knowledge_dir.is_dir():
                return parent

        return None

    @classmethod
    def is_knl_repo(cls, path: Path | None = None) -> bool:
        """
        Check if path is in a KNL-initialized repository.

        Args:
            path: Path to check (defaults to current directory)

        Returns:
            True if in KNL repository
        """
        return cls.find_repo_root(path) is not None

    @classmethod
    def get_task_dir(cls, task_id: str, repo_root: Path | None = None) -> Path:
        """
        Get task directory path.

        Args:
            task_id: Normalized task ID
            repo_root: Repository root (defaults to current repo)

        Returns:
            Path to task directory
        """
        root = repo_root or cls.find_repo_root() or Path.cwd()
        return root / cls.LOCAL_TASKS_DIR / task_id
