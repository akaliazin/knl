# KNL - Knowledge Retention Library

A modern, AI-powered task management and development assistant that helps you retain context, maintain quality, and ensure consistency across your development work.

## What is KNL?

KNL (Knowledge Retention Library) is a command-line tool that:

- **Manages development tasks** with persistent context and memory
- **Enhances code quality** using AI-powered analysis (Claude)
- **Maintains development standards** across tasks
- **Generates tests** based on learned patterns
- **Assists with git workflows** (commits, PRs)
- **Transfers knowledge** between projects

Think of it as a development assistant that learns from your work and helps you stay productive.

## Features

### Task Management
- Track tasks linked to JIRA tickets or GitHub issues
- Maintain rich context for each task
- Auto-detect task IDs from branch names
- Organize tests, artifacts, and documentation per task

### AI Integration
- Powered by Claude Code via MCP (Model Context Protocol)
- Code quality analysis
- Test generation based on project patterns
- Consistent documentation
- Smart commit messages and PR summaries

### Knowledge Base
- Local `.knowledge/` directory stores task history
- Learn and apply development standards
- Export knowledge to new projects
- Archive or reset as needed

## Requirements

- **Python 3.14+** (uses modern Python features)
  - Version requirement specified in `pyproject.toml` (`requires-python`)
  - Installer automatically detects and validates the required version
- **UV** (Python package manager)
- Git repository (recommended)

## Quick Start

### Installation

```bash
# One-line installer (recommended)
curl -LsSf https://raw.githubusercontent.com/yourusername/knl/main/install.sh | sh

# Or with wget
wget -qO- https://raw.githubusercontent.com/yourusername/knl/main/install.sh | sh
```

The installer is smart and will:
1. **Auto-detect Python 3.14+** from PATH and common locations:
   - User installations (`~/.local`, `~/bin`)
   - pyenv installations (`~/.pyenv/versions/`)
   - Homebrew (macOS: `/opt/homebrew`, `/usr/local`)
   - Conda/Miniconda environments
   - System installations
2. **Prompt for Python path** if not found automatically
3. **Show installation instructions** for Python 3.14+ (no sudo required):
   - pyenv (recommended for Linux/macOS)
   - Homebrew (macOS)
   - Build from source to ~/.local
   - python.org installers
   - Miniconda
4. Install UV if needed
5. Install KNL using the detected Python
6. Add to your PATH automatically
7. Create initial configuration

**Note:** No system/root privileges required. Everything installs to your home directory.

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/knl.git
cd knl

# Install with UV
uv pip install -e .

# Or use the installer
./install.sh
```

## Usage

### Initialize KNL in Your Repository

```bash
cd your-project
knl init
```

You'll be prompted to choose:
- Task ID format (JIRA or GitHub)
- Project identifier

This creates a `.knowledge/` directory with:
- Configuration
- Templates
- Development standards
- Task storage

### Create a Task

```bash
# JIRA-style
knl create PROJ-123

# GitHub-style
knl create "#456"

# With title
knl create PROJ-123 --title "Add user authentication"

# Auto-fetch from JIRA/GitHub (when configured)
knl create PROJ-123 --fetch
```

### List Tasks

```bash
# All tasks
knl list

# Filter by status
knl list --status todo
knl list --status in_progress

# Include archived
knl list --all
```

### Show Task Details

```bash
knl show PROJ-123
```

### Update Task

```bash
# Update status
knl task update PROJ-123 --status in_progress

# Update title
knl task update PROJ-123 --title "New title"
```

### Delete Task

```bash
knl delete PROJ-123

# Skip confirmation
knl delete PROJ-123 --force
```

### Configuration

```bash
# View all configuration
knl config list

# View local config only
knl config list --local

# Get specific value
knl config get task.id_format

# Set value (global)
knl config set integrations.jira.url "https://company.atlassian.net"

# Set value (local to repo)
knl config set task.jira_project "MYPROJ" --local

# Edit config file
knl config edit
knl config edit --local
```

## Directory Structure

### Global Configuration
```
~/.config/knl/
├── config.toml       # Global settings
├── templates/        # Default templates
└── cache/           # Global cache
```

### Repository Structure
```
your-project/
├── .knowledge/              # KNL knowledge base (git-ignored)
│   ├── config.toml         # Local settings
│   ├── cache/              # Local cache
│   ├── tasks/              # Task storage
│   │   ├── PROJ-123/
│   │   │   ├── metadata.json
│   │   │   ├── context.md
│   │   │   ├── tests/
│   │   │   └── artifacts/
│   │   └── gh-456/         # GitHub #456
│   ├── scripts/            # Repo-specific scripts
│   ├── templates/          # Repo-specific templates
│   └── standards/          # Development standards
│       └── development.md
└── .gitignore              # Updated to ignore .knowledge/
```

## Configuration

### Task ID Formats

**JIRA**: `PROJ-123`, `ABC-456`
- Set project code at init
- Optionally configure JIRA integration for metadata fetching

**GitHub**: `#123`, `#456`
- Set repository at init
- Optionally configure GitHub integration

### Integration Setup

#### JIRA Integration
```toml
[integrations.jira]
enabled = true
url = "https://company.atlassian.net"
project = "PROJ"
username = "your-email@company.com"
api_token = "your-api-token"
```

#### GitHub Integration
```toml
[integrations.github]
enabled = true
repo = "owner/repo"
token = "ghp_your_token"
```

#### AI Integration
```toml
[integrations.ai]
enabled = true
provider = "claude"
model = "claude-sonnet-4-5-20250929"
api_key = ""  # Or use Claude Code
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/knl.git
cd knl

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/knl
```

### Project Structure

```
knl/
├── src/knl/
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── models/             # Pydantic models
│   │   ├── config.py       # Configuration models
│   │   └── task.py         # Task models
│   ├── core/               # Core functionality
│   │   ├── config.py       # Config management
│   │   └── paths.py        # Path utilities
│   ├── commands/           # CLI commands
│   │   ├── init.py
│   │   ├── task.py
│   │   └── config.py
│   └── utils/              # Utilities
│       ├── patterns.py     # Pattern matching
│       └── git.py          # Git integration
├── tests/                  # Test suite
├── install.sh             # Bootstrap installer
└── pyproject.toml         # Project configuration
```

## Roadmap

- [x] Phase 1: Core infrastructure and CLI
- [ ] Phase 2: Task management commands
- [ ] Phase 3: MCP server for Claude Code integration
- [ ] Phase 4: AI-powered code analysis
- [ ] Phase 5: Test generation
- [ ] Phase 6: Git workflow automation
- [ ] Phase 7: Knowledge transfer and export

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Issues: https://github.com/yourusername/knl/issues
- Discussions: https://github.com/yourusername/knl/discussions

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by [UV](https://github.com/astral-sh/uv) for fast Python package management
- AI integration via [Claude](https://www.anthropic.com/claude) and MCP
