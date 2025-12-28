"""Configuration management for KNL."""

import tomli
import tomli_w
from pathlib import Path
from typing import Any, Optional

from ..models.config import GlobalConfig, LocalConfig
from .paths import KnlPaths


class ConfigManager:
    """Manage global and local configuration."""

    @staticmethod
    def load_global_config() -> GlobalConfig:
        """
        Load global configuration.

        Returns:
            GlobalConfig instance
        """
        if not KnlPaths.GLOBAL_CONFIG_FILE.exists():
            # Create default config
            config = GlobalConfig()
            ConfigManager.save_global_config(config)
            return config

        with open(KnlPaths.GLOBAL_CONFIG_FILE, "rb") as f:
            data = tomli.load(f)

        return GlobalConfig(**data)

    @staticmethod
    def save_global_config(config: GlobalConfig) -> None:
        """
        Save global configuration.

        Args:
            config: GlobalConfig to save
        """
        KnlPaths.ensure_global_dirs()

        data = config.model_dump(mode="json", exclude_none=True)

        with open(KnlPaths.GLOBAL_CONFIG_FILE, "wb") as f:
            tomli_w.dump(data, f)

    @staticmethod
    def load_local_config(repo_root: Optional[Path] = None) -> Optional[LocalConfig]:
        """
        Load local repository configuration.

        Args:
            repo_root: Repository root path

        Returns:
            LocalConfig instance or None if not found
        """
        root = repo_root or KnlPaths.find_repo_root()
        if not root:
            return None

        config_file = root / KnlPaths.LOCAL_CONFIG_FILE
        if not config_file.exists():
            return None

        with open(config_file, "rb") as f:
            data = tomli.load(f)

        return LocalConfig(**data)

    @staticmethod
    def save_local_config(config: LocalConfig, repo_root: Optional[Path] = None) -> None:
        """
        Save local repository configuration.

        Args:
            config: LocalConfig to save
            repo_root: Repository root path
        """
        root = repo_root or KnlPaths.find_repo_root() or Path.cwd()
        KnlPaths.ensure_local_dirs(root)

        config_file = root / KnlPaths.LOCAL_CONFIG_FILE
        data = config.model_dump(mode="json", exclude_none=True)

        with open(config_file, "wb") as f:
            tomli_w.dump(data, f)

    @staticmethod
    def get_config_value(
        key: str, repo_root: Optional[Path] = None
    ) -> Optional[Any]:
        """
        Get configuration value with local override.

        Args:
            key: Configuration key (dot notation, e.g., 'task.id_format')
            repo_root: Repository root path

        Returns:
            Configuration value or None
        """
        # Try local config first
        local_config = ConfigManager.load_local_config(repo_root)
        if local_config:
            parts = key.split(".")
            value = local_config
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    break
            if value is not None:
                return value

        # Fall back to global config
        global_config = ConfigManager.load_global_config()
        parts = key.split(".")
        value = global_config
        for part in parts:
            value = getattr(value, part, None)
            if value is None:
                break

        return value

    @staticmethod
    def set_config_value(
        key: str, value: Any, local: bool = False, repo_root: Optional[Path] = None
    ) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key (dot notation)
            value: Value to set
            local: If True, set in local config; otherwise global
            repo_root: Repository root path (for local config)
        """
        if local:
            config = ConfigManager.load_local_config(repo_root) or LocalConfig()
            # Set nested value
            parts = key.split(".")
            obj = config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
            ConfigManager.save_local_config(config, repo_root)
        else:
            config = ConfigManager.load_global_config()
            parts = key.split(".")
            obj = config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
            ConfigManager.save_global_config(config)
