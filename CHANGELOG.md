# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-01-05

### Added

#### Crumbs Bundling System
- **Crumbs distributed with KNL package**: Knowledge crumbs now bundled in Python package (`src/knl/bundled_crumbs/`)
- **Automatic extraction during installation**: Installer copies crumbs from installed package to data directory
- **XDG-compliant data directories**:
  - Repo-local: `.knl/share/crumbs/`
  - User-local: `~/.local/share/knl/crumbs/` (or `$XDG_DATA_HOME/knl/crumbs/`)
- **Smart path discovery**: `KnlPaths.get_bundled_crumbs_dir()` with priority search:
  1. Repo-local installation
  2. User-local installation
  3. Development fallback (`<repo>/crumbs/`)
- **Idempotent updates**: Re-installation preserves user modifications, only adds new crumbs
- **Works for all modes**: Source and compiled binaries, repo-local and user-local

#### Documentation Command (Basic Mode)
- **New `knl docs update` command**: Semi-automated documentation synchronization
- **Heuristic analysis**: Detects documentation gaps without AI:
  - New files requiring documentation
  - Modified CLI commands needing reference updates
  - Missing CHANGELOG entries
- **Graceful degradation**: Works without MCP server, shows actionable recommendations
- **Foundation for AI**: Infrastructure ready for AI-powered analysis (Phase 4)

#### New CLI Commands
- **`knl help`**: Equivalent to `--help` for convenience
- **Enhanced `knl version`**: Shows detailed version information:
  - KNL version
  - Python version (current and pinned)
  - Last commit (hash + timestamp): `681ca95 2026-01-05 22:39:29 +0300`
  - Knowledge crumbs count

#### Installer Features
- **`--repo-local` flag**: Explicit repo-local installation (mutually exclusive with `--user-local`)
- **Default behavior preserved**: Repo-local if in git repo, otherwise user-local
- **Python version pinning**: Uses UV's native `uv python pin` for validation
- **Bytecode pre-compilation**: Faster first run with pre-compiled `.pyc` files
- **Intelligent next steps**: Context-aware suggestions based on repository state
- **Better error messages**: Detailed debugging info for crumbs extraction failures

### Changed

#### Configuration Locations (XDG-Compliant)
- **User-local config**: Moved from `~/.cache/knl/` to `~/.config/knl/` (or `$XDG_CONFIG_HOME/knl/`)
- **Repo-local config**: Changed from `.knl/` to `.knl/config/`
- **Crumbs location**: Separated from config into `.knl/share/crumbs/` (repo-local) or `~/.local/share/knl/crumbs/` (user-local)
- **Follows XDG Base Directory Specification**: Proper separation of config and data

#### Crumbs Structure
- **Simplified directory structure**: `know-how/crumbs/` → `crumbs/` at repo root
- **Cleaner navigation**: Direct access without nested directories
- **Bundled in package**: Included in wheel distribution via `pyproject.toml`

#### Installer Improvements
- **Uses venv Python**: Extracts crumbs using installed venv Python (not system Python)
- **Better error handling**: Clear messages for missing packages or extraction failures
- **Version display**: Shows `knl version` output after successful installation
- **Crumbs in output**: Reports crumb count and location in success message

#### Documentation Updates
- **Git pre-commit hook**: Auto-syncs `install.sh` → `docs/install.sh` on commit
- **MkDocs build hook**: Copies `install.sh` to built site during `mkdocs build`
- **Always up-to-date**: GitHub Pages always serves latest installer

### Fixed

- **Critical**: Fixed crumbs extraction to use venv Python instead of system Python
  - Resolves `ModuleNotFoundError: No module named 'knl'` during installation
- **Type hints**: Fixed Pylance errors in `cli_help.py` by using Click types instead of `typer.core`
- **Parameter naming**: Fixed `get_install_location()` to use `force_user_local` parameter consistently
- **Crumb counting**: Excludes README.md from crumb count in `knl version`

### Technical Details

#### New Components
- **`src/knl/bundled_crumbs/`**: Crumbs bundled with package
- **`src/knl/core/paths.py`**: Added `get_bundled_crumbs_dir()` for crumbs discovery
- **`src/knl/commands/docs.py`**: Documentation update command with heuristic analysis
- **`src/knl/integrations/mcp.py`**: MCP client infrastructure (for future AI integration)
- **`hooks/pre-commit`**: Git hook for install.sh synchronization
- **`docs/hooks.py`**: MkDocs hook for installer deployment

#### Installation Modes Tested
- ✅ Repo-local clean install
- ✅ Repo-local re-install (idempotent)
- ✅ User-local clean install
- ✅ User-local re-install (idempotent)
- ✅ Crumbs extracted correctly in all modes
- ✅ `knl crumb list` works in all modes

#### Statistics
- **7 commits** with comprehensive improvements
- **93 tests passing** ✓
- **2 starter crumbs** included (README + GitHub Pages setup guide)

### Impact

This checkpoint release significantly improves the installation experience and establishes a robust foundation for knowledge management. The crumbs bundling system ensures fresh installs immediately have access to curated development knowledge, while XDG-compliance provides a cleaner, more standard directory structure. The documentation command provides basic functionality that will be enhanced with AI in Phase 4.

### Notes

This is a **checkpoint release** focusing on installation improvements and crumbs infrastructure. The `knl docs update` command provides basic heuristic analysis; full AI-powered documentation synchronization will be implemented in the next release (Phase 4).

## [1.2.0] - 2025-12-31

### Added

#### Knowledge Crumbs Command (`knl crumb`)
- **New CLI command** for browsing and managing knowledge crumbs
- **Six core subcommands**:
  - `knl crumb list` - List all crumbs with filtering and sorting
  - `knl crumb show <path>` - Display full crumb content with rich markdown rendering
  - `knl crumb info <path>` - Display crumb metadata
  - `knl crumb find <query>` - Search crumbs by content and metadata
  - `knl crumb categories` - List all categories with counts
  - `knl crumb tags` - List all tags with usage counts
- **Filtering options**: Filter by category, tags, difficulty level
- **Sorting options**: Sort by title, created date, updated date, difficulty, category
- **Output formats**: Table (default), compact, JSON
- **Search capabilities**: Search in specific fields (title, description, tags, content) with case-sensitive option
- **Rich formatting**: Beautiful table output, syntax-highlighted markdown rendering
- **Custom YAML parser**: No external dependencies for frontmatter parsing

#### Compiled Binary Installation
- **New `--compiled` flag** for portable installation mode
- **Minimal dependencies**: Requires only Python 3.8+ (vs 3.14+ for source installation)
- **Self-contained executable**: Single ~52MB `.pyz` file with all dependencies bundled
- **Offline installation**: Support for airgapped environments via `--binary-path` flag
- **Build automation**: New `make build-binary` target using shiv
- **Perfect for**: CI/CD pipelines, distribution, restricted environments

#### Knowledge Crumbs Deployment
- **Automatic deployment** during installation (both source and compiled modes)
- **Curated development knowledge**: Actionable guides for common development tasks
- **Category organization**: DevOps, Testing, Security, Development, Tooling
- **LLM-friendly format**: YAML frontmatter with comprehensive metadata
- **Installation locations**: `.knl/know-how/crumbs/` (repo-local) or `~/.local/knl/know-how/crumbs/` (user-local)
- **First crumb included**: GitHub Pages deployment guide

### Changed

#### Installer Enhancements
- **Enhanced `install.sh`** with new installation modes
- **New functions**:
  - `deploy_crumbs()` - Deploys knowledge crumbs to installation directory
  - `install_compiled_binary()` - Handles compiled binary installation
- **Updated wrapper scripts** to support both source and compiled modes
- **Installation summary** now shows crumb count and location

#### Documentation Updates
- **Comprehensive installation guide** with source vs compiled comparison
- **All docs updated** with crumb command examples
- **Installation tabs** added for different modes (source, compiled, repo-local, user-local)
- **Updated files**: README.md, docs/installation.md, docs/quickstart.md, docs/index.md, docs/development/setup.md

### Technical Details

#### New Components
- **`src/knl/models/crumb.py`**: Pydantic models for Crumb and CrumbMetadata
- **`src/knl/core/crumbs.py`**: CrumbManager for parsing YAML frontmatter and querying crumbs
- **`src/knl/commands/crumb.py`**: CLI interface with Rich formatting (388 lines)
- **Custom YAML parser**: Handles both inline JSON lists and multi-line YAML lists

#### Statistics
- **14 files changed**: 1,339 insertions(+), 93 deletions(-)
- **3 new files created**: Models, core logic, and CLI commands
- **Binary size**: ~52MB self-contained executable

### Impact

This release transforms KNL from a task management tool into a comprehensive knowledge management system. Users can now easily discover and browse curated development knowledge without resorting to raw `ls` and `cat` commands. The compiled binary option makes KNL accessible to a wider range of environments and use cases.

## [1.1.0] - 2025-12-29

### Added

#### Know-How System
- **Crumbs Framework**: New `know-how/crumbs/` directory for capturing carefully collated development knowledge
  - Category-based organization (devops/, development/, testing/, security/, tooling/)
  - YAML frontmatter metadata for LLM-friendly structured data
  - GitHub Flavored Markdown throughout
  - First crumb: `devops/github-pages-setup.md` - Complete guide for GitHub Pages deployment with GitHub Actions

#### Documentation Improvements
- **Separate docs requirements**: Created `docs/requirements.txt` for documentation-only dependencies
  - Allows building docs with Python 3.12 while KNL requires Python 3.14+
  - Separates concerns: docs build doesn't need KNL package installation
- **Improved GitHub Actions workflow**:
  - Fixed Python version compatibility (3.12 for docs build)
  - Added cache-dependency-path for proper pip caching
  - Workflow now successfully builds and deploys to GitHub Pages

### Changed
- Replaced `templates/` directory with `know-how/crumbs/` for better clarity
  - "Templates" was misleading - these are knowledge articles, not code templates
  - "Crumbs" better represents bite-sized, reusable knowledge pieces

### Fixed
- Documentation deployment to GitHub Pages now works correctly
- GitHub Actions workflow permissions properly configured for Pages deployment

## [1.0.0] - 2025-12-29

### Added

#### Core Features
- **Task Management**: JIRA-style (`PROJ-123`) and GitHub-style (`#456`) task tracking
- **Knowledge Base**: Local `.knowledge/` directory for persistent task context
- **Configuration System**: Hierarchical TOML-based configuration (global + local)
- **CLI Commands**: `init`, `create`, `list`, `show`, `update`, `delete`, `config`
- **Task Context**: Markdown-based context files for each task
- **Task Metadata**: JSON metadata tracking status, timestamps, tags, and links

#### Installation & Deployment
- **Dual Installation Modes**:
  - Repo-local (`.knl/` in repository)
  - User-local (`~/.local/knl/`)
- **Heredoc-Based Installer**: Python 3.8+ installer using only stdlib
- **Python Version Detection**: Auto-detects Python 3.14+ from multiple sources
- **UV Integration**: Automatic UV installation if needed
- **Context Isolation**: Strict separation between KNL and target repository environments
- **XDG Compliance**: Configuration in `~/.cache/knl/` or `$XDG_CACHE_HOME/knl/`

#### Documentation
- **MkDocs Site**: Comprehensive documentation with Material theme
- **GitHub Pages**: Auto-deployment via GitHub Actions
- **Clean URLs**: Installer available at `https://akaliazin.github.io/knl/install.sh`
- **Guides**: Installation, Quick Start, Configuration, Task Management, Architecture
- **API Reference**: Complete CLI command documentation

#### Architecture
- **Python Version Pinning**: `.python-version` files for stability
- **CLAUDE.md Management**: Language-aware documentation generation
- **Language Detection**: Automatic detection of Python, Java/Groovy, Node.js, Go, Rust, Ruby
- **Template System**: Language-specific CLAUDE.md templates
- **Minimal Repository Impact**: Only `.knl/`, `.knowledge/`, and `.gitignore` modifications

#### Development
- **Typer CLI Framework**: Modern, type-safe CLI with Rich output
- **Pydantic Models**: Type-safe configuration and task models
- **Comprehensive Testing**: pytest-based test suite
- **Code Quality Tools**: ruff, mypy, pytest with coverage
- **Makefile**: Common development tasks (`make test`, `make lint`, `make docs`)

### Features

- Task ID format auto-detection from git branch names
- Repository-specific configuration overrides
- Git integration for task workflows
- Task archiving and deletion
- Status tracking (todo, in_progress, in_review, done, blocked, cancelled)
- Task templates for common patterns
- Artifact and test file organization per task
- Color terminal output with Rich formatting
- Environment variable overrides (`KNL_*` prefix)

### Documentation

- Installation guide with troubleshooting
- Quick start tutorial with common workflows
- Configuration reference with examples
- Task management deep dive
- Architecture principles and design philosophy
- CLI reference documentation
- Development setup guide
- Roadmap for future phases

### Technical Details

- **Language**: Python 3.14+
- **Package Manager**: UV
- **CLI Framework**: Typer + Rich
- **Configuration**: Pydantic Settings + TOML
- **Documentation**: MkDocs with Material theme
- **Testing**: pytest + hypothesis
- **Code Quality**: ruff + mypy
- **License**: MIT

### Infrastructure

- GitHub Actions workflow for documentation deployment
- GitHub Pages integration
- Version management via git tags
- Automatic installer updates on release

### Project Principles

Documented in PRINCIPLES.md:
- Knowledge retention and learning
- AI-powered development assistance
- Task-centric organization
- Context separation and isolation
- Minimal repository impact
- Language-aware templates
- Python version pinning
- User control and approval

### Known Limitations

- AI integration (Claude) not yet implemented
- Test generation features planned for Phase 3
- Git workflow automation planned for Phase 5
- Knowledge export/import planned for Phase 6
- Interactive TUI planned for Phase 7

## [Unreleased]

### Planned Features

#### Phase 2: AI Integration
- MCP server for Claude Code
- Code quality analysis
- Pattern recognition
- Smart suggestions

#### Phase 3: Test Automation
- Test generation from context
- Test templates from history
- Coverage tracking
- Quality metrics

#### Phase 4: Documentation
- Automated documentation updates
- Consistency checking
- Cross-referencing
- mkdocs integration

#### Phase 5: Git Workflow
- Commit message generation
- PR summary creation
- Branch naming suggestions
- Changelog automation

#### Phase 6: Knowledge Transfer
- Export/import knowledge bases
- Best practice summarization
- Cross-project learning
- Template sharing

#### Phase 7: Advanced Features
- Interactive TUI (Textual)
- Real-time collaboration
- Analytics and insights
- Custom plugins

---

[1.3.0]: https://github.com/akaliazin/knl/releases/tag/v1.3.0
[1.2.0]: https://github.com/akaliazin/knl/releases/tag/v1.2.0
[1.1.0]: https://github.com/akaliazin/knl/releases/tag/v1.1.0
[1.0.0]: https://github.com/akaliazin/knl/releases/tag/v1.0.0
