"""Configuration models for KNL."""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskIDFormat(str, Enum):
    """Supported task ID formats."""

    JIRA = "jira"
    GITHUB = "github"
    CUSTOM = "custom"


class JiraIntegration(BaseModel):
    """JIRA integration configuration."""

    enabled: bool = False
    url: str = ""
    project: str = ""
    username: str = ""
    api_token: str = ""


class GitHubIntegration(BaseModel):
    """GitHub integration configuration."""

    enabled: bool = False
    repo: str = ""  # Format: "owner/repo"
    token: str = ""


class AIIntegration(BaseModel):
    """AI/Claude integration configuration."""

    enabled: bool = True
    provider: str = "claude"  # claude, openai, custom
    api_key: str = ""
    model: str = "claude-sonnet-4-5-20250929"


class TaskConfig(BaseModel):
    """Task-related configuration."""

    id_format: TaskIDFormat = TaskIDFormat.JIRA
    jira_project: str = ""
    github_repo: str = ""
    auto_detect_from_branch: bool = True
    custom_pattern: str | None = None


class DocsConfig(BaseModel):
    """Documentation configuration."""

    mcp_server: str = Field(
        default="knl-docs-analyzer", description="MCP server name for documentation analysis"
    )
    auto_approve: bool = Field(
        default=False, description="Auto-approve documentation updates without user confirmation"
    )
    changelog_template: str = Field(
        default="## [{version}] - {date}\n\n{content}",
        description="Template for CHANGELOG entries",
    )
    cli_ref_dir: Path = Field(default=Path("docs/cli"), description="CLI reference documentation directory")
    coverage_threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Minimum documentation coverage required (0.0-1.0)"
    )


class GlobalConfig(BaseSettings):
    """Global configuration stored in ~/.config/knl/config.toml."""

    model_config = SettingsConfigDict(
        env_prefix="KNL_",
        case_sensitive=False,
    )

    # General settings
    editor: str = Field(default="vim", description="Preferred text editor")
    cache_dir: Path = Field(
        default=Path.home() / ".config" / "knl" / "cache",
        description="Global cache directory",
    )

    # Default task configuration
    task: TaskConfig = Field(default_factory=TaskConfig)

    # Documentation configuration
    docs: DocsConfig = Field(default_factory=DocsConfig)

    # Integrations (can be overridden locally)
    integrations_jira: JiraIntegration = Field(
        default_factory=JiraIntegration, alias="integrations.jira"
    )
    integrations_github: GitHubIntegration = Field(
        default_factory=GitHubIntegration, alias="integrations.github"
    )
    integrations_ai: AIIntegration = Field(
        default_factory=AIIntegration, alias="integrations.ai"
    )

    # CLI preferences
    color_output: bool = True
    verbose: bool = False


class LocalConfig(BaseSettings):
    """Local configuration stored in <repo>/.knowledge/config.toml."""

    model_config = SettingsConfigDict(
        env_prefix="KNL_",
        case_sensitive=False,
    )

    # Repository-specific task configuration
    task: TaskConfig = Field(default_factory=TaskConfig)

    # Documentation configuration (override global)
    docs: DocsConfig | None = Field(default=None)

    # Local integrations (override global)
    integrations_jira: JiraIntegration | None = Field(
        default=None, alias="integrations.jira"
    )
    integrations_github: GitHubIntegration | None = Field(
        default=None, alias="integrations.github"
    )
    integrations_ai: AIIntegration | None = Field(
        default=None, alias="integrations.ai"
    )

    # Local paths
    knowledge_dir: Path = Field(
        default=Path(".knowledge"), description="Knowledge base directory"
    )
    cache_dir: Path = Field(
        default=Path(".knowledge/cache"), description="Local cache directory"
    )

    # Development standards
    standards_file: Path = Field(
        default=Path(".knowledge/standards/development.md"),
        description="Development standards document",
    )
