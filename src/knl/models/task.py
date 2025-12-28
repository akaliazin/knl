"""Task models for KNL."""

import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Task status."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class TaskIDType(str, Enum):
    """Task ID type."""

    JIRA = "jira"
    GITHUB = "github"
    CUSTOM = "custom"


class TaskMetadata(BaseModel):
    """Task metadata stored in metadata.json."""

    # Identity
    task_id: str = Field(..., description="Task identifier (e.g., PROJ-123 or #456)")
    task_id_type: TaskIDType = Field(..., description="Type of task ID")
    normalized_id: str = Field(
        ..., description="Normalized ID for filesystem (e.g., gh-456)"
    )

    # Details
    title: str = Field(default="", description="Task title")
    description: str = Field(default="", description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Current status")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # External links
    external_url: Optional[str] = None
    branch_name: Optional[str] = None

    # Tags and labels
    tags: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)

    # AI context
    context_summary: str = Field(
        default="", description="AI-generated summary of task context"
    )

    # Custom fields
    custom_fields: dict[str, Any] = Field(default_factory=dict)

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate task ID format."""
        # JIRA pattern: PROJ-123
        jira_pattern = r"^[A-Z][A-Z0-9]+-\d+$"
        # GitHub pattern: #123
        github_pattern = r"^#\d+$"

        if not (re.match(jira_pattern, v) or re.match(github_pattern, v)):
            raise ValueError(
                f"Invalid task ID format: {v}. "
                "Expected JIRA format (PROJ-123) or GitHub format (#123)"
            )
        return v


class Task(BaseModel):
    """Complete task representation."""

    metadata: TaskMetadata
    task_dir: Path

    @property
    def context_file(self) -> Path:
        """Path to task context markdown file."""
        return self.task_dir / "context.md"

    @property
    def tests_dir(self) -> Path:
        """Path to task tests directory."""
        return self.task_dir / "tests"

    @property
    def artifacts_dir(self) -> Path:
        """Path to task artifacts directory."""
        return self.task_dir / "artifacts"

    @property
    def metadata_file(self) -> Path:
        """Path to task metadata JSON file."""
        return self.task_dir / "metadata.json"

    def create_structure(self) -> None:
        """Create task directory structure."""
        self.task_dir.mkdir(parents=True, exist_ok=True)
        self.tests_dir.mkdir(exist_ok=True)
        self.artifacts_dir.mkdir(exist_ok=True)

    @classmethod
    def normalize_id(cls, task_id: str) -> str:
        """
        Normalize task ID for filesystem safety.

        Args:
            task_id: Original task ID (e.g., PROJ-123 or #456)

        Returns:
            Normalized ID safe for filesystem (e.g., PROJ-123 or gh-456)
        """
        if task_id.startswith("#"):
            # GitHub: #456 -> gh-456
            return f"gh-{task_id[1:]}"
        # JIRA: already filesystem safe
        return task_id

    @classmethod
    def detect_id_type(cls, task_id: str) -> TaskIDType:
        """
        Detect task ID type from format.

        Args:
            task_id: Task identifier

        Returns:
            TaskIDType enum value
        """
        if task_id.startswith("#"):
            return TaskIDType.GITHUB
        if re.match(r"^[A-Z][A-Z0-9]+-\d+$", task_id):
            return TaskIDType.JIRA
        return TaskIDType.CUSTOM
