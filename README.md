# KNL - Knowledge Retention Library

A modern, AI-powered task management and development assistant that helps you retain context, maintain quality, and ensure consistency across your development work.

📚 **[Full Documentation](https://akaliazin.github.io/knl/)** | 🚀 **[Quick Start](https://akaliazin.github.io/knl/quickstart/)** | 🏗️ **[Architecture](https://akaliazin.github.io/knl/architecture/principles/)**

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

### Knowledge Crumbs
- Curated development knowledge deployed with KNL
- Bite-sized, reusable guides for common tasks
- Categories: DevOps, Testing, Security, Development
- LLM-friendly format with YAML metadata
- Browse crumbs in `.knl/know-how/crumbs/` or `~/.local/knl/know-how/crumbs/`

## Requirements

### Source Installation (Default)
- **Python 3.8+** for installer (uses only stdlib)
- **Python 3.14+** for KNL itself (uses modern Python features)
  - Version requirement specified in `pyproject.toml` (`requires-python`)
  - Installer automatically detects and validates the required version
- **UV** (Python package manager - installer can install it for you)
- Git repository (optional, but recommended)

### Compiled Binary Installation (Portable)
- **Python 3.8+** to run the compiled binary (no UV needed)
- Git repository (optional, but recommended)

## Quick Start

### Installation

KNL supports multiple installation modes and formats:

#### Repo-Local Installation (Default)

When running the installer inside a git repository, KNL installs to `.knl/` in the current directory. This keeps KNL isolated per project.

```bash
cd your-repo
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh
```

**Benefits:**
- Each repository has its own isolated KNL installation
- No PATH pollution
- Easy to version-control KNL version per project
- Minimal impact on repository (only `.knl/` and `.knowledge/` folders)

**After installation:**
```bash
# Add to PATH for this session
export PATH="$(pwd)/.knl/bin:$PATH"

# Or add to your shell config for persistence
echo 'export PATH="$(pwd)/.knl/bin:$PATH"' >> ~/.bashrc
```

#### User-Local Installation

For system-wide installation, use the `--user-local` flag or run outside a git repository:

```bash
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --user-local
```

This installs KNL to `~/.local/knl/` and automatically adds it to your PATH.

**Benefits:**
- Available globally across all projects
- Only need to install once
- Automatically added to PATH

#### Compiled Binary Installation (Portable)

For maximum portability with minimal dependencies:

```bash
# Install latest compiled binary (requires only Python 3.8+)
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled

# Install specific version
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled --version v1.2.0

# Install from local binary (for offline or airgapped environments)
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled --binary-path /path/to/knl.pyz
```

**Benefits of compiled binary:**
- No virtual environment needed
- No UV dependency manager required
- Requires only Python 3.8+ (vs 3.14+ for source)
- Single ~52MB self-contained file
- Perfect for distribution and CI/CD environments

#### Version Management

Install specific versions or refs:

```bash
# Install specific version (source)
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --version v1.2.0

# Install from branch or tag
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --ref develop

# Install from custom repo
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --repo yourname/knl

# Combine with compiled mode
curl -LsSf https://akaliazin.github.io/knl/install.sh | sh -s -- --compiled --version v1.2.0 --user-local
```

#### What the Installer Does

The installer is smart and will:

**For Source Installation (default):**
1. **Find Python 3.8+** to run the installer itself (uses only stdlib)
2. **Find Python 3.14+** for KNL from PATH and common locations:
   - User installations (`~/.local`, `~/bin`)
   - pyenv installations (`~/.pyenv/versions/`)
   - Homebrew (macOS: `/opt/homebrew`, `/usr/local`)
   - Conda/Miniconda environments
   - System installations
3. **Detect git repository** and choose appropriate installation location
4. Install UV if needed
5. Create isolated virtual environment for KNL
6. Install KNL using the detected Python
7. Create wrapper scripts (`knl` and `kdt` alias)
8. **Deploy knowledge crumbs** - reusable development knowledge
9. Update `.gitignore` (repo-local only)
10. Create initial configuration in `~/.cache/knl/` (XDG-compliant)

**For Compiled Binary Installation (`--compiled`):**
1. **Find Python 3.8+** to run the binary (less restrictive)
2. Download or copy compiled binary (self-contained `.pyz` file)
3. Create wrapper scripts (`knl` and `kdt` alias)
4. **Deploy knowledge crumbs** - reusable development knowledge
5. Update `.gitignore` (repo-local only)
6. Create initial configuration

**Note:** No sudo/root privileges required. Everything installs to user directories.

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/akaliazin/knl.git
cd knl

# Option 1: Run the installer (recommended)
./install.sh

# Option 2: Install with UV directly
uv pip install -e .

# Option 3: Build and install compiled binary
make build-binary
./install.sh --compiled --binary-path ./dist/knl.pyz
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

### Browse Knowledge Crumbs

```bash
# List all crumbs
knl crumb list

# List crumbs by category
knl crumb list --category devops

# Filter by tags and difficulty
knl crumb list --tag deployment --difficulty beginner

# Show crumb content
knl crumb show devops/github-pages-setup

# Show crumb metadata
knl crumb info devops/github-pages-setup

# Search crumbs
knl crumb find "github actions"
knl crumb find "deployment" --in title

# List categories
knl crumb categories

# List tags
knl crumb tags --sort count
```

See the [Crumb CLI Reference](https://akaliazin.github.io/knl/cli/crumbs/) for complete documentation.

## Directory Structure

### KNL Installation Locations

#### Repo-Local Installation (Default in Git Repos)

**Source Mode:**
```
your-project/
├── .knl/                    # KNL installation (git-ignored)
│   ├── venv/               # KNL's isolated Python environment
│   ├── bin/                # Wrapper scripts (knl, kdt)
│   ├── know-how/           # Deployed knowledge crumbs
│   │   ├── README.md
│   │   └── crumbs/         # Curated development knowledge
│   │       ├── devops/
│   │       ├── testing/
│   │       └── security/
│   └── .version            # Installed KNL version
├── .knowledge/             # Knowledge base (git-ignored)
│   └── [see below]
└── .gitignore             # Updated to ignore .knl/ and .knowledge/
```

**Compiled Binary Mode:**
```
your-project/
├── .knl/                    # KNL installation (git-ignored)
│   ├── knl.pyz             # Self-contained executable (~52MB)
│   ├── bin/                # Wrapper scripts (knl, kdt)
│   ├── know-how/           # Deployed knowledge crumbs
│   └── .version            # Installed KNL version
├── .knowledge/             # Knowledge base (git-ignored)
└── .gitignore             # Updated to ignore .knl/ and .knowledge/
```

#### User-Local Installation

**Source Mode:**
```
~/.local/knl/               # KNL installation (system-wide)
├── venv/                   # KNL's isolated Python environment
├── bin/                    # Wrapper scripts (knl, kdt)
├── know-how/               # Deployed knowledge crumbs
└── .version                # Installed KNL version
```

**Compiled Binary Mode:**
```
~/.local/knl/               # KNL installation (system-wide)
├── knl.pyz                 # Self-contained executable
├── bin/                    # Wrapper scripts (knl, kdt)
├── know-how/               # Deployed knowledge crumbs
└── .version                # Installed KNL version
```

### Global Configuration (XDG-Compliant)
```
~/.cache/knl/               # or $XDG_CACHE_HOME/knl/
├── config.toml             # Global settings
├── templates/              # Default templates
└── cache/                  # Global cache
```

### Knowledge Base Structure
```
.knowledge/                 # Repository knowledge base (git-ignored)
├── config.toml            # Local settings (override global)
├── cache/                 # Local cache
├── tasks/                 # Task storage
│   ├── PROJ-123/
│   │   ├── metadata.json  # Task metadata
│   │   ├── context.md     # Development context
│   │   ├── tests/         # Task-specific tests
│   │   └── artifacts/     # Generated artifacts
│   └── gh-456/            # GitHub #456 (normalized from #456)
├── scripts/               # Repo-specific scripts
├── templates/             # Repo-specific templates
└── standards/             # Development standards
    └── development.md
```

### Context Separation

KNL maintains strict isolation between its own execution context and your repository:

**KNL's Context** (`.knl/` or `~/.local/knl/`):
- KNL's virtual environment
- KNL's Python packages
- Completely isolated from your repository

**Your Repository's Context**:
- Your code and dependencies
- Your virtual environment (if any)
- Completely isolated from KNL

**Benefits:**
- KNL never pollutes your project dependencies
- KNL can work on projects with incompatible Python versions
- No PYTHONPATH, PATH, or environment variable leaking

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
git clone https://github.com/akaliazin/knl.git
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

- Issues: https://github.com/akaliazin/knl/issues
- Discussions: https://github.com/akaliazin/knl/discussions

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by [UV](https://github.com/astral-sh/uv) for fast Python package management
- AI integration via [Claude](https://www.anthropic.com/claude) and MCP
