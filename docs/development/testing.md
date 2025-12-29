# Testing Guide

*This page is under construction.*

Guide for writing and running tests in KNL.

## Running Tests

### Quick Start

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::TestConfigManager::test_load_global_config
```

### Coverage Reports

```bash
# Generate coverage report
make test-cov

# View HTML coverage report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Test Structure

### Directory Organization

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_config.py           # Configuration tests
├── test_task.py             # Task management tests
├── test_paths.py            # Path utilities tests
├── test_patterns.py         # Pattern matching tests
├── test_cli.py              # CLI tests
└── fixtures/                # Test fixtures and data
    ├── sample_config.toml
    └── sample_task/
```

### Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test methods: `test_<behavior>`

Example:
```python
# tests/test_config.py

class TestConfigManager:
    def test_load_global_config(self):
        """Test loading global configuration."""
        pass

    def test_load_local_config(self):
        """Test loading local configuration."""
        pass

    def test_merge_configs(self):
        """Test merging global and local configs."""
        pass
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from knl.core.config import ConfigManager

class TestConfigManager:
    def test_load_config(self, tmp_path):
        """Test loading configuration from file."""
        # Arrange
        config_file = tmp_path / "config.toml"
        config_file.write_text('[task]\nid_format = "jira"')

        # Act
        manager = ConfigManager(config_file)
        config = manager.load()

        # Assert
        assert config.task.id_format == "jira"
```

### Using Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository structure."""
    repo = tmp_path / "test-repo"
    repo.mkdir()
    knowledge = repo / ".knowledge"
    knowledge.mkdir()
    return repo

# tests/test_task.py
def test_create_task(temp_repo):
    """Test task creation."""
    # Use temp_repo fixture
    task_dir = temp_repo / ".knowledge" / "tasks" / "PROJ-123"
    # ... test logic
```

### Testing CLI Commands

```python
from typer.testing import CliRunner
from knl.cli import app

runner = CliRunner()

def test_cli_version():
    """Test CLI version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output

def test_cli_create_task():
    """Test task creation via CLI."""
    result = runner.invoke(app, ["create", "PROJ-123"])
    assert result.exit_code == 0
    assert "Created task PROJ-123" in result.output
```

### Testing Error Handling

```python
import pytest

def test_invalid_task_id():
    """Test handling of invalid task ID."""
    with pytest.raises(ValueError, match="Invalid task ID"):
        create_task("invalid-id")

def test_file_not_found():
    """Test handling of missing file."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("/nonexistent/config.toml"))
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("task_id,expected", [
    ("PROJ-123", "PROJ-123"),
    ("#456", "gh-456"),
    ("ABC-789", "ABC-789"),
])
def test_normalize_task_id(task_id, expected):
    """Test task ID normalization."""
    result = normalize_task_id(task_id)
    assert result == expected
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```python
def test_parse_jira_id():
    """Test JIRA ID parsing."""
    assert parse_jira_id("PROJ-123") == ("PROJ", "123")

def test_parse_github_id():
    """Test GitHub ID parsing."""
    assert parse_github_id("#456") == "456"
```

### Integration Tests

Test multiple components together:

```python
def test_task_lifecycle(temp_repo):
    """Test complete task lifecycle."""
    # Create task
    task = create_task("PROJ-123", temp_repo)
    assert task.exists()

    # Update task
    update_task_status(task, "in_progress")
    assert task.status == "in_progress"

    # Delete task
    delete_task(task)
    assert not task.exists()
```

### End-to-End Tests

Test complete user workflows:

```python
def test_full_workflow(temp_repo):
    """Test full task workflow via CLI."""
    runner = CliRunner()

    # Initialize repo
    result = runner.invoke(app, ["init"], cwd=temp_repo)
    assert result.exit_code == 0

    # Create task
    result = runner.invoke(app, ["create", "PROJ-123"], cwd=temp_repo)
    assert result.exit_code == 0

    # List tasks
    result = runner.invoke(app, ["list"], cwd=temp_repo)
    assert "PROJ-123" in result.output
```

## Best Practices

### Test Independence

Each test should be independent:

```python
# Good - uses fixture for isolation
def test_create_task(temp_repo):
    create_task("PROJ-123", temp_repo)
    assert task_exists("PROJ-123", temp_repo)

# Bad - depends on previous test
def test_update_task():
    # Assumes PROJ-123 exists from previous test
    update_task_status("PROJ-123", "done")
```

### Descriptive Names

Use clear, descriptive test names:

```python
# Good
def test_create_task_with_github_id_normalizes_to_filesystem_safe_name():
    pass

# Acceptable
def test_github_id_normalization():
    pass

# Bad
def test_task1():
    pass
```

### Test Coverage Goals

- Aim for >80% code coverage
- Focus on critical paths
- Test edge cases and error handling
- Don't test framework code

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

@patch('knl.utils.git.subprocess.run')
def test_git_status(mock_run):
    """Test git status command."""
    mock_run.return_value = Mock(
        stdout="On branch main\n",
        returncode=0
    )

    result = get_git_status()
    assert result.branch == "main"
    mock_run.assert_called_once()
```

## Continuous Integration

Tests run automatically on:

- Every push to GitHub
- Every pull request
- Before deployment

GitHub Actions workflow:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      - run: make test-cov
      - uses: codecov/codecov-action@v3
```

## Troubleshooting

### Tests Failing Locally

```bash
# Clear pytest cache
rm -rf .pytest_cache

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reinstall in development mode
uv pip install -e ".[dev]"

# Run tests with verbose output
pytest tests/ -vv
```

### Coverage Issues

```bash
# See which lines aren't covered
pytest tests/ --cov=knl --cov-report=html
open htmlcov/index.html
```

### Slow Tests

```bash
# Show slowest tests
pytest tests/ --durations=10

# Run only fast tests
pytest tests/ -m "not slow"
```

## Next Steps

- [Development Setup](setup.md) - Set up your environment
- [Contributing Guide](contributing.md) - Contribution guidelines
- [Architecture Principles](../architecture/principles.md) - Understand the design
