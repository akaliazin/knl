# KNL Project Principles & Concept

## Vision

KNL (Knowledge Retention Library) is a command-line tool that helps developers retain and leverage development knowledge across tasks. It acts as a persistent memory layer for development work, learning from each task to improve code quality, testing, and documentation.

## Core Principles

### 1. Knowledge Retention & Learning
- **Persistent Context**: Every task's context, decisions, and outcomes are stored locally
- **Learning from History**: Use knowledge from previous tasks to inform current work
- **Pattern Recognition**: Identify and apply successful patterns across tasks
- **Knowledge Transfer**: Export learned best practices to other projects

### 2. AI-Powered Development Assistant
- **Code Quality Analysis**: Leverage Claude/AI for intelligent code review
- **Test Generation**: Create tests based on learned patterns from previous tasks
- **Documentation Consistency**: Maintain coherent documentation across tasks
- **Git Workflow Assistance**: Generate meaningful commit messages and PR summaries

### 3. Task-Centric Organization
- **JIRA & GitHub Integration**: Support both JIRA tickets and GitHub issues
- **Task Isolation**: Each task has its own directory with context, tests, and artifacts
- **Status Tracking**: Monitor task lifecycle (todo → in_progress → in_review → done)
- **Flexible Management**: Create, list, show, update, delete, and archive tasks

## Technical Architecture

### Core Technology Stack
- **Language**: Python 3.14+ (for KNL itself; installer works with 3.8+)
- **Package Management**: UV for fast, reliable dependency management
- **CLI Framework**: Typer (modern, type-safe CLI with automatic help)
- **Terminal UI**: Rich for beautiful, informative output
- **Configuration**: Pydantic Settings with TOML files
- **AI Integration**: Claude via MCP (Model Context Protocol)

### Installation Architecture

KNL supports two installation modes:

#### 1. Repo-Local Installation (Default)
```
<repo_root>/.knl/           # KNL installation (when in git repo)
  ├── venv/                 # KNL's isolated Python environment
  ├── lib/                  # KNL's Python packages
  ├── bin/knl               # KNL executable
  └── .version              # Installed KNL version
```

#### 2. User-Local Installation
```
$HOME/.local/knl/           # KNL installation (system-wide)
  ├── venv/                 # KNL's isolated Python environment
  ├── lib/                  # KNL's Python packages
  ├── bin/knl               # KNL executable
  └── .version              # Installed KNL version
```

**Installation Decision Logic:**
- `install.sh` detects if running in a git repository (checks for `.git/`)
- **Default**: Repo-local installation if `.git/` exists
- **Override**: User can choose user-local with `--user-local` flag
- **Benefit**: Repo-local keeps KNL isolated per project; user-local shares across projects

### Context Separation

KNL maintains strict isolation between its own execution context and the target repository:

```bash
# KNL's Context
KNL_CONTEXT_DIR=<repo>/.knl  (or $HOME/.local/knl)
  - KNL's virtual environment
  - KNL's Python packages
  - KNL's configuration
  - Completely isolated from target repo

# Target's Context
TARGET_CONTEXT_DIR=<repo>
  - User's repository code
  - User's virtual environment (if any)
  - User's dependencies
  - Completely isolated from KNL
```

**Environment Isolation:**
- No `PYTHONPATH`, `PATH`, or other env vars leak between contexts
- KNL runs in its own venv; target code runs in its own (or system) Python
- KNL can work on projects with incompatible Python versions
- Target project is never polluted with KNL's dependencies

### Python Version Pinning

To ensure development stability and reproducibility, KNL pins Python versions for both contexts:

**KNL Context Python Pinning:**
```
<repo>/.knl/.python-version        # Pins KNL's Python version
or
$HOME/.local/knl/.python-version   # Pins KNL's Python version (user-local)
```

When KNL is installed, the installer:
1. Discovers or uses the explicitly specified Python version for KNL (e.g., 3.14.2)
2. Creates a `.python-version` file in the KNL installation directory
3. This ensures consistent Python version across reinstalls and updates
4. Tools like pyenv automatically respect this file

**Target Repository Python Pinning:**
```
<repo>/.python-version              # Pins target repo's Python version
```

When KNL is initialized in a target repository (`knl init`):
1. Checks if `.python-version` exists in the target repo
2. If present: Respects and uses that version for target-specific operations
3. If absent and target is Python-based: Suggests creating one based on detected version
4. Stores the version to ensure reproducible builds and consistent behavior

**Benefits:**
- **Stability**: Same Python version used across different machines and installations
- **Reproducibility**: Other developers get the same Python version
- **Tool Integration**: Works with pyenv, asdf, and other version managers
- **Clear Documentation**: Explicit declaration of Python requirements

**Example Workflow:**
```bash
# KNL installation creates:
.knl/.python-version          # Contains: 3.14.2

# Target repo initialization checks/creates:
.python-version               # Contains: 3.11.5 (or whatever target uses)

# Both files are independent and serve different purposes
```

### Configuration & Data Storage

```
# Configuration (follows XDG spec)
$XDG_CACHE_HOME/knl/        # or $HOME/.cache/knl
  ├── config.toml           # Global KNL configuration
  ├── cache/                # Temporary cache data
  └── templates/            # Default templates

# Repository-local knowledge base
<repo>/.knowledge/          # Knowledge retention (git-ignored by default)
  ├── config.toml           # Local settings (override global)
  ├── cache/                # Local cache
  ├── tasks/                # Task storage
  │   └── TASK-ID/
  │       ├── metadata.json # Task metadata
  │       ├── context.md    # Development context
  │       ├── tests/        # Task-specific tests
  │       └── artifacts/    # Generated artifacts
  ├── templates/            # Repo-specific templates
  ├── standards/            # Development standards
  └── scripts/              # Helper scripts
```

### Minimal Repository Impact

KNL is designed to be non-invasive:

**Only additions to repository:**
1. `.knl/` directory (if repo-local install; git-ignored)
   - Contains KNL installation and `.python-version` for KNL's Python
2. `.knowledge/` directory (git-ignored by default; optionally versionable)
   - Contains task data, templates, and standards
3. `.python-version` file in repo root (if not present and needed)
   - Pins target repository's Python version for stability
   - Only suggested for Python-based projects
4. `.gitignore` amendments (only to exclude `.knl/` and `.knowledge/`)

**No other modifications:**
- ❌ No files added to project root (except `.python-version` if suggested/approved)
- ❌ No changes to existing configuration files
- ❌ No modifications to package.json, requirements.txt, etc.
- ❌ No global environment pollution

**All KNL artifacts contained within:**
- `.knl/` - KNL installation and tooling
- `.knowledge/` - Development knowledge and task data
- `$XDG_CACHE_HOME/knl/` - Global configuration and cache

### CLAUDE.md Management

When KNL is initialized in a target repository (`knl init`), it provides intelligent CLAUDE.md guidance:

#### Language Detection

KNL automatically detects the primary development language/environment of the target repository:

**Detection Strategy:**
1. Analyze repository files and structure
2. Identify language-specific files:
   - Python: `requirements.txt`, `pyproject.toml`, `setup.py`, `.py` files
   - Java/Groovy: `build.gradle`, `pom.xml`, `settings.gradle`, `.java`/`.groovy` files
   - Node.js: `package.json`, `package-lock.json`, `.js`/`.ts` files
   - Go: `go.mod`, `go.sum`, `.go` files
   - Rust: `Cargo.toml`, `Cargo.lock`, `.rs` files
   - Ruby: `Gemfile`, `Gemfile.lock`, `.rb` files
3. Determine primary language based on file count and importance
4. Support polyglot repositories (multiple languages)

#### CLAUDE.md Initialization Flow

**When CLAUDE.md exists:**
1. **Read existing CLAUDE.md**: Parse and analyze current content
2. **Compare with KNL best practices**: Identify gaps and improvements
3. **Generate merge proposal**: Show what KNL would add/improve
4. **Present diff to user**: Clear explanation of each change
5. **Ask for approval**: User can accept, reject, or modify the proposal

**Example Merge Proposal:**
```markdown
KNL detected existing CLAUDE.md. Suggested improvements:

[+] Add section: Task Management
    - Explains knl commands (create, list, show)
    - Documents task ID formats (JIRA/GitHub)

[+] Add section: Knowledge Base Structure
    - Documents .knowledge/ directory
    - Explains task context and standards

[~] Enhance section: Development Workflow
    - Add integration with knl task tracking
    - Add AI-assisted commit messages

Accept changes? [Y/n/edit]
```

**When CLAUDE.md does not exist:**
1. **Detect primary language**: Analyze repository structure
2. **Generate language-specific template**: Tailor content to detected language
3. **Include KNL best practices**: Task management, knowledge retention patterns
4. **Suggest creation**: Ask user if they want to create CLAUDE.md

**Example for Groovy/Gradle Project:**
```markdown
# CLAUDE.md (Generated for Groovy/Gradle Project)

This file provides guidance to Claude Code when working with this repository.

## Project Overview

[KNL will prompt user to fill this in]

## Technology Stack

- **Language**: Groovy
- **Build Tool**: Gradle
- **JDK Version**: [detected from gradle.properties or build.gradle]

## Development Setup

```bash
# Build project
./gradlew build

# Run tests
./gradlew test

# [Additional project-specific commands]
```

## Task Management with KNL

This project uses KNL for task tracking and knowledge retention.

### Common Commands

```bash
# Create a new task
knl create PROJ-123

# List all tasks
knl list

# Show task details
knl show PROJ-123
```

### Task Workflow

1. Create task: `knl create TASK-ID`
2. Update context as you work
3. Write tests in `.knowledge/tasks/TASK-ID/tests/`
4. Update task status: `knl task update TASK-ID --status in_progress`

## Code Standards

[KNL will include repo-specific standards from .knowledge/standards/]

## Testing

- Unit tests: `./gradlew test`
- Integration tests: `./gradlew integrationTest`
- Coverage: `./gradlew jacocoTestReport`

## Common Gotchas

[KNL learns from task history and can populate this section]
```

#### Language-Specific Template Features

**Python Projects:**
- Virtual environment setup
- pip/poetry/uv dependency management
- pytest/unittest patterns
- Type hints and mypy
- Black/ruff formatting

**Java/Groovy Projects:**
- Gradle/Maven build commands
- JUnit test patterns
- Code style (Checkstyle/SpotBugs)
- Dependency management
- Spring Boot specifics (if detected)

**Node.js Projects:**
- npm/yarn/pnpm commands
- Jest/Mocha test patterns
- ESLint/Prettier configuration
- Package scripts
- TypeScript specifics (if detected)

**Go Projects:**
- Go modules
- Testing with `go test`
- Linting with golangci-lint
- Build and run commands

**Rust Projects:**
- Cargo commands
- Testing with `cargo test`
- Clippy linting
- Documentation with rustdoc

#### Best Practices Included

KNL's CLAUDE.md templates always include:

1. **Clear Project Overview**: What the project does
2. **Development Setup**: How to get started
3. **Architecture Notes**: Key design decisions
4. **Testing Strategy**: How to run and write tests
5. **Code Standards**: Style guides and conventions
6. **Common Commands**: Frequently used CLI commands
7. **Task Management**: Integration with KNL
8. **Debugging Tips**: Common issues and solutions
9. **CI/CD Notes**: Build and deployment process

#### User Control

- **Non-invasive**: KNL never modifies CLAUDE.md without approval
- **Incremental updates**: Suggest improvements as project evolves
- **Respect existing content**: Merge, don't replace
- **Learn from history**: Use task outcomes to improve documentation

### Installation Script Architecture

The `install.sh` script is designed for maximum portability and maintainability:

**Requirements:**
- Only requires **Python 3.8+** (any system Python)
- No external Python packages needed
- Uses only Python standard library for portability

**Implementation Strategy:**
```bash
#!/usr/bin/env bash
# Minimal bash wrapper

# Embed Python installer using heredoc
python3 << 'PYTHON_INSTALLER'
#!/usr/bin/env python3
# Pure Python installer using only stdlib
import sys
import os
import subprocess
# ... full installer logic in Python
PYTHON_INSTALLER
```

**Benefits:**
- **Maintainable**: Python is easier to maintain than complex bash
- **Portable**: Works on any system with Python 3.8+
- **Testable**: Python code can be unit tested
- **Powerful**: Access to full Python stdlib (json, urllib, tarfile, etc.)
- **Simple bash wrapper**: Just invokes the embedded Python script

**Version Management:**
```bash
# Install latest version (default)
curl -sSL https://raw.githubusercontent.com/akaliazin/knl/main/install.sh | sh

# Install specific version
curl -sSL https://raw.githubusercontent.com/akaliazin/knl/main/install.sh | sh -s -- --version 0.2.0

# Install from specific branch/tag
curl -sSL https://raw.githubusercontent.com/akaliazin/knl/main/install.sh | sh -s -- --ref develop

# Show installed version
knl --version

# Note: Upgrade command planned for future release
```

**Repository:**
- Source: https://github.com/akaliazin/knl
- Releases: Tagged versions following semver
- Installer: Always uses latest from `main` branch unless `--ref` specified

## Design Philosophy

### User Experience
1. **Bootstrap Installation**: One-line installer like UV (`curl | sh`)
2. **Zero Sudo Required**: All installation to user's home or repo directory
3. **Smart Defaults**: Repo-local install if in git repo; user-local otherwise
4. **Intelligent Fallbacks**: Minimal configuration needed
5. **Helpful Error Messages**: Guide users to solutions, not just problems
6. **Consistent Interface**: Follow patterns from established tools (DVC, Git)
7. **Version Control**: Easy to install, upgrade, and pin specific versions

### Command Design
- **Standard Commands**: `init`, `create`, `list`, `show`, `update`, `delete`
- **Intuitive Help**: `command --help` and `help command` both work
- **Short & Long Flags**: Support both `-h` and `--help`
- **Smart Autocomplete**: Shell completion for commands and task IDs
- **Contextual Guidance**: Show relevant help based on context

### Configuration Management
- **Hierarchical Settings**: Defaults → Global → Local → CLI flags
- **TOML Format**: Human-readable, well-supported configuration files
- **Type-Safe**: Pydantic models ensure valid configuration
- **Environment Override**: Support `KNL_*` environment variables

### Data Storage
- **Git-Ignored by Default**: `.knowledge/` not committed (user can opt-in)
- **Portable**: Plain text files (markdown, JSON, TOML)
- **Versionable**: Templates and standards can be committed
- **Cacheable**: Separate cache directory for transient data

## Future Capabilities (Roadmap)

### Phase 1: Foundation (In Progress)
- ✅ Core CLI and commands
- ✅ Task management (JIRA/GitHub)
- ✅ Configuration system
- ✅ Local knowledge base
- ✅ Dual installation modes (repo-local/user-local)
- 🚧 Python version pinning for stability
- 🚧 CLAUDE.md intelligent management
- 🚧 Language detection and templates

### Phase 2: AI Integration
- MCP server for Claude Code
- Code quality analysis
- Pattern recognition
- Smart suggestions

### Phase 3: Test Automation
- Test generation from context
- Test templates from history
- Coverage tracking
- Quality metrics

### Phase 4: Documentation
- Automated documentation updates
- Consistency checking
- Cross-referencing
- mkdocs integration

### Phase 5: Git Workflow
- Commit message generation
- PR summary creation
- Branch naming suggestions
- Changelog automation

### Phase 6: Knowledge Transfer
- Export/import knowledge bases
- Best practice summarization
- Cross-project learning
- Template sharing

### Phase 7: Advanced Features
- Interactive TUI (Textual)
- Real-time collaboration
- Analytics and insights
- Custom plugins

## Non-Goals

- **Not a Project Manager**: Complements JIRA/GitHub, doesn't replace them
- **Not a Code Editor**: Integrates with your editor, doesn't replace it
- **Not Cloud-First**: Local-first, with optional cloud sync
- **Not Opinionated**: Adapts to your workflow, doesn't impose one

## Key Differentiators

1. **Knowledge Retention**: Unlike task trackers, KNL remembers and learns
2. **AI-Native**: Built from the ground up with AI assistance in mind
3. **Local-First**: Your data stays on your machine
4. **Developer-Focused**: Built by developers, for developers
5. **Extensible**: Easy to add custom scripts, templates, and workflows

## Success Criteria

A successful KNL implementation should:
- ✅ Reduce cognitive load when switching between tasks
- ✅ Improve code quality through learned patterns
- ✅ Accelerate testing with generated test cases
- ✅ Maintain consistent documentation automatically
- ✅ Transfer knowledge efficiently across projects
- ✅ Integrate seamlessly into existing workflows

---

*This document defines the core principles and vision for KNL. It should be updated as the project evolves and new insights emerge.*
