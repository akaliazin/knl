"""Tests for task models."""

import pytest

from knl.models.task import Task, TaskIDType, TaskMetadata, TaskStatus


class TestTaskIDDetection:
    """Test task ID detection and normalization."""

    def test_detect_jira_id(self) -> None:
        """Test JIRA ID detection."""
        assert Task.detect_id_type("PROJ-123") == TaskIDType.JIRA
        assert Task.detect_id_type("ABC-456") == TaskIDType.JIRA
        assert Task.detect_id_type("X1-999") == TaskIDType.JIRA

    def test_detect_github_id(self) -> None:
        """Test GitHub ID detection."""
        assert Task.detect_id_type("#123") == TaskIDType.GITHUB
        assert Task.detect_id_type("#999") == TaskIDType.GITHUB

    def test_normalize_jira_id(self) -> None:
        """Test JIRA ID normalization (no change)."""
        assert Task.normalize_id("PROJ-123") == "PROJ-123"
        assert Task.normalize_id("ABC-456") == "ABC-456"

    def test_normalize_github_id(self) -> None:
        """Test GitHub ID normalization."""
        assert Task.normalize_id("#123") == "gh-123"
        assert Task.normalize_id("#456") == "gh-456"


class TestTaskMetadata:
    """Test task metadata validation."""

    def test_valid_jira_metadata(self) -> None:
        """Test creating metadata with valid JIRA ID."""
        metadata = TaskMetadata(
            task_id="PROJ-123",
            task_id_type=TaskIDType.JIRA,
            normalized_id="PROJ-123",
        )
        assert metadata.task_id == "PROJ-123"
        assert metadata.status == TaskStatus.TODO

    def test_valid_github_metadata(self) -> None:
        """Test creating metadata with valid GitHub ID."""
        metadata = TaskMetadata(
            task_id="#456",
            task_id_type=TaskIDType.GITHUB,
            normalized_id="gh-456",
        )
        assert metadata.task_id == "#456"
        assert metadata.normalized_id == "gh-456"

    def test_invalid_task_id(self) -> None:
        """Test that invalid task IDs raise ValueError."""
        with pytest.raises(ValueError, match="Invalid task ID format"):
            TaskMetadata(
                task_id="invalid",
                task_id_type=TaskIDType.JIRA,
                normalized_id="invalid",
            )
