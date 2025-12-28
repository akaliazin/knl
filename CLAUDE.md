# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KNL (Knowledge Retention Library) is a Python-based CLI tool that provides AI-powered task management and development assistance. It maintains persistent context for development tasks, helps with code quality, testing, documentation, and git workflows.

**Key Concept**: KNL creates a `.knowledge/` directory in each repository to store task context, development standards, templates, and learned patterns. This knowledge base grows with each task and can be exported to other projects.

## Common Commands

### Development

```bash
# Install in development mode
make dev
# or
uv pip install -e ".[dev]"

# Run the CLI
uv run knl --help

# Run tests
make test
# or
pytest tests/ -v

# Run tests with coverage
make test-cov

# Lint code
make lint

# Format code
make format

# Type check
make type-check

# Run all checks
make check-all

# Clean build artifacts
make clean
```

### Using KNL

```bash
# Initialize in a repository
knl init

# Create a task
knl create PROJ-123
knl create "#456"

# List tasks
knl list

# Show task details
knl show PROJ-123

# Update task
knl task update PROJ-123 --status in_progress

# Configuration
knl config list
knl config get task.id_format
knl config set integrations.jira.url "https://company.atlassian.net" --local
```

## Architecture

### Directory Structure

```
src/knl/
├── cli.py              # Main CLI entry point using Typer
├── models/             # Pydantic models
│   ├── config.py       # Global/Local config, integrations
│   └── task.py         # Task, TaskMetadata, TaskStatus
├── core/               # Core business logic
│   ├── config.py       # ConfigManager for loading/saving config
│   └── paths.py        # KnlPaths utility for directory management
├── commands/           # CLI command implementations
│   ├── init.py         # Repository initialization
│   ├── task.py         # Task CRUD operations
│   └── config.py       # Configuration management
└── utils/              # Utility modules
    ├── patterns.py     # Task ID pattern matching
    └── git.py          # Git integration helpers
```

### Key Design Patterns

1. **Configuration Hierarchy**: Global config (`~/.config/knl/config.toml`) can be overridden by local config (`.knowledge/config.toml`). Both use Pydantic Settings.

2. **Task ID Formats**: Supports JIRA (`PROJ-123`) and GitHub (`#456`). GitHub IDs are normalized to `gh-456` for filesystem safety.

3. **Knowledge Base**: Each repository gets a `.knowledge/` directory:
   - `tasks/` - Individual task directories with metadata, context, tests, artifacts
   - `templates/` - Task templates
   - `standards/` - Development standards that evolve with the project
   - `scripts/` - Repo-specific automation
   - `cache/` - Local caching

4. **Typer CLI**: Uses Typer for the CLI framework with Rich for output formatting. Commands can be called directly (`knl create`) or via subcommands (`knl task create`).

5. **MCP Integration (Planned)**: Will expose the knowledge base to Claude Code via Model Context Protocol.

### Adding New Commands

Commands are organized in `src/knl/commands/`. Each command module:
- Creates a Typer app instance
- Registers commands with decorators
- Is added to main CLI in `cli.py`

Example:
```python
# In src/knl/commands/mycommand.py
import typer
app = typer.Typer()

@app.command()
def my_action():
    """Do something."""
    pass

# In src/knl/cli.py
from .commands import mycommand
app.add_typer(mycommand.app, name="mycommand")
```

### Configuration Management

- `GlobalConfig` and `LocalConfig` are Pydantic Settings models
- `ConfigManager` handles loading/saving with TOML (using `tomli`/`tomli-w`)
- Configuration can be edited via CLI or directly in TOML files
- Local config inherits from global but can override values

### Task Lifecycle

1. **Create**: `knl create TASK-ID` creates directory structure, metadata.json, context.md
2. **Work**: Developer updates context.md, adds tests, generates artifacts
3. **Update**: Status changes (todo → in_progress → in_review → done)
4. **Archive**: Old tasks can be archived or deleted

## Python Version

Requires Python 3.14+ to use modern features. Configured in `pyproject.toml`.

## Dependencies

Core dependencies:
- **typer**: CLI framework
- **rich**: Terminal formatting
- **pydantic**: Data validation and settings
- **tomli/tomli-w**: TOML reading/writing
- **anthropic**: AI integration (planned)

Development dependencies:
- **pytest**: Testing
- **ruff**: Linting and formatting
- **mypy**: Type checking
- **hypothesis**: Property-based testing (planned)

## Testing

- Tests in `tests/` directory
- Use pytest
- Follow pattern: `test_<module>.py` with `Test<Feature>` classes
- Aim for >80% coverage
- Run with `make test` or `pytest`

## Code Style

- Follow PEP 8
- Use Ruff for linting and formatting
- Type hints required (enforced by mypy strict mode)
- Line length: 100 characters
- Use `|` for union types, not `Optional` or `Union`

## Important Constraints

1. **Task IDs**: Must match JIRA (`^[A-Z][A-Z0-9]+-\d+$`) or GitHub (`^#\d+$`) patterns
2. **File Safety**: GitHub IDs are normalized (`#123` → `gh-123`) for directory names
3. **.knowledge/ is git-ignored**: By default, to avoid committing task context. Users can opt-in to commit templates/standards.
4. **Config Files are TOML**: Not JSON or YAML
5. **Python 3.14+**: Do not compromise on this requirement

## Future Phases

- **Phase 3**: MCP server for Claude Code integration
- **Phase 4**: AI-powered code analysis
- **Phase 5**: Automated test generation
- **Phase 6**: Git workflow automation (commit messages, PR summaries)
- **Phase 7**: Knowledge export/import between projects

When implementing these phases, maintain the existing architecture and ensure backward compatibility with the `.knowledge/` directory structure.
